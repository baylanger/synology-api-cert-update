set -e

SYNO_API_ZIP=synology-api.zip
SYNO_API_MASTER=synology-api-master
SYNO_API_CERT_UPDATE_ZIP=synology-api-cert-update.zip
SYNO_API_CERT_UPDATE_MAIN=synology-api-cert-update-MAIN

NOCOLOR='\033[0m'
GREEN='\033[0;32m'
RED='\033[0;31m'

# Delete previous synology-api
[ -f $SYNO_API_ZIP ] && /usr/bin/rm -f $SYNO_API_ZIP
[ -d $SYNO_API_MASTER ] && /usr/bin/rm -rf $SYNO_API_MASTER

# Download synology-api
echo -e "$GREEN Downloading https://github.com/N4S4/synology-api/archive/refs/heads/master.zip $NOCOLOR"
wget -q https://github.com/N4S4/synology-api/archive/refs/heads/master.zip -O $SYNO_API_ZIP

# Install synology-api (unzip, delete zip file, install)
echo -e "$GREEN Running 7z to extract $SYNO_API_ZIP $NOCOLOR"
7z x -bso0 $SYNO_API_ZIP
# Install synology-api, you might see warnings but the install should complete
cd synology-api-master
echo -e "$GREEN Running python3 setup.py install --force $NOCOLOR"
python3 setup.py install --force
cd ..
/usr/bin/rm $SYNO_API_ZIP

# Delete previous synology-api-cert-update
[ -f $SYNO_API_CERT_UPDATE_ZIP ] && /usr/bin/rm -f $SYNO_API_CERT_UPDATE_ZIP
[ -d $SYNO_API_CERT_UPDATE_MAIN ] && /usr/bin/rm -rf $SYNO_API_CERT_UPDATE_MAIN

# Download synology-api-cert-update
echo -e "$GREEN Downloading https://github.com/baylanger/synology-api-cert-update/archive/refs/heads/master.zip $NOCOLOR"
wget -q https://github.com/baylanger/synology-api-cert-update/archive/refs/heads/master.zip -O $SYNO_API_CERT_UPDATE_ZIP

# Install synology-api-cert-update (unzip, delete zip file, install)
echo -e "$GREEN Running 7z to extract $SYNO_API_CERT_UPDATE_ZIP $NOCOLOR"
7z -bso0 x $SYNO_API_CERT_UPDATE_ZIP
/usr/bin/rm $SYNO_API_CERT_UPDATE_ZIP
