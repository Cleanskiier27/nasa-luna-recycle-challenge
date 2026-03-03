#!/bin/bash
# NetworkBuster Linux Distribution Setup Script
# Creates a custom Ubuntu-based distribution with Windows integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 NetworkBuster Linux Distribution Setup${NC}"
echo "=========================================="

# Check if running on Windows
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo -e "${RED}❌ This script must be run on Windows${NC}"
    exit 1
fi

# Check if WSL is installed
if ! command -v wsl &> /dev/null; then
    echo -e "${RED}❌ WSL is not installed. Please install WSL first.${NC}"
    echo "Run: wsl --install"
    exit 1
fi

# Install Ubuntu 22.04 LTS as base
echo -e "${YELLOW}📦 Installing Ubuntu 22.04 LTS base...${NC}"
wsl --install -d Ubuntu-22.04

# Wait for installation to complete
echo -e "${YELLOW}⏳ Waiting for Ubuntu installation to complete...${NC}"
sleep 10

# Set up NetworkBuster distribution
echo -e "${YELLOW}🔧 Setting up NetworkBuster distribution...${NC}"

# Create NetworkBuster setup script for inside WSL
cat > /tmp/networkbuster-setup.sh << 'EOF'
#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛡️ NetworkBuster Distribution Configuration${NC}"
echo "==========================================="

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo -e "${YELLOW}📦 Installing essential packages...${NC}"
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    vim \
    htop \
    tmux \
    python3 \
    python3-pip \
    nodejs \
    npm \
    docker.io \
    openssh-server \
    ufw \
    fail2ban \
    unattended-upgrades \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install development tools
echo -e "${YELLOW}🔧 Installing development tools...${NC}"
sudo apt install -y \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    nodejs \
    npm

# Install Azure CLI
echo -e "${YELLOW}☁️ Installing Azure CLI...${NC}"
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Google Cloud SDK
echo -e "${YELLOW}☁️ Installing Google Cloud SDK...${NC}"
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt update && sudo apt install -y google-cloud-sdk

# Configure SSH
echo -e "${YELLOW}🔐 Configuring SSH...${NC}"
sudo systemctl enable ssh
sudo systemctl start ssh
sudo ufw allow ssh

# Configure firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Install and configure Docker
echo -e "${YELLOW}🐳 Configuring Docker...${NC}"
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Create NetworkBuster directories
echo -e "${YELLOW}📁 Creating NetworkBuster directories...${NC}"
sudo mkdir -p /opt/networkbuster
sudo mkdir -p /var/log/networkbuster
sudo mkdir -p /etc/networkbuster

# Create NetworkBuster user and group
echo -e "${YELLOW}👤 Creating NetworkBuster user...${NC}"
sudo groupadd networkbuster
sudo useradd -m -g networkbuster -s /bin/bash networkbuster
sudo usermod -aG sudo,docker networkbuster

# Set up NetworkBuster branding
echo -e "${YELLOW}🎨 Setting up NetworkBuster branding...${NC}"
sudo tee /etc/networkbuster/version << 'NETBUSTER'
NetworkBuster Linux Distribution v2.0
Based on Ubuntu 22.04 LTS
Integrated with Windows Subsystem for Linux
Build Date: $(date)
NETBUSTER

# Create NetworkBuster MOTD
sudo tee /etc/update-motd.d/99-networkbuster << 'EOF'
#!/bin/bash
echo ""
echo "🛰️  Welcome to NetworkBuster Linux"
echo "   Integrated Ubuntu Distribution for Windows"
echo ""
cat /etc/networkbuster/version
echo ""
EOF
sudo chmod +x /etc/update-motd.d/99-networkbuster

# Install custom packages for NetworkBuster
echo -e "${YELLOW}📦 Installing NetworkBuster custom packages...${NC}"

# Install Python packages
pip3 install --user \
    azure-storage-blob \
    azure-identity \
    scikit-learn \
    tensorflow \
    torch \
    transformers \
    pandas \
    numpy \
    fastapi \
    uvicorn \
    requests \
    aiofiles

# Install Node.js packages globally
sudo npm install -g \
    @azure/storage-blob \
    express \
    socket.io \
    cors \
    helmet \
    compression

# Create NetworkBuster service
echo -e "${YELLOW}⚙️ Creating NetworkBuster service...${NC}"
sudo tee /etc/systemd/system/networkbuster.service << 'EOF'
[Unit]
Description=NetworkBuster Defense System
After=network.target

[Service]
Type=simple
User=networkbuster
WorkingDirectory=/opt/networkbuster
ExecStart=/usr/bin/python3 /opt/networkbuster/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Set up backup system
echo -e "${YELLOW}💾 Setting up backup system...${NC}"
sudo mkdir -p /mnt/k-drive
sudo tee /etc/fstab << 'EOF'
# NetworkBuster backup mount
/mnt/k-drive  /mnt/k-drive  drvfs  defaults  0 0
EOF

# Create backup script
sudo tee /usr/local/bin/networkbuster-backup << 'EOF'
#!/bin/bash
# NetworkBuster Backup Script

BACKUP_DIR="/mnt/k-drive/networkbuster-backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🛡️ NetworkBuster Backup Started: $DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup system configuration
tar -czf "$BACKUP_DIR/$DATE/system-config.tar.gz" /etc/networkbuster /etc/update-motd.d/99-networkbuster

# Backup user data
tar -czf "$BACKUP_DIR/$DATE/user-data.tar.gz" /home/networkbuster

# Backup logs
tar -czf "$BACKUP_DIR/$DATE/logs.tar.gz" /var/log/networkbuster

# Backup installed packages
dpkg --get-selections > "$BACKUP_DIR/$DATE/installed-packages.list"

echo "✅ NetworkBuster Backup Completed: $DATE"
echo "📁 Backup location: $BACKUP_DIR/$DATE"
EOF

sudo chmod +x /usr/local/bin/networkbuster-backup

# Set up cron job for automated backups
echo -e "${YELLOW}⏰ Setting up automated backups...${NC}"
sudo tee /etc/cron.daily/networkbuster-backup << 'EOF'
#!/bin/bash
/usr/local/bin/networkbuster-backup
EOF
sudo chmod +x /etc/cron.daily/networkbuster-backup

# Clean up
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
sudo apt autoremove -y
sudo apt autoclean

echo -e "${GREEN}✅ NetworkBuster Linux Distribution setup complete!${NC}"
echo ""
echo -e "${BLUE}🎉 NetworkBuster Features:${NC}"
echo "  • Ubuntu 22.04 LTS base"
echo "  • Windows Subsystem for Linux integration"
echo "  • Azure and Google Cloud CLI"
echo "  • Docker container support"
echo "  • Python AI/ML frameworks"
echo "  • Node.js development tools"
echo "  • Automated backup to K: drive"
echo "  • Security hardening"
echo ""
echo -e "${YELLOW}🔄 Please restart your WSL instance to apply all changes${NC}"
EOF

# Execute the setup script in WSL
echo -e "${YELLOW}⚙️ Configuring NetworkBuster inside WSL...${NC}"
wsl -d Ubuntu-22.04 bash /tmp/networkbuster-setup.sh

# Rename the distribution to NetworkBuster
echo -e "${YELLOW}🏷️ Renaming distribution to NetworkBuster...${NC}"
wsl --export Ubuntu-22.04 /tmp/networkbuster.tar
wsl --unregister Ubuntu-22.04
wsl --import NetworkBuster /tmp/networkbuster.tar /tmp/networkbuster.tar

# Clean up
rm -f /tmp/networkbuster.tar
rm -f /tmp/networkbuster-setup.sh

echo -e "${GREEN}🎉 NetworkBuster Linux Distribution created successfully!${NC}"
echo ""
echo -e "${BLUE}📊 NetworkBuster Information:${NC}"
echo "  Name: NetworkBuster"
echo "  Base: Ubuntu 22.04 LTS"
echo "  Integration: Windows Subsystem for Linux"
echo "  Backup Location: K:\networkbuster-backup"
echo ""
echo -e "${YELLOW}🚀 To use NetworkBuster:${NC}"
echo "  wsl -d NetworkBuster"
echo ""
echo -e "${YELLOW}💾 To run backup:${NC}"
echo "  wsl -d NetworkBuster sudo /usr/local/bin/networkbuster-backup"