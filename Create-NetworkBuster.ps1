# NetworkBuster Linux Distribution Creator
# Creates a custom Ubuntu-based distribution integrated with Windows

param(
    [string]$BackupDrive = "K:",
    [string]$DistroName = "NetworkBuster"
)

Write-Host "🚀 NetworkBuster Linux Distribution Creator" -ForegroundColor Blue
Write-Host "==========================================" -ForegroundColor Blue

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ Please run this script as Administrator" -ForegroundColor Red
    exit 1
}

# Check if WSL is installed
try {
    $wslVersion = wsl --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "WSL not found"
    }
} catch {
    Write-Host "❌ WSL is not installed. Please install WSL first." -ForegroundColor Red
    Write-Host "Run: wsl --install" -ForegroundColor Yellow
    exit 1
}

# Check if backup drive exists
if (-not (Test-Path $BackupDrive)) {
    Write-Host "❌ Backup drive $BackupDrive does not exist" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Create backup directory structure
$backupPath = Join-Path $BackupDrive "networkbuster-backup"
if (-not (Test-Path $backupPath)) {
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    Write-Host "📁 Created backup directory: $backupPath" -ForegroundColor Yellow
}

# Install Ubuntu base
Write-Host "📦 Installing Ubuntu 22.04 LTS base..." -ForegroundColor Yellow
try {
    wsl --install -d Ubuntu-22.04
    Write-Host "✅ Ubuntu 22.04 LTS installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install Ubuntu: $_" -ForegroundColor Red
    exit 1
}

# Wait for installation
Write-Host "⏳ Waiting for Ubuntu installation to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Create NetworkBuster configuration script
$configScript = @"
#!/bin/bash
set -e

# NetworkBuster Configuration Script
echo "🛡️ Configuring NetworkBuster Distribution..."

# Update and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y build-essential git curl wget vim htop tmux python3 python3-pip nodejs npm docker.io openssh-server ufw fail2ban unattended-upgrades

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Google Cloud SDK
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt update && sudo apt install -y google-cloud-sdk

# Configure SSH and firewall
sudo systemctl enable ssh
sudo systemctl start ssh
sudo ufw --force enable
sudo ufw allow ssh

# Configure Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker `$USER

# Create NetworkBuster directories
sudo mkdir -p /opt/networkbuster /var/log/networkbuster /etc/networkbuster

# Create NetworkBuster user
sudo groupadd networkbuster 2>/dev/null || true
sudo useradd -m -g networkbuster -s /bin/bash networkbuster 2>/dev/null || true
sudo usermod -aG sudo,docker networkbuster

# Set up branding
sudo tee /etc/networkbuster/version << 'EOF'
NetworkBuster Linux Distribution v2.0
Based on Ubuntu 22.04 LTS
Integrated with Windows Subsystem for Linux
Build Date: `$(date)
EOF

# Create MOTD
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
pip3 install --user azure-storage-blob azure-identity scikit-learn tensorflow torch transformers pandas numpy fastapi uvicorn requests aiofiles

# Install Node.js packages
sudo npm install -g @azure/storage-blob express socket.io cors helmet compression

# Set up backup mount point
sudo mkdir -p /mnt/backup-drive

# Create backup script
sudo tee /usr/local/bin/networkbuster-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/mnt/backup-drive/networkbuster-backup"
DATE=`$(date +%Y%m%d_%H%M%S)

echo "🛡️ NetworkBuster Backup Started: `$DATE"

mkdir -p "`$BACKUP_DIR/`$DATE"

# Backup system configuration
tar -czf "`$BACKUP_DIR/`$DATE/system-config.tar.gz" /etc/networkbuster /etc/update-motd.d/99-networkbuster 2>/dev/null || true

# Backup user data
tar -czf "`$BACKUP_DIR/`$DATE/user-data.tar.gz" /home/networkbuster 2>/dev/null || true

# Backup logs
tar -czf "`$BACKUP_DIR/`$DATE/logs.tar.gz" /var/log/networkbuster 2>/dev/null || true

# Backup installed packages
dpkg --get-selections > "`$BACKUP_DIR/`$DATE/installed-packages.list" 2>/dev/null || true

echo "✅ NetworkBuster Backup Completed: `$DATE"
EOF

sudo chmod +x /usr/local/bin/networkbuster-backup

# Set up daily backup cron job
echo "0 2 * * * /usr/local/bin/networkbuster-backup" | sudo tee -a /etc/crontab

# Clean up
sudo apt autoremove -y
sudo apt autoclean

echo "✅ NetworkBuster configuration complete!"
"@

# Save configuration script
$configScript | Out-File -FilePath "$env:TEMP\networkbuster-config.sh" -Encoding UTF8

# Execute configuration in WSL
Write-Host "⚙️ Configuring NetworkBuster distribution..." -ForegroundColor Yellow
try {
    wsl -d Ubuntu-22.04 bash $env:TEMP\networkbuster-config.sh
    Write-Host "✅ NetworkBuster configuration completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Configuration failed: $_" -ForegroundColor Red
    exit 1
}

# Export and re-import as NetworkBuster
Write-Host "🏷️ Creating NetworkBuster distribution..." -ForegroundColor Yellow
try {
    wsl --export Ubuntu-22.04 $env:TEMP\networkbuster.tar
    wsl --unregister Ubuntu-22.04
    wsl --import $DistroName $env:TEMP\networkbuster.tar $env:TEMP\networkbuster.tar
    Write-Host "✅ NetworkBuster distribution created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create NetworkBuster distribution: $_" -ForegroundColor Red
    exit 1
}

# Set up Windows integration
Write-Host "🔗 Setting up Windows integration..." -ForegroundColor Yellow

# Create Windows batch file for easy access
$batchFile = @"
@echo off
echo 🚀 Starting NetworkBuster Linux Distribution...
wsl -d $DistroName
"@

$batchFile | Out-File -FilePath "$env:USERPROFILE\Desktop\NetworkBuster.bat" -Encoding ASCII

# Create PowerShell script for backup
$backupScript = @"
param(
    [string]`$BackupDrive = "$BackupDrive"
)

Write-Host "💾 NetworkBuster Backup to `$BackupDrive" -ForegroundColor Blue

# Mount backup drive in WSL
wsl -d $DistroName sudo mkdir -p /mnt/backup-drive
wsl -d $DistroName sudo mount -t drvfs `$BackupDrive /mnt/backup-drive -o metadata

# Run backup
wsl -d $DistroName sudo /usr/local/bin/networkbuster-backup

Write-Host "✅ Backup completed" -ForegroundColor Green
"@

$backupScript | Out-File -FilePath "$env:USERPROFILE\Desktop\NetworkBuster-Backup.ps1" -Encoding UTF8

# Clean up temporary files
Remove-Item $env:TEMP\networkbuster.tar -ErrorAction SilentlyContinue
Remove-Item $env:TEMP\networkbuster-config.sh -ErrorAction SilentlyContinue

# Display completion information
Write-Host "" -ForegroundColor Green
Write-Host "🎉 NetworkBuster Linux Distribution Created Successfully!" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "📊 Distribution Information:" -ForegroundColor Blue
Write-Host "  Name: $DistroName" -ForegroundColor White
Write-Host "  Base: Ubuntu 22.04 LTS" -ForegroundColor White
Write-Host "  Backup Drive: $BackupDrive" -ForegroundColor White
Write-Host "  Backup Path: $backupPath" -ForegroundColor White
Write-Host "" -ForegroundColor Green
Write-Host "🚀 Usage:" -ForegroundColor Yellow
Write-Host "  • Desktop shortcut: NetworkBuster.bat" -ForegroundColor White
Write-Host "  • Command line: wsl -d $DistroName" -ForegroundColor White
Write-Host "  • Backup script: NetworkBuster-Backup.ps1" -ForegroundColor White
Write-Host "" -ForegroundColor Green
Write-Host "🛡️ Features:" -ForegroundColor Blue
Write-Host "  • Ubuntu 22.04 LTS base system" -ForegroundColor White
Write-Host "  • Windows Subsystem for Linux integration" -ForegroundColor White
Write-Host "  • Azure and Google Cloud CLI" -ForegroundColor White
Write-Host "  • Docker container support" -ForegroundColor White
Write-Host "  • Python AI/ML frameworks" -ForegroundColor White
Write-Host "  • Node.js development tools" -ForegroundColor White
Write-Host "  • Automated daily backups" -ForegroundColor White
Write-Host "  • Security hardening" -ForegroundColor White
Write-Host "" -ForegroundColor Green
Write-Host "💡 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run NetworkBuster.bat to start the distribution" -ForegroundColor White
Write-Host "  2. Configure your cloud credentials if needed" -ForegroundColor White
Write-Host "  3. Run NetworkBuster-Backup.ps1 for manual backups" -ForegroundColor White
Write-Host "  4. Daily automatic backups are scheduled" -ForegroundColor White