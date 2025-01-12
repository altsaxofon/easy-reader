#!/bin/bash

echo "EasyReader Setup Script"

# Get the current user dynamically
USER=$(whoami)

# Get the directory of the setup script
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Update and install dependencies (only the ones that are necessary)
echo "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv espeak-ng
sudo usermod -aG audio $USER  # 

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
echo "Ensuring the user has audio permissions..."
if ! groups $USER | grep -q '\baudio\b'; then
    sudo usermod -aG audio $USER
else
    echo "$USER is already in the audio group."
fi

# Create systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/easy_reader.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=EasyReader Python Script
After=sound.target
Wants=sound.target

[Service]
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/main.py
WorkingDirectory=$SCRIPT_DIR
Restart=always
User=$USER
Group=$USER
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:0"
Environment="SDL_AUDIODRIVER=alsa"
# Replace 1,0 with the USB audio card numbers from `aplay -l`
# Environment="AUDIODEV=hw:1,0" 
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