# WSL Update Scripts

This folder contains helper scripts to update WSL distributions.

Files:
- `update-wsl.ps1` — PowerShell host script that enumerates WSL distros and runs `apt update && apt full-upgrade -y && apt autoremove -y` inside each. Run from an elevated PowerShell session.
- `update-wsl.sh` — Minimal shell script intended to be run *inside* a WSL distro (e.g., `bash update-wsl.sh`).

Usage (PowerShell host):
- Elevate PowerShell (Run as Administrator)
- Update all distros: `.	ools\update-wsl.ps1` (or `.	ools\update-wsl.ps1 -DryRun` to see commands)
- Update a single distro: `.	ools\update-wsl.ps1 -Distro ubuntu`

Usage (inside WSL):
- `chmod +x scripts/update-wsl.sh && ./scripts/update-wsl.sh`

Safety notes:
- These scripts use `sudo` inside WSL; you'll be prompted for the distro user's password if required.
- Review and run manually if you need more control over upgrades or reboots.
