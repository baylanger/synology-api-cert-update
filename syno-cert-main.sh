#DRY_RUN="echo DRY_RUN"

SCRIPT_DIR=$(dirname $0)

# Docker root install dir
DOCKER_VOLUME_ROOT=/volume1/docker

# Swag etc/letsencrypt root dir
SWAG_ETC_LE_ROOT=$DOCKER_VOLUME_ROOT/swag/etc/letsencrypt

# Define your base domain name
DOMAIN=yourdomain.com

SWAG_LE_LIVE_CERTS_DIR=$SWAG_ETC_LE_ROOT/live/$DOMAIN
SWAG_LE_LIVE_PRIVKEY_PEM_FILE=$SWAG_LE_LIVE_CERTS_DIR/privkey.pem
UPLOAD_CERT_TIME=$SWAG_LE_LIVE_CERTS_DIR/.upload-cert-time

[ ! -d $SWAG_LE_LIVE_CERTS_DIR ] && \
  echo "ERROR $SWAG_LE_LIVE_CERTS_DIR no such directory" && \
  exit 5

[ ! -f $SWAG_LE_LIVE_PRIVKEY_PEM_FILE ] && \
  echo "ERROR $SWAG_LE_LIVE_PRIVKEY_PEM_FILE no such file" && \
  exit 10

echo "INFO running python3 $SCRIPT_DIR/update-syno-cert.py"
$DRY_RUN python3 $SCRIPT_DIR/update-syno-cert.py

SWAG_LE_LIVE_PRIVKEY_PEM_MD5=$(cat $SWAG_LE_LIVE_PRIVKEY_PEM_FILE | md5sum | sed -e 's/ .*//g')

# Update certificate in docker instance adguard
if [ -d $DOCKER_VOLUME_ROOT/adguard/config ]; then
  echo "INFO entering $DOCKER_VOLUME_ROOT/adguard/config"
  cd $DOCKER_VOLUME_ROOT/adguard/config
  if [ -f privkey.pem ]; then
    SYNO_PRIVKEY_PEM_MD5=$(cat privkey.pem | md5sum | sed -e 's/ .*//g')
    if [ $SWAG_LE_LIVE_PRIVKEY_PEM_MD5 != $SYNO_PRIVKEY_PEM_MD5 ]; then
      echo "INFO updating fullchain.pem w/ $SWAG_LE_LIVE_CERTS_DIR/fullchain.pem"
      cp -f $SWAG_LE_LIVE_CERTS_DIR/fullchain.pem config/.
      echo "INFO updating privkey.pem w/ $SWAG_LE_LIVE_CERTS_DIR/fullchain.pem"
      cp -f $SWAG_LE_LIVE_CERTS_DIR/privkey.pem config/.
      docker restart adguard
    else
      echo "INFO skipping $DOCKER_VOLUME_ROOT/adguard/config has latest cert files"
    fi
  else
    echo "WARN privkey.pem is missing, skipping $DOCKER_VOLUME_ROOT/adguard/config"
    echo "cd -"
    cd - > /dev/null
  fi
else
  echo "WARN directory $DOCKER_VOLUME_ROOT/adguard/config is missing"
fi

exit $EXIT_CODE
