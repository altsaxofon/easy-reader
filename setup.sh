#!/bin/bash
echo "---"
echo "EasyReader Setup Script"
echo "---"

# Get the current user dynamically
USER=$(whoami)

# Get the directory of the setup script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Update and install dependencies (only the ones that are necessary)
echo "---"
echo "Updating system and installing dependencies..."
echo "---"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv espeak-ng mpg123
sudo usermod -aG audio $USER  # 

echo "---"
echo "Setting up virtual environment"
echo "---"

# Create virtual environment inside the script directory (only if it doesn't already exist)
VENV_DIR="$SCRIPT_DIR/easyreader_ve"
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up Python virtual environment in the script directory..."
    python3 -m venv --system-site-packages "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
    deactivate
else
    echo "Virtual environment already exists. Skipping creation."
fi

# Add the current user to the audio group (only if not already a member)
echo "---"
echo "Ensuring the user has audio permissions..."
echo "---"

if ! groups $USER | grep -q '\baudio\b'; then
    sudo usermod -aG audio $USER
else
    echo "$USER is already in the audio group."
fi

# Create systemd service file
echo "---"
echo "Creating systemd service..."
echo "---"
SERVICE_FILE="/etc/systemd/system/easy_reader.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=EasyReader Python Script
After=sound.target
Wants=sound.target

[Service]
# Mount the auduiobook partition 
ExecStartPre=/bin/mkdir -p /mnt/sdcard
ExecStartPre=/bin/bash -c 'mountpoint -q /mnt/sdcard || /bin/mount -o uid=1000,gid=1000,umask=0022,iocharset=utf8 /dev/mmcblk0p3 /mnt/sdcard'

# Set the speaker volume to 90% (100% will cause distortion i think)
ExecStartPre=/usr/bin/amixer sset 'Speaker' 90%

# Start the python script
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/main.py

WorkingDirectory=$SCRIPT_DIR
Restart=always

#Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:0"
Environment="PYTHONUNBUFFERED=1"
#Environment="DEBUG=1"

Environment="SDL_AUDIODRIVER=alsa"
# Environment="AUDIODEV=hw:0,0" 
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to apply changes
echo "---"
echo "Reloading systemd and enabling service..."
echo "---"

sudo systemctl daemon-reload
sudo systemctl enable easy_reader.service

# Start the service
echo "Starting EasyReader service..."
echo "---"
sudo systemctl start easy_reader.service

# Check if the service is running
echo "Checking service status..."
echo "---"
sudo systemctl status easy_reader.service
echo "---"
echo "Setup complete. EasyReader should now run automatically on boot."