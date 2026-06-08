#!/usr/bin/env bash
# One-time Azure VM setup for TechKraft Recruit.
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/techkraft}"

echo "==> TechKraft VM setup (app dir: $APP_DIR)"

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "==> Installing packages..."
$SUDO apt-get update -qq
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  ca-certificates curl git gnupg lsb-release

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | $SUDO sh
fi

$SUDO usermod -aG docker "$USER" || true

if [ ! -f /swapfile ]; then
  echo "==> Creating 2 GB swap (helps on 1 GB RAM VMs)..."
  $SUDO fallocate -l 2G /swapfile || $SUDO dd if=/dev/zero of=/swapfile bs=1M count=2048
  $SUDO chmod 600 /swapfile
  $SUDO mkswap /swapfile
  $SUDO swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | $SUDO tee -a /etc/fstab
fi

if [ ! -d "$APP_DIR/.git" ]; then
  echo "==> Clone the repo into $APP_DIR before running migrations."
  echo "    Example:"
  echo "    git clone https://YOUR_TOKEN@github.com/YOUR_USER/techkraft.git $APP_DIR"
else
  echo "==> Repo already present at $APP_DIR"
fi

PUBLIC_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')

cat <<EOF

============================================================
TechKraft VM setup complete
============================================================
Public IP: $PUBLIC_IP

Next steps:
1. Clone repo to $APP_DIR (if not done)
2. cp .env.example .env  &&  nano .env
   - Set POSTGRES_PASSWORD, SECRET_KEY, CORS_ORIGINS=http://$PUBLIC_IP
   - Set GHCR_OWNER to your GitHub username
   - Set EMAIL_ENABLED / SMTP_* if using notifications
3. Log in to ghcr.io:
   echo "ghp_TOKEN" | docker login ghcr.io -u YOUR_USER --password-stdin
4. Push to main (GitHub Actions builds images), then:
   bash $APP_DIR/deploy/deploy.sh

GitHub Actions secrets for auto-deploy:
  VM_HOST=$PUBLIC_IP
  VM_USER=$USER
  VM_SSH_KEY=<private deploy key>
  VM_APP_DIR=$APP_DIR
============================================================
EOF
