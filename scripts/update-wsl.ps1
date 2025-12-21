<#
.SYNOPSIS
  Update packages in WSL distros from Windows (PowerShell script).

.DESCRIPTION
  This script enumerates available WSL distros and runs apt update/full-upgrade/autoremove inside each.
  Run from an elevated PowerShell prompt.

.PARAMETER Distro
  Optional specific distro name. If omitted, all installed distros will be updated.

.EXAMPLE
  .\scripts\update-wsl.ps1
  Updates all WSL distros.

  .\scripts\update-wsl.ps1 -Distro ubuntu
  Updates only the 'ubuntu' distro.
#>
[CmdletBinding()]
param(
  [string]$Distro,
  [switch]$DryRun
)

function Run-UpdateInDistro {
  param($name)
  Write-Host "==> Updating distro: $name" -ForegroundColor Cyan
  if ($DryRun) {
    Write-Host "Dry-run: wsl -d $name -- bash -lc 'sudo apt update && sudo apt full-upgrade -y && sudo apt autoremove -y'"
    return
  }

  $cmd = "sudo apt update && sudo apt full-upgrade -y && sudo apt autoremove -y"
  try {
    wsl -d $name -- bash -lc "$cmd"
    Write-Host "Finished update for $name" -ForegroundColor Green
  } catch {
    Write-Host "Update failed for $name: $_" -ForegroundColor Red
  }
}

# Ensure wsl is available
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
  Write-Error "WSL is not available on this system. Install WSL or run updates inside your distro directly."
  exit 1
}

if ($Distro) {
  # Update single distro
  Run-UpdateInDistro -name $Distro
  exit 0
}

# Get list of distros
$distroList = wsl -l -q 2>$null | Where-Object { $_ -ne '' }
if (-not $distroList) {
  Write-Host "No WSL distros found." -ForegroundColor Yellow
  exit 0
}

Write-Host "Found distros: $($distroList -join ', ')" -ForegroundColor Cyan
foreach ($d in $distroList) {
  Run-UpdateInDistro -name $d
}

Write-Host "All WSL updates attempted." -ForegroundColor Green
