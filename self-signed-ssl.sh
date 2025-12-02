#!/bin/bash

# Create self-signed SSL certificate for IP-based access
# Use this if you don't have a domain name

# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Generate self-signed certificate (valid for 1 year)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/whisper.key \
    -out /etc/nginx/ssl/whisper.crt \
    -subj "/C=US/ST=State/L=City/O=Whisper Demo/CN=$(curl -s ifconfig.me)"

# Update nginx configuration for self-signed cert
sudo tee /etc/nginx/sites-available/whisper-ssl << 'EOF'
server {
    listen 8080;
    server_name _;

    # Redirect HTTP to HTTPS
    return 301 https://$host:8443$request_uri;
}

server {
    listen 8443 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/whisper.crt;
    ssl_certificate_key /etc/nginx/ssl/whisper.key;

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

        client_max_body_size 50M;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        proxy_read_timeout 300s;
    }
}
EOF

# Enable the SSL configuration
sudo ln -sf /etc/nginx/sites-available/whisper-ssl /etc/nginx/sites-enabled/whisper
sudo nginx -t
sudo systemctl reload nginx

echo "Self-signed SSL certificate created!"
echo "Access your site at: https://YOUR_IP:8443"
echo "Note: Browser will show security warning - click 'Advanced' and proceed"