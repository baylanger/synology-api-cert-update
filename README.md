# Synology DSM automated certificate update

Everything is Work In Progress, the current code doesn't do exactly what you probably want. The installation guide isn't completed. Stay tune!

Uses Synology API with the help of [N4S4/synology-api](https://github.com/N4S4/synology-api)

Currently the scripts uses certificate located in a Docker swag instance running on the same Synology server.

# Installation

## 1. Connect to your Synology NAS
```
ssh youradmin_user@your_nas_hostname_or_ipaddress
sudo su -
cd ~youradmin_user
```

WARNING : Make sure you cd into the directory of your admin user. If you don't the installation will likely run in /root and on a Synology update you will lose everything including your customized settings in the syno-cert-update.ini file.

## 2. Install synology-api and synology-api-cert-update

First option (2.1) is automated.

Second option (2.2) is manual.

### 2.1 Install or update via shell script (automatic)

The following `curl` command downloads the `install.sh` script from this repo and runs it. The script installs or updates N4S4/synology-api and baylanger/synology-api-cert-update.

It will not overwrite your configuration fine but if there are changes, it will show them and you need to manually make the changes.

```
curl -s -o- https://raw.githubusercontent.com/baylanger/synology-api-cert-update/refs/heads/main/install.sh | bash
```

### 2.2 Manual install or update

Synology-API : Download the zip file, unzip it and run the installation

```
# Download
wget https://github.com/N4S4/synology-api/archive/refs/heads/master.zip
# Unzip master.zip and delete the file
7z x master.zip && rm master.zip
# Install synology-api, you might see warnings but the install should complete
( cd synology-api-master && python3 setup.py install --force )
```

Install this project (synology-api-cert-update)
```
# Download
wget https://github.com/baylanger/synology-api-cert-update/archive/refs/heads/master.zip
# Unzip master.zip and delete the file
7z x master.zip && rm master.zip
```

## 3. Configuration

Edit the syno-cert-update.ini file and set the values appropriately.

At minimum you should make the following changes and make sure all of the remaining settings are valid for your setup:
- hostname
- username
- password
- primary_domain
- have_wildcard_domain - set to false if you don't have a wildcard certificate
- set_certificate_as_default - should stay true if you want the old certificate to be automatically replaced in your NAS' config.
- docker_swag_le_live_dir

## 4. Add a task scheduler for the script to automatically run

Using your Synology UI add a schedule tasks to run this script at least once a day.
