#!/usr/bin/env bash
# ==============================================================================
# NagrikSetu - Automated AWS EC2 Deployment Script
# Target OS: Ubuntu 22.04 / 24.04 LTS (x86_64)
# Recommended Instance: t3.medium (4 GiB RAM, 25 GB SSD)
# ==============================================================================

set -euo pipefail

echo "=================================================================="
echo "    NAGRIKSETU - AWS EC2 AUTOMATED MICROSERVICES DEPLOYMENT       "
echo "=================================================================="

# 1. Detect Host Public IP Address
echo "[1/7] Detecting EC2 Public IP address..."
PUBLIC_IP=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s --connect-timeout 5 https://checkip.amazonaws.com 2>/dev/null || curl -s --connect-timeout 5 https://ifconfig.me 2>/dev/null || echo "127.0.0.1")
fi
echo "==> Public IP detected: $PUBLIC_IP"

# 2. Configure Swap Space (4 GB) to prevent OOM during Docker build
echo "[2/7] Configuring 4 GB swap file for build stability..."
if ! grep -q "swapfile" /etc/fstab; then
    sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "==> 4 GB swap configured successfully."
else
    echo "==> Swap file already configured."
fi

# 3. Update Package Repositories and Install Dependencies
echo "[3/7] Updating apt repositories and installing prerequisites..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git ufw

# 4. Install Official Docker Engine and Docker Compose Plugin
echo "[4/7] Installing Docker Engine & Docker Compose..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER" || true
    echo "==> Docker Engine installed successfully."
else
    echo "==> Docker is already installed: $(docker --version)"
fi

# 5. Setup Project Code Directory
echo "[5/7] Preparing project repository..."
TARGET_DIR="$HOME/nagriksetu"
if [ -d "$TARGET_DIR/.git" ]; then
    echo "==> Repository exists at $TARGET_DIR, pulling latest changes from main..."
    cd "$TARGET_DIR"
    git fetch origin main
    git reset --hard origin/main
else
    echo "==> Cloning repository into $TARGET_DIR..."
    git clone https://github.com/VIDYASAGAR08/nagriksetu.git "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# 6. Configure Environment Variables
echo "[6/7] Generating environment configuration (.env)..."
cat <<EOF > .env
# NagrikSetu Production AWS Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=civicadmin_db
SECRET_KEY=nagriksetu-aws-production-secret-key-$(openssl rand -hex 16)
INITIAL_ADMIN_EMAIL=admin@civicportal.gov
INITIAL_ADMIN_PASSWORD=AdminPass123!@#

MYSQL_ROOT_PASSWORD=root_password_2026
MYSQL_DATABASE=skill_db
MYSQL_USER=nagriksetu_skill
MYSQL_PASSWORD=skill-app-pass-2026
JWT_SECRET=nagriksetu-skill-super-secret-key-2026-xyz-32char
ADMIN_EMAIL=skill.admin@nagriksetu.local
ADMIN_PASSWORD=SkillAdmin@2026!

RABBITMQ_USER=nagriksetu
RABBITMQ_PASS=nagriksetu-mq-pass-2026

PUBLIC_IP=${PUBLIC_IP}
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:8000,http://localhost:8001,http://localhost:8003,http://${PUBLIC_IP}:5173,http://${PUBLIC_IP}:5174,http://${PUBLIC_IP}:5175,http://${PUBLIC_IP}:8000,http://${PUBLIC_IP}:8001,http://${PUBLIC_IP}:8003
EOF

# 7. Build and Launch All 9 Microservices
echo "[7/7] Building and starting all 9 containers (this may take 3-5 minutes on initial build)..."
docker compose down || true
docker compose up -d --build

echo "Waiting for PostgreSQL and MySQL database health checks..."
sleep 15
docker compose ps

echo ""
echo "=================================================================="
echo "    NAGRIKSETU IS NOW FULLY DEPLOYED ON AWS EC2!                  "
echo "=================================================================="
echo ""
echo "  1. Central Administrative Portal : http://${PUBLIC_IP}:5173"
echo "     - National Admin Login        : admin@civicportal.gov / AdminPass123!@#"
echo "     - Regional Admin (Bengaluru)  : admin.bengaluru@nagriksetu.gov.in / AdminPass123!@#"
echo "     - Citizen & Family Head Login : aarav.sharma@example.com / CitizenPass123!@"
echo "     - Parent Proxy Login          : priya.sharma@example.com / CitizenPass123!@"
echo ""
echo "  2. School Education Portal       : http://${PUBLIC_IP}:5174"
echo "     - SSO Parent Login (Priya)    : priya.sharma@example.com / CitizenPass123!@"
echo "     - School Admin Login          : principal@model.school.gov / SchoolPass123!@"
echo ""
echo "  3. Skill Development Portal      : http://${PUBLIC_IP}:5175"
echo "     - Citizen Learner Login       : priya.sharma@example.com / CitizenPass123!@"
echo "     - Skill Center Admin Login    : skill.admin@nagriksetu.local / SkillAdmin@2026!"
echo ""
echo "  4. REST API Swagger Documentation:"
echo "     - Administrative Backend API  : http://${PUBLIC_IP}:8000/docs"
echo "     - School Education Backend API: http://${PUBLIC_IP}:8001/docs"
echo "     - Skill Development API       : http://${PUBLIC_IP}:8003/docs"
echo "     - RabbitMQ Broker Web UI      : http://${PUBLIC_IP}:15672 (User: nagriksetu / Pass: nagriksetu-mq-pass-2026)"
echo ""
echo "=================================================================="
