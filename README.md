# Synology DSM automated certificate update

Everything is Work In Progress, the current code doesn't do exactly what you probably want. The installation guide isn't completed. Stay tune!

Uses Synology API with the help of [N4S4/synology-api](https://github.com/N4S4/synology-api)

Currently the scripts uses certificate located in a Docker swag instance running on the same Synology server. Planning to 

# Installation

## 1. Connect to your Synology NAS and become root
```
ssh youradmin_user@your_nas_hostname_or_ipaddress
sudo su -
```

## 2. Install synology-api and synology-api-cert-update

Pick either first or second option.

### 2.1 Install or update via shell script

The following curl command downloads a shell script and runs it. The script installs or updates N4S4/synology-api and baylanger/synology-api-cert-update

```
curl -s https://https://raw.githubusercontent.com/baylanger/synology-api-cert-update/refs/heads/main/install.sh | bash
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

## 3. Add cron to your NAS

Using your Synology UI add a schedule tasks to run this script at least once a day.
