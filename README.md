# Synology DSM automated certificate update

Uses Synology API with the help of [N4S4/synology-api](https://github.com/N4S4/synology-api)

Currently the scripts uses certificate located in a Docker swag instance running on the same Synology server. Planning to 

Work In Progress, the current code doesn't do exactly what you probably want. Stay tune!

# Installation

## Synology-API
```
- Requires https://github.com/N4S4/synology-api/
  - Download zip file
    wget https://github.com/N4S4/synology-api/archive/refs/heads/master.zip
  - Unzip
    7z x master.zip
  - Install synology-api
    cd synology-api-master
    python3 setup.py install --force
```
