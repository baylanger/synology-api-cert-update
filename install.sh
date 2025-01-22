set -e

SYNO_API_ZIP=synology-api.zip
SYNO_API_MASTER=synology-api-master
SYNO_API_CERT_UPDATE_ZIP=synology-api-cert-update.zip
SYNO_API_CERT_UPDATE_MAIN=synology-api-cert-update-main

NOCOLOR='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[33m'
RED='\033[0;31m'

# Compare the latest synology-api-cert-update-main/syno-cert-update.ini with the current one
# and output any changes the end user should manually update.
check_ini_changes() {

  echo
  echo -e "${GREEN}Comparing your syno-cert-update.ini with the latest one${NOCOLOR}"
  set -o pipefail +e
  DIFF_OUTPUT=$(diff -u <(grep -v ^# synology-api-cert-update/syno-cert-update.ini | \
    awk '{print $1, $0}') <(grep -v ^# synology-api-cert-update-main/syno-cert-update.ini | \
    awk '{print $1, $0}') | \
    cut -d ' ' -f 1,3-)

  if [ $? -eq 0 ]; then
    echo -e "${GREEN}No changes required in your syno-cert-update.ini${NOCOLOR}"
  else
	echo -e "${YELLOW}"
    echo "$DIFF_OUTPUT" > synology-api-cert-update/syno-cert-update.diff
    grep '^[+-]' synology-api-cert-update/syno-cert-update.diff | \
      cut -c2- | cut -d' ' -f1 | sort | uniq -u | \
      while read line; do grep "^[+-]$line" test.txt; done
	echo
    echo -e "${RED}ATTENTION adjust your syno-cert-update.ini based on the above output in ${YELLOW}yellow"
    echo -e "${RED} Line starting with - means the setting should be removed from your .ini file"
    echo -e " Line starting with + means the setting is new and should be added in your .ini file${NOCOLOR}"
  fi
  set +o pipefail -e
}

# Delete previous synology-api
[ -f $SYNO_API_ZIP ] && /usr/bin/rm -f $SYNO_API_ZIP
[ -d $SYNO_API_MASTER ] && /usr/bin/rm -rf $SYNO_API_MASTER

# Download synology-api
echo -e "${GREEN}Downloading https://github.com/N4S4/synology-api/archive/refs/heads/master.zip${NOCOLOR}"
wget -q https://github.com/N4S4/synology-api/archive/refs/heads/master.zip -O $SYNO_API_ZIP

# Install synology-api (unzip, delete zip file, install)
echo -e "${GREEN}Running 7z to extract $SYNO_API_ZIP${NOCOLOR}"
7z x -y -bso0 $SYNO_API_ZIP
# Install synology-api, you might see warnings but the install should complete
cd synology-api-master
echo -e "${GREEN}Running python3 setup.py install --force${NOCOLOR}"
python3 setup.py install --force
cd ..
/usr/bin/rm $SYNO_API_ZIP

# Delete previous synology-api-cert-update
[ -f $SYNO_API_CERT_UPDATE_ZIP ] && /usr/bin/rm -f $SYNO_API_CERT_UPDATE_ZIP
[ -d $SYNO_API_CERT_UPDATE_MAIN ] && /usr/bin/rm -rf $SYNO_API_CERT_UPDATE_MAIN

# Download synology-api-cert-update
echo -e "${GREEN}Downloading https://github.com/baylanger/synology-api-cert-update/archive/refs/heads/main.zip${NOCOLOR}"
wget -q https://github.com/baylanger/synology-api-cert-update/archive/refs/heads/main.zip -O $SYNO_API_CERT_UPDATE_ZIP

# Install synology-api-cert-update (unzip, delete zip file, install)
echo -e "${GREEN}Running 7z to extract $SYNO_API_CERT_UPDATE_ZIP${NOCOLOR}"
7z x -y -bso0 $SYNO_API_CERT_UPDATE_ZIP
/usr/bin/rm $SYNO_API_CERT_UPDATE_ZIP

# Rename directory synology-api-cert-update-main to synology-api-cert-update, 1st time install
# OR copy required files without overwriting the .ini file
if [ ! -d synology-api-cert-update ]; then
  mv $SYNO_API_CERT_UPDATE_MAIN synology-api-cert-update
else
  mv $SYNO_API_CERT_UPDATE_MAIN/{*.py,*.sh,LICENSE,README.md} synology-api-cert-update
fi

# Compare the latest downloaded .ini file with the current installed one
check_ini_changes
