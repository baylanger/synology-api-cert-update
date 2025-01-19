#!/usr/bin/python3
#
#
#  WORK IN PROGRESS
#  ----------------
#
#  TODO
#  ----
#  . Allow first time certificate upload, i.e. don't delete old cert since there was none!
#  . Allow via config to cleanup (delete) any expired certs
#  . Allow via config to cleanup (delete) any certs not assigned to any service
#
# Requires https://github.com/N4S4/synology-api/
#   Download zip file
#     wget https://github.com/N4S4/synology-api/archive/refs/heads/master.zip
#   Unzip
#     7z x master.zip
#   Install synology-api
#     cd synology-api-master
#     python3 setup.py install --force
#
import configparser
import json
import sys
from datetime import datetime, timedelta
from synology_api import core_certificate

# Path to configuration file
config_ini_file = 'syno-cert-update.ini'

# Load INI configuration
config_settings = configparser.ConfigParser()
config_settings.read(config_ini_file)

# Accessing configuration values from [connect] section
connect_section = config_settings['connect']
hostname = connect_section.get('hostname')
port = connect_section.get('port', '5001')
username = connect_section.get('username', 'default_user')
password = connect_section.get('password', 'default_password')
secure = connect_section.getboolean('secure', True)
cert_verify = connect_section.getboolean('cert_verify', False)
dsm_version = connect_section.getint('dsm_version', 7)
connect_debug = connect_section.getboolean('debug', False)
if connect_debug:
    print("connect =>", dict(connect_section), "\n")

# Accessing configuration values from [certificate] section
certificate_section = config_settings['certificate']
primary_domain = certificate_section.get('primary_domain')
have_wildcard_domain = certificate_section.getboolean('have_wildcard_domain', True)
days_to_expiration = certificate_section.getint('days_to_expiration', 1)
set_certificate_as_default = certificate_section.getboolean('set_certificate_as_default', True)
certificate_debug = certificate_section.get('debug', False)
if certificate_debug:
    print("certificate =>", dict(certificate_section), "\n")

# Accessing configuration values from [docker] section
docker_section = config_settings['docker']
docker_swag_le_live = docker_section.get('docker_swag_le_live_dir')
docker_debug = docker_section.get('debug', False)
if docker_debug:
    print("docker =>", dict(docker_section), "\n")

# Set or don't set wildcard_domain var
if have_wildcard_domain:
    wildcard_domain = f'*.{primary_domain}'
else:
    wildcard_domain = ''

# Construct private key and certificates path using the base docker_swag_le_live
private_key_path = f"{docker_swag_le_live}/{primary_domain}/privkey.pem"
server_certificate_path = f"{docker_swag_le_live}/{primary_domain}/cert.crt"
ca_certificate_path = f"{docker_swag_le_live}/{primary_domain}/chain.crt"

# Current date
current_date = datetime.utcnow()
expiration_date = current_date + timedelta(days=days_to_expiration)

# Function to convert string date to datetime object
def parse_valid_till(date_str):
    return datetime.strptime(date_str, "%b %d %H:%M:%S %Y GMT")

# Create syn object to communicate with your server
syn = core_certificate.Certificate(
    hostname,
    port,
    username,
    password,
    secure,
    cert_verify,
    dsm_version,
    connect_debug
)

# Request current certificates list
certificate_list = syn.list_cert()
print(json.dumps(certificate_list, indent=4))

# Extract expired certificate IDs
expired_ids = [
    cert['id'] for cert in certificate_list['data']['certificates'] if parse_valid_till(cert['valid_till']) < current_date
]
# Print list of expired certificate IDs
print(f"Expired Certificate IDs: {expired_ids}")

# Extract certificates expiring before expiration_date and matching domain
expiring_soon_and_matching_domains = [
    cert['id'] for cert in certificate_list['data']['certificates']
    if current_date <= parse_valid_till(cert['valid_till']) <= expiration_date
    and any(domain in primary_domain or domain in wildcard_domain for domain in cert['subject']['sub_alt_name'])
]
# Print list of certificates expiring
print(f"Certificates expiring before {expiration_date} and matching domains: {expiring_soon_and_matching_domains}")

# Filter and get list where 'sub_alt_name' matches the primary or wildcard domain
# and 'services' is not empty
current_certificate_ids = [
    cert['id'] for cert in certificate_list['data']['certificates']
    if (primary_domain in cert['subject']['sub_alt_name'] or wildcard_domain in cert['subject']['sub_alt_name'])
    and cert['services']
]
print("Current certificate IDs" + str(current_certificate_ids))

# Extract certificates where is_broken is True
current_broken_certificates = [cert for cert in certificate_list['data']['certificates'] if cert['is_broken']]
print("Current broken certificates:" + str(current_broken_certificates))

# Filter and get list of 'id' where 'services' is empty
empty_service_ids = [cert['id'] for cert in certificate_list['data']['certificates'] if not cert['services']]
print("Certificate not assigned to any service:" + str(empty_service_ids))

# Filter and get list of 'id' where 'sub_alt_name' matches the primary or wildcard domain and 'services' is empty
ids_matching_domains_with_no_services = [
    cert['id'] for cert in certificate_list['data']['certificates']
    if (primary_domain in cert['subject']['sub_alt_name'] or wildcard_domain in cert['subject']['sub_alt_name'])
    and not cert['services']  # Check if services is empty
]
print("Certificate matching primary_domain or wildcard_domain but not assigned to any service:" + str(ids_matching_domains_with_no_services))

# Upload new certificate
syn.upload_cert(
    serv_key=private_key_path,
    ser_cert=server_certificate_path,
    ca_cert=ca_certificate_path,
    set_as_default=set_certificate_as_default
)

# Delete old certificate, we should probably delete any matching domain that isn't assigned
# to any services

# Delete current (now previous) certicate only if the uploaded cert is set as default
if set_certificate_as_default:
    syn.delete_certificate(current_certificate_id)

# Get latest certificates list
certificate_list = syn.list_cert()
# Get new certificate id
new_certificate_id = certificate_list["data"]["certificates"][0]["id"]
print("New certificate ID:" + new_certificate_id)
