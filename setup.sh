#!/bin/bash

# Update and install dependencies
echo "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv espeak-ng

# Create virtual environment (optional)
echo "Setting up Python virtual environment..."
python3 -m venv /home/admin/easyreader_ve
source /home/admin/easyreader_ve/bin/activate
pip install -r /home/admin/easyreader/requirements.txt
deactivate

# Add the pi user to the audio group
echo "Ensuring the user has audio permissions..."
sudo usermod -aG audio pi

# Create systemd service file
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/easyreader.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=EasyReader Python Script
After=sound.target
Wants=sound.target

[Service]
ExecStart=/home/admin/easyreader_ve/bin/python /home/admin/easyreader/main.py
WorkingDirectory=/home/admin/easyreader
Restart=always
User=pi
Group=pi
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:0"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd to apply changes
echo "Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable easyreader.service

# Start the service
echo "Starting EasyReader service..."
sudo systemctl start easyreader.service

# Check if the service is running
echo "Checking service status..."
sudo systemctl status easyreader.service

echo "Setup complete. EasyReader should now run automatically on boot."