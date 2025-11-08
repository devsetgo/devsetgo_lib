# Node.js and NPX Setup Guide

This guide ensures `npx` is available across all development environments for VS Code extensions like GistPad that require it.

## Overview

The GistPad VS Code extension requires `npx` (Node Package Execute) to run certain Node.js packages. This guide covers setup for:
- DevContainer (already configured)
- WSL (Windows Subsystem for Linux)
- Remote SSH servers

## DevContainer Setup ✅

**Status: Already configured**

Your DevContainer is already set up with:
- Node.js 18 via the `ghcr.io/devcontainers/features/node:1` feature
- GistPad extension (`vsls-contrib.gistfs`) added to auto-install
- `npx` is automatically available with Node.js

## WSL Setup

### Option 1: Using Node Version Manager (Recommended)

```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload your shell or restart terminal
source ~/.bashrc

# Install latest LTS Node.js
nvm install --lts
nvm use --lts
nvm alias default node

# Verify installation
node --version
npm --version
npx --version
```

### Option 2: Using Package Manager

#### Ubuntu/Debian WSL:
```bash
# Update package index
sudo apt update

# Install Node.js and npm
sudo apt install -y nodejs npm

# Verify installation
node --version
npm --version
npx --version
```

#### If you get an older version, use NodeSource repository:
```bash
# Add NodeSource repository for latest Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
npx --version
```

### Option 3: Using Snap (Ubuntu WSL)

```bash
# Install Node.js via snap
sudo snap install node --classic

# Verify installation
node --version
npm --version
npx --version
```

## Remote SSH Setup

### For Ubuntu/Debian Servers:

```bash
# Connect to your remote server
ssh user@your-server

# Install Node.js and npm
sudo apt update
sudo apt install -y nodejs npm

# Or use NodeSource for latest version
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
npx --version
```

### For CentOS/RHEL/Rocky Linux:

```bash
# Using dnf/yum
sudo dnf install -y nodejs epel-release
sudo dnf install -y npm

# Or using NodeSource
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo dnf install -y nodejs

# Verify installation
node --version
npm --version
npx --version
```

### For Alpine Linux:

```bash
# Install Node.js and npm
sudo apk add --update nodejs npm

# Verify installation
node --version
npm --version
npx --version
```

## Automated Setup Scripts

See the `scripts/` directory for automated installation scripts:
- `scripts/setup-nodejs-wsl.sh` - WSL setup script
- `scripts/setup-nodejs-remote.sh` - Remote server setup script

## Verification

After installation on any environment, verify npx works:

```bash
# Check versions
node --version
npm --version
npx --version

# Test npx functionality
npx --help
```

## Troubleshooting

### Common Issues:

1. **`npx: command not found`**
   - Ensure Node.js and npm are properly installed
   - Restart your terminal/VS Code
   - Check if npm's bin directory is in your PATH

2. **Permission errors**
   - Avoid using `sudo` with npm/npx for user packages
   - Configure npm to use a different directory for global packages:
     ```bash
     mkdir ~/.npm-global
     npm config set prefix '~/.npm-global'
     echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
     source ~/.bashrc
     ```

3. **Old Node.js version**
   - Use nvm to manage Node.js versions
   - Or install from NodeSource repository for latest versions

4. **WSL specific issues**
   - Ensure Windows and WSL Node.js installations don't conflict
   - Use WSL-specific Node.js installation, not Windows version

## VS Code Extension Requirements

For GistPad and similar extensions:
- Node.js 14+ (recommended 18+ LTS)
- npm 6+
- npx (included with npm 5.2+)

The extension should automatically detect and use the available `npx` command in your environment.
