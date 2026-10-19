# Memvid Installer

Official installer for Memvid (v1).

## What it does

The installer automatically checks for and installs required dependencies, then installs Memvid globally:

- **System dependencies** (Linux only):
  - **ca-certificates** - SSL certificate bundle
  - **curl** - Command-line tool for downloading files
  - **openssl** or **libssl3** - SSL/TLS library
- **git** - Version control system
- **node** (LTS) - JavaScript runtime
- **npm** - Package manager (comes with node)
- **memvid** - Installed globally via `npm install -g memvid-cli@latest`

The installer only installs missing tools (no upgrades in v1). If a tool is already installed, it will be detected and skipped.

**Important notes:**
- On macOS, if Xcode Command Line Tools are missing, the installer will prompt you to install them and then exit. You'll need to complete the Xcode installation and run the installer again.
- The installer will show you what will be installed and ask for confirmation before proceeding.
- On Linux, Node.js LTS is installed via the NodeSource repository for Debian/Ubuntu and RHEL-based distributions to ensure you get the latest LTS version.

## Prerequisites

- **macOS**: 
  - Homebrew must be installed (the installer will check and exit if missing)
  - Xcode Command Line Tools (installer will prompt to install if missing)
- **Linux**: 
  - `sudo` access (required for package installation, except Alpine which may use `su`)
  - One of the supported package managers (apt, dnf, pacman, or apk)
- **Windows**: 
  - winget (Windows Package Manager) - comes with Windows 11, or install from https://aka.ms/getwinget

## Supported Platforms

- **macOS** - Uses Homebrew (requires Xcode Command Line Tools)
- **Linux** - Multiple distributions supported:
  - **Debian/Ubuntu** - Uses apt (Node.js installed via NodeSource repository)
  - **Fedora/RHEL/CentOS/Rocky/AlmaLinux** - Uses dnf (Node.js installed via NodeSource repository)
  - **Arch/Manjaro** - Uses pacman
  - **Alpine** - Uses apk
- **Windows** - Requires winget (Windows Package Manager)

## Installation

### macOS / Linux

**Quick install** (recommended):
```bash
curl -fsSL https://raw.githubusercontent.com/memvid/memvid/main/install/install.sh | bash
```

**Download and run locally**:
```bash
curl -fsSL https://raw.githubusercontent.com/memvid/memvid/main/install/install.sh -o install.sh
chmod +x install.sh
./install.sh
```

**Non-interactive mode** (for CI/CD):
The installer can run without user interaction when piped via `curl | bash`. It will proceed automatically if no terminal is detected.

### Windows

Open PowerShell and run:

```powershell
irm https://raw.githubusercontent.com/memvid/memvid/main/install/install.ps1 | iex
```

Or download and run:

```powershell
.\install.ps1
```

## Security

These scripts are open source and readable. Before running, you can:

1. Review the script contents on GitHub
2. Download and inspect locally
3. Run with appropriate permissions

The installer will:
- Show what will be installed before proceeding
- Ask for confirmation before installing anything
- Use only system package managers (no third-party installers)
- Print clear status messages for each step

## Verification

After installation, verify it worked:

```bash
memvid --version
```

## Troubleshooting

If installation fails:

1. **macOS**:
   - Ensure Homebrew is installed: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
   - If Xcode CLI Tools installation was prompted, complete it and run the installer again
   - If `node` command is not found after installation, you may need to restart your terminal or source your shell config file

2. **Linux**:
   - Check that you have `sudo` access (or run as root on Alpine)
   - Ensure your package manager is up to date (`sudo apt-get update`, `sudo dnf check-update`, etc.)
   - If Node.js installation fails, check that curl and ca-certificates are installed
   - Verify npm global bin directory is in your PATH: `npm config get prefix`

3. **Windows**:
   - Ensure winget is installed (comes with Windows 11, or install from https://aka.ms/getwinget)
   - Run PowerShell as Administrator if needed

4. **General**:
   - Check that npm global bin directory is in your PATH: `npm list -g memvid-cli`
   - Try running `memvid --version` to verify installation
   - On Linux, you may need to use `sudo` for global npm installs

For issues, please open an issue on GitHub.
