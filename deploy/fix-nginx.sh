#!/usr/bin/env bash
# Reinstall host nginx site (IP + domain proxy) and reload. Safe after certbot — re-run certbot if :443 breaks.
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/techkraft}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo: sudo bash $APP_DIR/deploy/fix-nginx.sh"
  exit 1
fi

echo "==> Checking frontend on 127.0.0.1:8080..."
if ! curl -sf http://127.0.0.1:8080/ >/dev/null 2>&1; then
  echo "WARNING: Nothing responding on :8080 — start containers first:"
  echo "  cd $APP_DIR && docker compose -f docker-compose.prod.yml up -d"
fi

echo "==> Installing nginx site..."
cp "$APP_DIR/deploy/nginx-host.conf" /etc/nginx/sites-available/techkraft
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/techkraft /etc/nginx/sites-enabled/techkraft

nginx -t
systemctl reload nginx

echo "==> Done. Test:"
echo "  curl -I http://127.0.0.1:8080/"
echo "  curl -I http://127.0.0.1/"
echo "  curl -I https://pywithaayush.tech/"
