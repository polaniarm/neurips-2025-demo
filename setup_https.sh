#!/bin/bash

# Generate self-signed certificate for testing
# Run this on your AWS server

# Create certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "Certificate created. Run server with:"
echo "uvicorn server:app --host 0.0.0.0 --port 8443 --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem"