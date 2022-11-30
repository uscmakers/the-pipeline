#!/bin/bash

USER="pi"
PI_ADDR="100.69.87.103"
LOCAL_DIR="./klipper_config"
REMOTE_DIR="/home/pi/"

echo "Syncing to $PI_ADDR..."

# scp -r $LOCAL_DIR $USER@$PI_ADDR:$REMOTE_DIR
rsync -av -e ssh --exclude-from='exclude-file.txt' $LOCAL_DIR $USER@$PI_ADDR:$REMOTE_DIR

curl -X POST http://100.69.87.103/printer/firmware_restart