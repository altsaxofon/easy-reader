#!/bin/bash

echo "EasyReader Setup Script"

# Get the current user dynamically
USER=$(whoami)

# Get the directory of the setup script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Update and install dependencies (only the ones that are necessary)

# Create virtual environment inside the script directory (only if it doesn't already exist)
VENV_DIR="$SCRIPT_DIR/easyreader_ve"


# Create systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/easy_reader.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=EasyReader Python Script
After=sound.target
Wants=sound.target

[Service]
ExecStartPre=/bin/mkdir -p /mnt/sdcard
ExecStartPre=/bin/bash -c 'mountpoint -q /mnt/sdcard || /bin/mount -o uid=1000,gid=1000,umask=0022,iocharset=utf8 /dev/mmcblk0p3 /mnt/sdcard'
ExecStartPre=/usr/bin/amixer sset 'Speaker' 90%
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/main.py
WorkingDirectory=$SCRIPT_DIR
Restart=always

Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:0"
Environment="SDL_AUDIODRIVER=alsa"
# Environment="AUDIODEV=hw:0,0" 
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to apply changes
echo "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable easy_reader.service

# Start the service
echo "Starting EasyReader service..."
sudo systemctl start easy_reader.service

# Check if the service is running
echo "Checking service status..."
sudo systemctl status easy_reader.service

echo "Setup complete. EasyReader should now run automatically on boot."