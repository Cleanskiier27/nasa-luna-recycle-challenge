# NetworkBuster Linux Distribution

A custom Ubuntu-based Linux distribution integrated with Windows Subsystem for Linux (WSL), designed for development, cloud operations, and AI/ML workloads.

## 🚀 Features

- **Ubuntu 22.04 LTS Base**: Stable, long-term support foundation
- **Windows Integration**: Seamless WSL integration with Windows
- **Cloud-Native**: Pre-installed Azure CLI and Google Cloud SDK
- **Development Ready**: Python, Node.js, Docker, and essential dev tools
- **AI/ML Support**: TensorFlow, PyTorch, scikit-learn pre-installed
- **Security Hardened**: UFW firewall, Fail2Ban, unattended upgrades
- **Automated Backups**: Daily backups to configurable drive (default: K:)
- **Container Support**: Docker with privileged access

## 📋 Prerequisites

- Windows 10/11 Pro or Enterprise (WSL requires Pro/Enterprise)
- Windows Subsystem for Linux enabled
- Administrator privileges
- Available drive for backup (default: K:)

## 🛠️ Installation

### Option 1: PowerShell Job (Recommended)

```powershell
# Run as Administrator
.\Start-NetworkBusterJob.ps1 -BackupDrive "K:" -DistroName "NetworkBuster"
```

### Option 2: Background Job

```powershell
# Start creation as background job
$job = .\Start-NetworkBusterJob.ps1 -BackupDrive "K:" -AsJob

# Monitor progress
Get-Job -Id $job.Id

# Get results when complete
Receive-Job -Id $job.Id
```

### Option 3: Manual Setup

```bash
# Run the creation script
.\create-networkbuster.sh
```

## 📊 Distribution Information

| Component | Version/Details |
|-----------|----------------|
| Base OS | Ubuntu 22.04 LTS |
| Kernel | WSL2 (Windows integration) |
| Python | 3.10+ with AI/ML packages |
| Node.js | Latest LTS with development packages |
| Docker | 20.10+ with Compose |
| Cloud CLI | Azure CLI + Google Cloud SDK |
| Backup | Automated to K:\networkbuster-backup |

## 🚀 Usage

### Starting NetworkBuster

```batch
# From desktop shortcut
NetworkBuster.bat

# From command line
wsl -d NetworkBuster

# From PowerShell
wsl --distribution NetworkBuster
```

### Manual Backup

```powershell
# Run backup script
.\NetworkBuster-Backup.ps1
```

### Inside NetworkBuster

```bash
# Check version
cat /etc/networkbuster/version

# Run backup manually
sudo /usr/local/bin/networkbuster-backup

# Check system status
htop
docker --version
az --version
gcloud --version
```

## 📁 Directory Structure

```
/opt/networkbuster/          # NetworkBuster specific files
/etc/networkbuster/          # Configuration files
/var/log/networkbuster/      # Log files
/home/networkbuster/         # User home directory
/mnt/backup-drive/           # Backup mount point
```

## 💾 Backup System

### Automatic Backups
- **Schedule**: Daily at 2:00 AM
- **Location**: K:\networkbuster-backup\YYYYMMDD_HHMMSS\
- **Contents**:
  - System configuration
  - User data
  - Installed packages list
  - Log files

### Manual Backups
```bash
# Inside NetworkBuster
sudo /usr/local/bin/networkbuster-backup
```

### Backup Contents
Each backup contains:
- `system-config.tar.gz`: NetworkBuster configuration
- `user-data.tar.gz`: User home directory
- `logs.tar.gz`: System and NetworkBuster logs
- `installed-packages.list`: Package installation list

## 🛡️ Security Features

- **Firewall**: UFW with SSH access
- **Intrusion Prevention**: Fail2Ban configured
- **Automatic Updates**: Unattended security upgrades
- **User Isolation**: Dedicated networkbuster user
- **SSH Hardening**: Key-based authentication recommended

## ☁️ Cloud Integration

### Azure
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Deploy resources
az deployment group create --resource-group myRG --template-file template.json
```

### Google Cloud
```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project your-project-id

# Deploy to Cloud Run
gcloud run deploy --source .
```

## 🐳 Docker Usage

```bash
# Check Docker status
sudo systemctl status docker

# Run containers
docker run -d -p 3000:3000 myapp

# Build images
docker build -t myimage .

# Use with Azure Container Registry
az acr login --name myregistry
docker tag myimage myregistry.azurecr.io/myimage
docker push myregistry.azurecr.io/myimage
```

## 🔧 Development Tools

### Python AI/ML
```bash
# Available packages
pip3 list | grep -E "(tensorflow|torch|scikit|pandas|numpy)"

# Run Jupyter (if installed)
jupyter notebook --ip=0.0.0.0 --port=8888
```

### Node.js Development
```bash
# Check installed packages
npm list -g

# Create new project
mkdir myproject && cd myproject
npm init -y
npm install express socket.io
```

## 📊 Monitoring

### System Monitoring
```bash
# System resources
htop

# Disk usage
df -h

# Network connections
ss -tuln

# Docker containers
docker ps -a
```

### NetworkBuster Logs
```bash
# View logs
tail -f /var/log/networkbuster/*.log

# System logs
journalctl -u networkbuster
```

## 🔄 Updates and Maintenance

### System Updates
```bash
# Update packages
sudo apt update && sudo apt upgrade

# Update Python packages
pip3 install --upgrade -r requirements.txt

# Update Node.js packages
npm update -g
```

### Distribution Updates
```bash
# Export current state
wsl --export NetworkBuster backup.tar

# Import updated version
wsl --import NetworkBuster-new ./backup.tar ./backup.tar

# Switch to new version
wsl --set-default NetworkBuster-new
```

## 🆘 Troubleshooting

### Common Issues

**WSL not starting**
```powershell
# Restart WSL service
Restart-Service LxssManager

# Re-register distribution
wsl --unregister NetworkBuster
wsl --import NetworkBuster ./backup.tar ./backup.tar
```

**Backup drive not accessible**
```bash
# Check mount
ls /mnt/backup-drive

# Remount if needed
sudo mount -t drvfs K: /mnt/backup-drive -o metadata
```

**Docker not working**
```bash
# Restart Docker
sudo systemctl restart docker

# Check status
sudo systemctl status docker
```

### Logs and Diagnostics
```bash
# WSL logs (from Windows)
Get-WinEvent -LogName Microsoft-Windows-WSL/Operational | Select-Object -Last 10

# NetworkBuster logs
tail -f /var/log/networkbuster/*.log

# System logs
dmesg | tail -20
```

## 📈 Performance Optimization

### WSL Configuration
Create/Edit `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true
```

### Docker Performance
```bash
# Use Docker with WSL integration
# Ensure Docker Desktop WSL integration is enabled
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create GitHub issue
- **Documentation**: This README
- **Logs**: Check `/var/log/networkbuster/`
- **WSL Issues**: Microsoft WSL documentation

---

**NetworkBuster** - Your integrated Linux development environment for Windows 🚀