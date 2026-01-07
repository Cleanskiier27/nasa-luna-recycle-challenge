# NetworkBuster Job Manager
# Manages the creation of NetworkBuster Linux distribution using PowerShell jobs

param(
    [string]$BackupDrive = "K:",
    [string]$DistroName = "NetworkBuster",
    [switch]$AsJob
)

Write-Host "🚀 NetworkBuster Job Manager" -ForegroundColor Blue
Write-Host "===========================" -ForegroundColor Blue

# Function to create NetworkBuster distribution
function New-NetworkBusterDistribution {
    param(
        [string]$BackupDrive,
        [string]$DistroName
    )

    Write-Host "📋 Starting NetworkBuster creation job..." -ForegroundColor Yellow

    # Check prerequisites
    if (-not (Test-Path $BackupDrive)) {
        throw "Backup drive $BackupDrive does not exist"
    }

    # Check if WSL is available
    try {
        $null = wsl --version
    } catch {
        throw "WSL is not installed or not available"
    }

    # Create backup directory
    $backupPath = Join-Path $BackupDrive "networkbuster-backup"
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

    Write-Host "📦 Installing Ubuntu 22.04 LTS..." -ForegroundColor Yellow
    $installResult = wsl --install -d Ubuntu-22.04 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Ubuntu: $installResult"
    }

    Write-Host "⏳ Waiting for installation..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20

    # Create configuration script
    $configScript = @"
#!/bin/bash
set -e
echo "🛡️ Configuring NetworkBuster..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y build-essential git curl wget vim htop tmux python3 python3-pip nodejs npm docker.io openssh-server ufw fail2ban

# Install cloud CLIs
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt update && sudo apt install -y google-cloud-sdk

# Configure services
sudo systemctl enable ssh && sudo systemctl start ssh
sudo ufw --force enable && sudo ufw allow ssh
sudo systemctl enable docker && sudo systemctl start docker
sudo usermod -aG docker `$USER

# Create directories
sudo mkdir -p /opt/networkbuster /var/log/networkbuster /etc/networkbuster

# Create user
sudo groupadd networkbuster 2>/dev/null || true
sudo useradd -m -g networkbuster -s /bin/bash networkbuster 2>/dev/null || true
sudo usermod -aG sudo,docker networkbuster

# Branding
sudo tee /etc/networkbuster/version << 'EOF'
NetworkBuster Linux Distribution v2.0
Based on Ubuntu 22.04 LTS
Integrated with Windows Subsystem for Linux
Build Date: `$(date)
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
pip3 install --user azure-storage-blob azure-identity scikit-learn pandas numpy fastapi uvicorn requests aiofiles

# Install Node packages
sudo npm install -g express socket.io cors helmet

# Backup setup
sudo mkdir -p /mnt/backup-drive
sudo tee /usr/local/bin/networkbuster-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/mnt/backup-drive/networkbuster-backup"
DATE=`$(date +%Y%m%d_%H%M%S)
echo "🛡️ NetworkBuster Backup: `$DATE"
mkdir -p "`$BACKUP_DIR/`$DATE"
tar -czf "`$BACKUP_DIR/`$DATE/system-config.tar.gz" /etc/networkbuster 2>/dev/null || true
tar -czf "`$BACKUP_DIR/`$DATE/user-data.tar.gz" /home/networkbuster 2>/dev/null || true
dpkg --get-selections > "`$BACKUP_DIR/`$DATE/installed-packages.list" 2>/dev/null || true
echo "✅ Backup completed: `$DATE"
EOF
sudo chmod +x /usr/local/bin/networkbuster-backup

# Daily backup cron
echo "0 2 * * * /usr/local/bin/networkbuster-backup" | sudo tee -a /etc/crontab

# Cleanup
sudo apt autoremove -y && sudo apt autoclean

echo "✅ NetworkBuster configuration complete!"
"@

    # Execute configuration
    Write-Host "⚙️ Configuring distribution..." -ForegroundColor Yellow
    $configScript | Out-File -FilePath $env:TEMP\networkbuster-config.ps1 -Encoding UTF8
    $configResult = wsl -d Ubuntu-22.04 bash $env:TEMP\networkbuster-config.ps1 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Configuration failed: $configResult"
    }

    # Export and rename distribution
    Write-Host "🏷️ Creating NetworkBuster distribution..." -ForegroundColor Yellow
    wsl --export Ubuntu-22.04 $env:TEMP\networkbuster.tar
    wsl --unregister Ubuntu-22.04
    wsl --import $DistroName $env:TEMP\networkbuster.tar $env:TEMP\networkbuster.tar

# Create Windows integration files
    Write-Host "🔗 Creating Windows integration..." -ForegroundColor Yellow

    # Desktop shortcut
    $batchContent = "@echo off`necho 🚀 Starting NetworkBuster Linux Distribution...`nwsl -d $DistroName"
    $batchContent | Out-File -FilePath "$env:USERPROFILE\Desktop\NetworkBuster.bat" -Encoding ASCII

    # Backup script
    $backupContent = @"
param([string]`$BackupDrive = "$BackupDrive")
Write-Host "💾 NetworkBuster Backup to `$BackupDrive" -ForegroundColor Blue
wsl -d $DistroName sudo mkdir -p /mnt/backup-drive
wsl -d $DistroName sudo mount -t drvfs `$BackupDrive /mnt/backup-drive -o metadata
wsl -d $DistroName sudo /usr/local/bin/networkbuster-backup
Write-Host "✅ Backup completed" -ForegroundColor Green
"@
    $backupContent | Out-File -FilePath "$env:USERPROFILE\Desktop\NetworkBuster-Backup.ps1" -Encoding UTF8

    # Cleanup
    Remove-Item $env:TEMP\networkbuster.tar -ErrorAction SilentlyContinue
    Remove-Item $env:TEMP\networkbuster-config.ps1 -ErrorAction SilentlyContinue

    Write-Host "✅ NetworkBuster distribution created successfully!" -ForegroundColor Green

    return @{
        Name = $DistroName
        BackupDrive = $BackupDrive
        BackupPath = $backupPath
        Status = "Completed"
        Timestamp = Get-Date
    }
}

# Main execution
if ($AsJob) {
    Write-Host "🔄 Starting NetworkBuster creation as background job..." -ForegroundColor Yellow

    $job = Start-Job -ScriptBlock ${function:New-NetworkBusterDistribution} -ArgumentList $BackupDrive, $DistroName

    Write-Host "📋 Job started with ID: $($job.Id)" -ForegroundColor Green
    Write-Host "🔍 Monitor progress with: Get-Job -Id $($job.Id)" -ForegroundColor Yellow
    Write-Host "📊 Get results with: Receive-Job -Id $($job.Id)" -ForegroundColor Yellow

    return $job
} else {
    try {
        $result = New-NetworkBusterDistribution -BackupDrive $BackupDrive -DistroName $DistroName

        Write-Host "" -ForegroundColor Green
        Write-Host "🎉 NetworkBuster Linux Distribution Created!" -ForegroundColor Green
        Write-Host "" -ForegroundColor Green
        Write-Host "📊 Distribution Details:" -ForegroundColor Blue
        Write-Host "  Name: $($result.Name)" -ForegroundColor White
        Write-Host "  Backup Drive: $($result.BackupDrive)" -ForegroundColor White
        Write-Host "  Backup Path: $($result.BackupPath)" -ForegroundColor White
        Write-Host "  Status: $($result.Status)" -ForegroundColor White
        Write-Host "  Completed: $($result.Timestamp)" -ForegroundColor White
        Write-Host "" -ForegroundColor Green
        Write-Host "🚀 Quick Start:" -ForegroundColor Yellow
        Write-Host "  • Run NetworkBuster.bat from desktop" -ForegroundColor White
        Write-Host "  • Or use: wsl -d $DistroName" -ForegroundColor White
        Write-Host "  • Backup: NetworkBuster-Backup.ps1" -ForegroundColor White

    } catch {
        Write-Host "❌ Creation failed: $_" -ForegroundColor Red
        exit 1
    }
}