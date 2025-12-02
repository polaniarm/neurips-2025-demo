#!/bin/bash

# Nginx and Let's Encrypt setup script for Ubuntu/Debian
# Run this on your AWS EC2 instance

# Update system
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# Create nginx configuration for Whisper service
sudo tee /etc/nginx/sites-available/whisper << 'EOF'
server {
    listen 8080;
    listen 8443 ssl;
    server_name YOUR_DOMAIN.com;  # Replace with your domain or use server IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed later)
        proxy_read_timeout 86400;

        # Increase buffer sizes for large audio files
        client_max_body_size 50M;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/whisper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "Nginx configured!"
echo ""
echo "Next steps:"
echo "1. Update YOUR_DOMAIN.com in /etc/nginx/sites-available/whisper"
echo "2. Point your domain to this server's IP"
echo "3. Run: sudo certbot --nginx -d YOUR_DOMAIN.com"
echo "4. Start your FastAPI server: uvicorn server:app --host 127.0.0.1 --port 8080"