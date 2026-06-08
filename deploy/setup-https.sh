#!/usr/bin/env bash
# One-time HTTPS setup: free port 80 for host nginx, proxy to Docker on 8080, run certbot.
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/techkraft}"
DOMAIN="${DOMAIN:-pywithaayush.tech}"
WWW_DOMAIN="${WWW_DOMAIN:-www.pywithaayush.tech}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash $APP_DIR/deploy/setup-https.sh"
  exit 1
fi

echo "==> Installing nginx + certbot (if missing)..."
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx certbot python3-certbot-nginx

echo "==> Binding frontend container to 127.0.0.1:8080 only..."
cd "$APP_DIR"
if grep -q '"80:80"' docker-compose.prod.yml; then
  sed -i 's/"80:80"/"127.0.0.1:8080:80"/' docker-compose.prod.yml
fi

docker compose -f docker-compose.prod.yml up -d frontend

echo "==> Installing host nginx site..."
cp "$APP_DIR/deploy/nginx-host.conf" /etc/nginx/sites-available/techkraft
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/techkraft
ln -s /etc/nginx/sites-available/techkraft /etc/nginx/sites-enabled/techkraft

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "==> Requesting Let's Encrypt certificate..."
certbot --nginx -d "$DOMAIN" -d "$WWW_DOMAIN"

echo ""
echo "✓ HTTPS setup complete — https://$DOMAIN"
echo "  Update CORS_ORIGINS in $APP_DIR/.env if needed, then:"
echo "  docker compose -f $APP_DIR/docker-compose.prod.yml restart backend"
