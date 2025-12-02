# Production Deployment with Nginx and Let's Encrypt

## Prerequisites
- Ubuntu/Debian server (AWS EC2)
- Domain name pointing to your server's IP (optional, can use IP)
- Ports 8080 and 8443 open in security group

## Step 1: Install Dependencies

```bash
# Update system
sudo apt update
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/neurips-2025-demo.git
cd neurips-2025-demo

# Create virtual environment and install Python packages
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn transformers torch python-multipart
```

## Step 2: Setup Systemd Service

Create a service to run the FastAPI app in the background:

```bash
sudo nano /etc/systemd/system/whisper.service
```

Add this content (adjust paths for your setup):

```ini
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
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable whisper
sudo systemctl start whisper
sudo systemctl status whisper
```

## Step 3: Configure Nginx

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/whisper
```

Add this (replace YOUR_DOMAIN.com with your actual domain):

```nginx
server {
    listen 8080;
    listen 8443 ssl;
    server_name YOUR_DOMAIN.com;  # Or use _ for any domain/IP

    # SSL certificates (will be added by certbot)
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;

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

        # Large file support
        client_max_body_size 50M;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        proxy_read_timeout 300s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/whisper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 4: Setup SSL with Let's Encrypt

```bash
# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d YOUR_DOMAIN.com

# Follow the prompts:
# - Enter email
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: yes)
```

Certbot will automatically:
- Get the certificate
- Configure nginx for HTTPS
- Set up auto-renewal

## Step 5: Verify Everything Works

1. Check services:
```bash
sudo systemctl status whisper
sudo systemctl status nginx
```

2. Check logs if needed:
```bash
sudo journalctl -u whisper -f
sudo tail -f /var/log/nginx/error.log
```

3. Access your site:
- HTTP: `http://YOUR_DOMAIN.com:8080`
- HTTPS: `https://YOUR_DOMAIN.com:8443`
- Microphone access now works because of HTTPS!

## Maintenance

### Update the application
```bash
cd ~/neurips-2025-demo
git pull
sudo systemctl restart whisper
```

### View logs
```bash
sudo journalctl -u whisper -f
```

### SSL certificate renewal (automatic)
Certbot sets up auto-renewal. Test it with:
```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### If microphone still doesn't work
- Ensure you're accessing via HTTPS
- Check browser console for errors
- Try a different browser

### If site doesn't load
1. Check nginx: `sudo systemctl status nginx`
2. Check app: `sudo systemctl status whisper`
3. Check ports: `sudo netstat -tlnp | grep -E '8000|8080|8443'`
4. Ensure AWS security group allows ports 8080 and 8443

### If transcription is slow
- Consider using a GPU instance
- Or use a smaller model like whisper-base