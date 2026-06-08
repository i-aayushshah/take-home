# Deploy TechKraft to Azure — Beginner Guide

> **Never hosted before? That's fine.** This guide explains every step.
> Set aside **~1 hour** the first time. After setup, every `git push` to `main` deploys automatically.

---

## What we're building

```
Your laptop
    │  git push
    ▼
GitHub
    ├── GitHub Actions BUILDS the Docker images (~3–5 min)
    │        │  pushes images to ghcr.io
    │        ▼
    │   ghcr.io  ──────────────┐
    │                          │ VM pulls ready-made images
    │  auto SSH ───────────────┤
    ▼                          ▼
Azure Virtual Machine (always on)
    ├── TechKraft frontend (nginx + React static build)
    ├── FastAPI backend
    ├── PostgreSQL
    └── Redis
```

**Why build on GitHub, not on the VM?** A `Standard_B2ats_v2` VM has only **1 GB RAM**. Building the frontend needs ~1.5 GB. GitHub Actions builds on a 7 GB runner and uploads images to **ghcr.io**. The VM just downloads and runs them.

---

## What you need

- [ ] Project pushed to a **GitHub repository**
- [ ] **Azure for Students** account
- [ ] **Windows PowerShell** or Windows Terminal
- [ ] About 1 hour for first-time setup

---

## Part 1 — Install tools on your laptop

### 1.1 — Azure CLI

1. https://aka.ms/installazurecliwindows
2. Run the `.msi` installer
3. **Close and reopen** your terminal
4. Verify:

```powershell
az --version
```

### 1.2 — Docker Desktop (local dev / optional)

1. https://www.docker.com/products/docker-desktop/
2. Install and restart if prompted
3. Verify:

```powershell
docker --version
```

---

## Part 2 — Create your Azure VM

### 2.1 — Login

```powershell
az login
```

Sign in with your Azure for Students account in the browser.

### 2.2 — Delete old resource group (if retrying)

```powershell
az group delete --name techkraft-rg --yes --no-wait
```

Wait ~30 seconds, then continue.

### 2.3 — Resource group (Korea Central)

```powershell
az group create --name techkraft-rg --location koreacentral
```

> `koreacentral` is often the only region with VM quota on Azure for Students (UWE Bristol).

### 2.4 — Create the VM

```powershell
az vm create `
  --resource-group techkraft-rg `
  --name techkraft-vm `
  --location koreacentral `
  --image Ubuntu2404 `
  --size Standard_B2ats_v2 `
  --admin-username azureuser `
  --generate-ssh-keys `
  --public-ip-sku Standard `
  --os-disk-size-gb 32 `
  --storage-sku Standard_LRS
```

Takes **3–5 minutes**. Save the **`publicIpAddress`** from the output — that is your server address.

| Cost item | Approx/month |
|---|---|
| VM `Standard_B2ats_v2` (1 GB RAM) | ~$8.54 |
| 32 GB HDD disk | ~$0.88 |
| Standard public IP | ~$3.65 |
| **Total** | **~$13.07** |

The VM may be **free-tier eligible** on Azure for Students — check Cost Management in the portal.

### 2.5 — Memory on a 1 GB VM

| Container | RAM limit | Role |
|---|---|---|
| PostgreSQL | 200 MB | tuned `shared_buffers=64MB` |
| Redis | 64 MB | cache / rate limits |
| FastAPI backend | 256 MB | 1 Uvicorn worker |
| nginx frontend | 64 MB | static SPA + API proxy |
| OS + Docker | ~200 MB | overhead |
| **Total** | **~784 MB** | fits with 2 GB swap from `setup-vm.sh` |

### 2.6 — Open firewall ports

```powershell
az vm open-port --resource-group techkraft-rg --name techkraft-vm --port 80 --priority 100
az vm open-port --resource-group techkraft-rg --name techkraft-vm --port 443 --priority 110
```

---

## Part 3 — Connect to the VM

```powershell
ssh azureuser@YOUR_VM_IP
```

Type `yes` on first connect. Your prompt becomes `azureuser@techkraft-vm:~$`.

---

## Part 4 — One-time VM setup

### 4.1 — Clone the repo

For a **private** repo, create a GitHub classic token with **`repo`** scope at https://github.com/settings/tokens

On the VM:

```bash
sudo mkdir -p /srv/techkraft
sudo chown azureuser:azureuser /srv/techkraft
git clone https://YOUR_GITHUB_USER:ghp_YOUR_TOKEN@github.com/YOUR_GITHUB_USER/techkraft.git /srv/techkraft
```

Run setup:

```bash
bash /srv/techkraft/deploy/setup-vm.sh
```

Then activate the docker group (or log out and back in):

```bash
newgrp docker
```

### 4.2 — Configure `.env`

```bash
cp /srv/techkraft/.env.example /srv/techkraft/.env
nano /srv/techkraft/.env
```

**Required production values:**

```env
POSTGRES_DB=take-home
POSTGRES_USER=postgres
POSTGRES_PASSWORD=choose_a_strong_password

SECRET_KEY=long_random_string_for_jwt_signing

GHCR_OWNER=your-github-username-lowercase

CORS_ORIGINS=http://YOUR_VM_IP

VITE_API_URL=
# Leave empty in production — nginx proxies /api to the backend

EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=your@gmail.com

GITHUB_TOKEN=ghp_your_models_token
GITHUB_MODEL=openai/gpt-4o
AI_SUMMARY_FALLBACK_MOCK=false
```

> **Gmail:** use an [App Password](https://myaccount.google.com/apppasswords). `SMTP_FROM` must match `SMTP_USER` for Gmail.

### 4.3 — Log in to ghcr.io (one time)

Create a classic token with **`read:packages`** scope.

```bash
echo "ghp_YOUR_read_packages_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
```

You should see `Login Succeeded`.

---

## Part 5 — First deploy

### Step 1 — Trigger image build (laptop)

Push to `main` (or run the workflow manually in GitHub → Actions):

```powershell
git push origin main
```

Wait for the **build** job to finish green (~3–5 min). This publishes:

- `ghcr.io/YOUR_USER/techkraft-backend:latest`
- `ghcr.io/YOUR_USER/techkraft-frontend:latest`

### Step 2 — Deploy on the VM

```bash
bash /srv/techkraft/deploy/deploy.sh
```

First deploy with an empty database — seed once:

```bash
RUN_SEED_ON_DEPLOY=true bash /srv/techkraft/deploy/deploy.sh
```

When complete:

```
  ✓ Backend is healthy
  ✓ Frontend is healthy
  ✓ Deploy complete
```

Open **http://YOUR_VM_IP** in your browser.

> **Security:** Change seeded admin passwords immediately after first login, or create new admin users and disable seed accounts.

---

## Part 6 — Auto-deploy on every push

### 6.1 — Deploy SSH key (laptop)

```powershell
ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$HOME\.ssh\techkraft_deploy"
```

Press Enter twice for no passphrase.

### 6.2 — Add public key to VM

```powershell
$pubKey = Get-Content "$HOME\.ssh\techkraft_deploy.pub"
ssh azureuser@YOUR_VM_IP "echo '$pubKey' >> ~/.ssh/authorized_keys"
```

### 6.3 — GitHub repository secrets

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Name | Value |
|---|---|
| `VM_HOST` | Your VM public IP |
| `VM_USER` | `azureuser` |
| `VM_SSH_KEY` | Full private key: `Get-Content "$HOME\.ssh\techkraft_deploy"` |
| `VM_APP_DIR` | `/srv/techkraft` |

### 6.4 — Test

```powershell
git add .
git commit -m "test: auto-deploy"
git push origin main
```

GitHub Actions runs **build** then **deploy**. Green checkmark = live in ~5 minutes.

---

## Part 7 — (Optional) Custom domain + HTTPS

### 7.1 — DNS

At your registrar, add:

| Type | Name | Value |
|---|---|---|
| A | `@` | `YOUR_VM_IP` |
| A | `www` | `YOUR_VM_IP` |

Verify:

```powershell
nslookup yourdomain.com
```

### 7.2 — Host nginx + Let's Encrypt

Because the frontend container already uses port 80, map it to localhost only and put host nginx in front.

On the VM, edit compose port mapping temporarily — or use this pattern:

```bash
# Install host nginx + certbot
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Point host nginx at the container (frontend on 127.0.0.1:8080)
# Edit docker-compose.prod.yml frontend ports: "127.0.0.1:8080:80"
# Then redeploy: bash /srv/techkraft/deploy/deploy.sh
```

Example host site (`/etc/nginx/sites-available/techkraft`):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/techkraft /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Update CORS:

```bash
nano /srv/techkraft/.env
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
docker compose -f /srv/techkraft/docker-compose.prod.yml restart backend
```

---

## What happens on each push

```
git push origin main
    → GitHub Actions: build backend + frontend images → ghcr.io
    → GitHub Actions: SSH to VM → deploy/deploy.sh
        → git pull (compose, migrations, scripts)
        → docker compose pull (no build on VM)
        → alembic upgrade head
        → docker compose up -d
        → health checks
```

---

## Handy commands (on the VM)

```bash
# Service status
docker compose -f /srv/techkraft/docker-compose.prod.yml ps

# Live logs
docker compose -f /srv/techkraft/docker-compose.prod.yml logs -f

# Manual deploy
bash /srv/techkraft/deploy/deploy.sh

# Restart backend only
docker compose -f /srv/techkraft/docker-compose.prod.yml restart backend

# Database shell
docker compose -f /srv/techkraft/docker-compose.prod.yml exec db \
  psql -U postgres -d take-home
```

---

## Troubleshooting

### Site not loading

```bash
docker compose -f /srv/techkraft/docker-compose.prod.yml ps
docker compose -f /srv/techkraft/docker-compose.prod.yml logs backend
```

### GitHub Actions deploy failed

Check **Actions** → failed step. Wrong `VM_HOST` or `VM_SSH_KEY` only breaks **deploy**; **build** still pushes images. Deploy manually with `bash /srv/techkraft/deploy/deploy.sh`.

### `denied` / `unauthorized` pulling images

Re-login to ghcr.io (token needs `read:packages`):

```bash
echo "ghp_TOKEN" | docker login ghcr.io -u YOUR_USER --password-stdin
```

### `manifest unknown`

Images not built yet. Push to `main` and wait for the **build** job to finish first.

### Emails not sending

- `EMAIL_ENABLED=true` in `.env`
- Gmail: `SMTP_FROM` must equal `SMTP_USER`
- Interview emails go to **both** the candidate and the assigned reviewer

### SSH connection refused

VM may be stopped. Azure Portal → Virtual Machines → **Start**, wait 2 minutes.

---

## Personal checklist (gitignored)

Copy notes to `azure_deployed.md` (gitignored) — VM IP, tokens, domain, passwords. Never commit secrets.

---

## Monthly cost summary

| Scenario | Monthly | Months on $100 credit |
|---|---|---|
| Full price | ~$13.07 | ~7.6 months |
| VM free-tier eligible | ~$4.53 (disk + IP) | ~22 months |

Check credit: Azure Portal → **Cost Management**.
