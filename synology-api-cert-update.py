#!/usr/bin/python3
#
#
#  WORK IN PROGRESS
#  ----------------
#
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
import json
import sys
from datetime import datetime, timedelta
from synology_api import core_certificate

# Define docker swag letsencrypt live root dir
docker_swag_le_live = "/volume1/docker/swag/etc/letsencrypt/live"

# Set your certificate name, if no wildcard_domain use => wildcard_domain = ''
primary_domain = 'yourdomain.com'
wildcard_domain = f'*.{primary_domain}'

# Set the number of days remaining for current cert to upload the new cert
days_to_expiration = 7

# How to connect to your Synology server, hostname or IP address
hostname = 'nas.yourdomain.com'
port = '5001'
username = 'admin'
password = ''
secure = True
cert_verify = False
dsm_version = 7
debug = True

# Set new certificate as default or not
set_certificate_as_default = True

###################################################################################
###################################################################################

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
    debug
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
syn.delete_certificate(current_certificate_id)

# Get latest certificates list
certificate_list = syn.list_cert()

# Get new certificate id
new_certificate_id = certificate_list["data"]["certificates"][0]["id"]
print("New certificate ID:" + new_certificate_id)
