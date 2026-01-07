#!/bin/bash
# NetworkBuster Linux Distribution Setup (Simplified)
# Creates a custom Ubuntu-based distribution with Windows integration

set -e

echo "🚀 NetworkBuster Linux Distribution Creator (Simplified)"
echo "======================================================"

# Check if running in WSL
if [[ ! -f /proc/version ]] || ! grep -q "Microsoft" /proc/version 2>/dev/null && ! grep -q "WSL" /proc/version 2>/dev/null; then
    echo "❌ This script should be run inside WSL"
    echo "Please run: wsl -d Ubuntu-22.04 bash <(curl -s https://raw.githubusercontent.com/your-repo/networkbuster-setup.sh)"
    exit 1
fi

echo "✅ Running in WSL environment"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
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
    openssh-server \
    ufw \
    fail2ban \
    unattended-upgrades

# Install cloud CLIs
echo "☁️ Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

echo "☁️ Installing Google Cloud SDK..."
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt update && sudo apt install -y google-cloud-sdk

# Configure services
echo "🔐 Configuring SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh
sudo ufw --force enable
sudo ufw allow ssh

# Create NetworkBuster directories
echo "📁 Creating NetworkBuster directories..."
sudo mkdir -p /opt/networkbuster
sudo mkdir -p /var/log/networkbuster
sudo mkdir -p /etc/networkbuster

# Create NetworkBuster user
echo "👤 Creating NetworkBuster user..."
sudo groupadd networkbuster 2>/dev/null || true
sudo useradd -m -g networkbuster -s /bin/bash networkbuster 2>/dev/null || true
sudo usermod -aG sudo networkbuster

# Set up branding
echo "🎨 Setting up NetworkBuster branding..."
sudo tee /etc/networkbuster/version << 'EOF'
NetworkBuster Linux Distribution v2.0
Based on Ubuntu 22.04 LTS
Integrated with Windows Subsystem for Linux
Build Date: $(date)
EOF

sudo tee /etc/update-motd.d/99-networkbuster << 'EOF'
#!/bin/bash
echo ""
echo "🛰️  Welcome to NetworkBuster Linux"
echo "   Integrated Ubuntu Distribution for Windows"
echo ""
cat /etc/networkbuster/version 2>/dev/null || echo "Version info not available"
echo ""
EOF
sudo chmod +x /etc/update-motd.d/99-networkbuster

# Install Python packages
echo "🐍 Installing Python AI/ML packages..."
pip3 install --user \
    azure-storage-blob \
    azure-identity \
    scikit-learn \
    pandas \
    numpy \
    fastapi \
    uvicorn \
    requests \
    aiofiles

# Install Node.js packages
echo "📦 Installing Node.js packages..."
sudo npm install -g \
    express \
    socket.io \
    cors \
    helmet \
    compression

# Set up backup system
echo "💾 Setting up backup system..."
sudo mkdir -p /mnt/k-drive-backup

# Create backup script
sudo tee /usr/local/bin/networkbuster-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/mnt/k-drive-backup/networkbuster-backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🛡️ NetworkBuster Backup Started: $DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup system configuration
tar -czf "$BACKUP_DIR/$DATE/system-config.tar.gz" /etc/networkbuster /etc/update-motd.d/99-networkbuster 2>/dev/null || true

# Backup user data
tar -czf "$BACKUP_DIR/$DATE/user-data.tar.gz" /home/networkbuster 2>/dev/null || true

# Backup logs
tar -czf "$BACKUP_DIR/$DATE/logs.tar.gz" /var/log/networkbuster 2>/dev/null || true

# Backup installed packages
dpkg --get-selections > "$BACKUP_DIR/$DATE/installed-packages.list" 2>/dev/null || true

echo "✅ NetworkBuster Backup Completed: $DATE"
echo "📁 Backup location: $BACKUP_DIR/$DATE"
EOF

sudo chmod +x /usr/local/bin/networkbuster-backup

# Set up daily backup cron job
echo "⏰ Setting up automated backups..."
echo "0 2 * * * /usr/local/bin/networkbuster-backup" | sudo tee -a /etc/crontab

# Clean up
echo "🧹 Cleaning up..."
sudo apt autoremove -y
sudo apt autoclean

echo ""
echo "🎉 NetworkBuster Linux Distribution Setup Complete!"
echo ""
echo "📊 Distribution Information:"
echo "  Name: NetworkBuster"
echo "  Base: Ubuntu 22.04 LTS"
echo "  Integration: Windows Subsystem for Linux"
echo ""
echo "🚀 Features:"
echo "  • Ubuntu 22.04 LTS base system"
echo "  • Azure and Google Cloud CLI"
echo "  • Python AI/ML frameworks"
echo "  • Node.js development tools"
echo "  • Automated daily backups to K: drive"
echo "  • Security hardening"
echo ""
echo "💡 Usage:"
echo "  • Check version: cat /etc/networkbuster/version"
echo "  • Manual backup: sudo /usr/local/bin/networkbuster-backup"
echo "  • Monitor system: htop"
echo ""
echo "🔧 Next Steps:"
echo "  1. Configure your cloud credentials:"
echo "     az login"
echo "     gcloud auth login"
echo "  2. Mount K: drive for backups:"
echo "     sudo mount -t drvfs K: /mnt/k-drive-backup -o metadata"
echo "  3. Start developing with your AI/ML tools!"