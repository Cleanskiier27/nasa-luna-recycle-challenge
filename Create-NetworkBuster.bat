@echo off
REM NetworkBuster Linux Distribution Creator
REM Creates a custom Ubuntu-based distribution with Windows integration

echo 🚀 NetworkBuster Linux Distribution Creator
echo ===========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as administrator
) else (
    echo ❌ Please run as administrator
    pause
    exit /b 1
)

REM Check if WSL is installed
wsl --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ WSL is not installed. Please install WSL first.
    echo Run: wsl --install
    pause
    exit /b 1
)

REM Check if K: drive exists
if not exist K:\ (
    echo ❌ Backup drive K: does not exist
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create backup directory
if not exist "K:\networkbuster-backup" (
    mkdir "K:\networkbuster-backup"
    echo 📁 Created backup directory: K:\networkbuster-backup
)

REM Install Ubuntu base
echo 📦 Installing Ubuntu 22.04 LTS base...
wsl --install -d Ubuntu-22.04
if %errorLevel% neq 0 (
    echo ❌ Failed to install Ubuntu
    pause
    exit /b 1
)

echo ✅ Ubuntu 22.04 LTS installed

REM Wait for installation
echo ⏳ Waiting for Ubuntu installation to complete...
timeout /t 20 /nobreak >nul

REM Create configuration script
echo # NetworkBuster Configuration Script > "%TEMP%\networkbuster-config.sh"
echo sudo apt update ^&^& sudo apt upgrade -y >> "%TEMP%\networkbuster-config.sh"
echo sudo apt install -y build-essential git curl wget vim htop tmux python3 python3-pip nodejs npm docker.io openssh-server ufw fail2ban unattended-upgrades >> "%TEMP%\networkbuster-config.sh"
echo curl -sL https://aka.ms/InstallAzureCLIDeb ^| sudo bash >> "%TEMP%\networkbuster-config.sh"
echo echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" ^| sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list >> "%TEMP%\networkbuster-config.sh"
echo curl https://packages.cloud.google.com/apt/doc/apt-key.gpg ^| sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - >> "%TEMP%\networkbuster-config.sh"
echo sudo apt update ^&^& sudo apt install -y google-cloud-sdk >> "%TEMP%\networkbuster-config.sh"
echo sudo systemctl enable ssh >> "%TEMP%\networkbuster-config.sh"
echo sudo systemctl start ssh >> "%TEMP%\networkbuster-config.sh"
echo sudo ufw --force enable >> "%TEMP%\networkbuster-config.sh"
echo sudo ufw allow ssh >> "%TEMP%\networkbuster-config.sh"
echo sudo systemctl enable docker >> "%TEMP%\networkbuster-config.sh"
echo sudo systemctl start docker >> "%TEMP%\networkbuster-config.sh"
echo sudo usermod -aG docker $USER >> "%TEMP%\networkbuster-config.sh"
echo sudo mkdir -p /opt/networkbuster /var/log/networkbuster /etc/networkbuster >> "%TEMP%\networkbuster-config.sh"
echo sudo groupadd networkbuster 2^>nul ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo sudo useradd -m -g networkbuster -s /bin/bash networkbuster 2^>nul ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo sudo usermod -aG sudo,docker networkbuster >> "%TEMP%\networkbuster-config.sh"
echo sudo tee /etc/networkbuster/version ^<^< 'EOF' >> "%TEMP%\networkbuster-config.sh"
echo NetworkBuster Linux Distribution v2.0 >> "%TEMP%\networkbuster-config.sh"
echo Based on Ubuntu 22.04 LTS >> "%TEMP%\networkbuster-config.sh"
echo Integrated with Windows Subsystem for Linux >> "%TEMP%\networkbuster-config.sh"
echo Build Date: $(date) >> "%TEMP%\networkbuster-config.sh"
echo EOF >> "%TEMP%\networkbuster-config.sh"
echo sudo tee /etc/update-motd.d/99-networkbuster ^<^< 'EOF' >> "%TEMP%\networkbuster-config.sh"
echo #!/bin/bash >> "%TEMP%\networkbuster-config.sh"
echo echo "" >> "%TEMP%\networkbuster-config.sh"
echo echo "🛰️  Welcome to NetworkBuster Linux" >> "%TEMP%\networkbuster-config.sh"
echo echo "   Integrated Ubuntu Distribution for Windows" >> "%TEMP%\networkbuster-config.sh"
echo echo "" >> "%TEMP%\networkbuster-config.sh"
echo cat /etc/networkbuster/version 2^>/dev/null ^|^| echo "Version info not available" >> "%TEMP%\networkbuster-config.sh"
echo echo "" >> "%TEMP%\networkbuster-config.sh"
echo EOF >> "%TEMP%\networkbuster-config.sh"
echo sudo chmod +x /etc/update-motd.d/99-networkbuster >> "%TEMP%\networkbuster-config.sh"
echo pip3 install --user azure-storage-blob azure-identity scikit-learn tensorflow torch transformers pandas numpy fastapi uvicorn requests aiofiles >> "%TEMP%\networkbuster-config.sh"
echo sudo npm install -g express socket.io cors helmet compression >> "%TEMP%\networkbuster-config.sh"
echo sudo mkdir -p /mnt/backup-drive >> "%TEMP%\networkbuster-config.sh"
echo sudo tee /usr/local/bin/networkbuster-backup ^<^< 'EOF' >> "%TEMP%\networkbuster-config.sh"
echo #!/bin/bash >> "%TEMP%\networkbuster-config.sh"
echo BACKUP_DIR="/mnt/backup-drive/networkbuster-backup" >> "%TEMP%\networkbuster-config.sh"
echo DATE=$(date +%%Y%%m%%d_%%H%%M%%S) >> "%TEMP%\networkbuster-config.sh"
echo echo "🛡️ NetworkBuster Backup Started: $DATE" >> "%TEMP%\networkbuster-config.sh"
echo mkdir -p "$BACKUP_DIR/$DATE" >> "%TEMP%\networkbuster-config.sh"
echo tar -czf "$BACKUP_DIR/$DATE/system-config.tar.gz" /etc/networkbuster /etc/update-motd.d/99-networkbuster 2^>/dev/null ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo tar -czf "$BACKUP_DIR/$DATE/user-data.tar.gz" /home/networkbuster 2^>/dev/null ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo tar -czf "$BACKUP_DIR/$DATE/logs.tar.gz" /var/log/networkbuster 2^>/dev/null ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo dpkg --get-selections ^> "$BACKUP_DIR/$DATE/installed-packages.list" 2^>/dev/null ^|^| true >> "%TEMP%\networkbuster-config.sh"
echo echo "✅ NetworkBuster Backup Completed: $DATE" >> "%TEMP%\networkbuster-config.sh"
echo EOF >> "%TEMP%\networkbuster-config.sh"
echo sudo chmod +x /usr/local/bin/networkbuster-backup >> "%TEMP%\networkbuster-config.sh"
echo echo "0 2 * * * /usr/local/bin/networkbuster-backup" ^| sudo tee -a /etc/crontab >> "%TEMP%\networkbuster-config.sh"
echo sudo apt autoremove -y >> "%TEMP%\networkbuster-config.sh"
echo sudo apt autoclean >> "%TEMP%\networkbuster-config.sh"
echo echo "✅ NetworkBuster configuration complete!" >> "%TEMP%\networkbuster-config.sh"

REM Execute configuration
echo ⚙️ Configuring NetworkBuster distribution...
wsl -d Ubuntu-22.04 bash "%TEMP%\networkbuster-config.sh"
if %errorLevel% neq 0 (
    echo ❌ Configuration failed
    pause
    exit /b 1
)

echo ✅ NetworkBuster configuration completed

REM Export and rename distribution
echo 🏷️ Creating NetworkBuster distribution...
wsl --export Ubuntu-22.04 "%TEMP%\networkbuster.tar"
wsl --unregister Ubuntu-22.04
wsl --import NetworkBuster "%TEMP%\networkbuster.tar" "%TEMP%\networkbuster.tar"
if %errorLevel% neq 0 (
    echo ❌ Failed to create NetworkBuster distribution
    pause
    exit /b 1
)

echo ✅ NetworkBuster distribution created

REM Create Windows integration files
echo 🔗 Creating Windows integration...

REM Desktop shortcut
echo @echo off > "%USERPROFILE%\Desktop\NetworkBuster.bat"
echo echo 🚀 Starting NetworkBuster Linux Distribution... >> "%USERPROFILE%\Desktop\NetworkBuster.bat"
echo wsl -d NetworkBuster >> "%USERPROFILE%\Desktop\NetworkBuster.bat"

REM Backup script
echo param([string]$BackupDrive = "K:") > "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"
echo Write-Host "💾 NetworkBuster Backup to $BackupDrive" -ForegroundColor Blue >> "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"
echo wsl -d NetworkBuster sudo mkdir -p /mnt/backup-drive >> "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"
echo wsl -d NetworkBuster sudo mount -t drvfs $BackupDrive /mnt/backup-drive -o metadata >> "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"
echo wsl -d NetworkBuster sudo /usr/local/bin/networkbuster-backup >> "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"
echo Write-Host "✅ Backup completed" -ForegroundColor Green >> "%USERPROFILE%\Desktop\NetworkBuster-Backup.ps1"

REM Clean up
del "%TEMP%\networkbuster.tar" 2>nul
del "%TEMP%\networkbuster-config.sh" 2>nul

REM Display completion information
echo.
echo 🎉 NetworkBuster Linux Distribution Created Successfully!
echo.
echo 📊 Distribution Information:
echo   Name: NetworkBuster
echo   Base: Ubuntu 22.04 LTS
echo   Backup Drive: K:
echo   Backup Path: K:\networkbuster-backup
echo.
echo 🚀 Usage:
echo   • Desktop shortcut: NetworkBuster.bat
echo   • Command line: wsl -d NetworkBuster
echo   • Backup script: NetworkBuster-Backup.ps1
echo.
echo 🛡️ Features:
echo   • Ubuntu 22.04 LTS base system
echo   • Windows Subsystem for Linux integration
echo   • Azure and Google Cloud CLI
echo   • Docker container support
echo   • Python AI/ML frameworks
echo   • Node.js development tools
echo   • Automated daily backups
echo   • Security hardening
echo.
echo 💡 Next Steps:
echo   1. Run NetworkBuster.bat to start the distribution
echo   2. Configure your cloud credentials if needed
echo   3. Run NetworkBuster-Backup.ps1 for manual backups
echo   4. Daily automatic backups are scheduled
echo.
echo Press any key to continue...
pause >nul