#!/bin/bash

# Create systemd service for Whisper FastAPI app
# This keeps your app running in the background

sudo tee /etc/systemd/system/whisper.service << EOF
[Unit]
Description=Whisper Transcription Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/neurips-2025-demo
Environment="PATH=/home/ubuntu/neurips-2025-demo/venv/bin"
ExecStart=/home/ubuntu/neurips-2025-demo/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable whisper
sudo systemctl start whisper

echo "Service created!"
echo "Commands:"
echo "  sudo systemctl status whisper  - Check status"
echo "  sudo systemctl restart whisper - Restart service"
echo "  sudo journalctl -u whisper -f  - View logs"