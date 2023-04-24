#!/bin/bash

USER="pi"
PI_ADDR="100.84.226.80"
# PI_ADDR="192.168.0.100"
LOCAL_DIR="./printer_data"
REMOTE_DIR="/home/$USER/"

echo "Syncing to $PI_ADDR..."

# scp -r $LOCAL_DIR $USER@$PI_ADDR:$REMOTE_DIR
rsync -av -e ssh --exclude-from='exclude-file.txt' $LOCAL_DIR $USER@$PI_ADDR:$REMOTE_DIR

curl -X POST http://$PI_ADDR/printer/firmware_restart