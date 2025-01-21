# Synology DSM automated certificate update

Uses Synology API with the help of [N4S4/synology-api](https://github.com/N4S4/synology-api)

Currently the scripts uses certificate located in a Docker swag instance running on the same Synology server. Planning to 

Work In Progress, the current code doesn't do exactly what you probably want. Stay tune!

# Installation

## Connect to your Synology NAS and become root
```
ssh youradmin_user@your_nas
sudo su -
```

## Install Synology-API from https://github.com/N4S4/synology-api/
```
- Download zip file
  wget https://github.com/N4S4/synology-api/archive/refs/heads/master.zip
- Unzip
  7z x master.zip
- Install synology-api
  cd synology-api-master
  python3 setup.py install --force
```

## Install this project
```
... WIP ...
```
