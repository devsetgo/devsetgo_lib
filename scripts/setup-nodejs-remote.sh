#!/bin/bash

# Node.js and NPX Setup Script for Remote SSH Servers
# This script installs Node.js and npm on remote Linux servers

set -e

echo "🚀 Setting up Node.js and NPX for Remote SSH Server..."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
elif [ -f /etc/redhat-release ]; then
    OS=$(cat /etc/redhat-release | cut -d' ' -f1)
elif [ -f /etc/alpine-release ]; then
    OS="Alpine Linux"
else
    echo "❌ Cannot detect OS. Manual installation may be required."
    exit 1
fi

echo "📋 Detected OS: $OS"

# Function to verify installation
verify_installation() {
    echo "🔍 Verifying installation..."
    node --version
    npm --version
    npx --version
    echo "✅ Node.js, npm, and npx are properly installed!"
}

# Function to install on Ubuntu/Debian
install_ubuntu_debian() {
    echo "📦 Installing Node.js on Ubuntu/Debian..."

    # Update package index
    sudo apt update

    # Install curl if not available
    if ! command -v curl >/dev/null 2>&1; then
        sudo apt install -y curl
    fi

    # Add NodeSource repository for latest Node.js
    echo "🔄 Adding NodeSource repository..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

    # Install Node.js
    sudo apt-get install -y nodejs

    verify_installation
}

# Function to install on CentOS/RHEL/Rocky Linux
install_rhel_based() {
    echo "📦 Installing Node.js on RHEL-based system..."

    # Determine package manager
    if command -v dnf >/dev/null 2>&1; then
        PKG_MGR="dnf"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MGR="yum"
    else
        echo "❌ No suitable package manager found (dnf/yum)"
        exit 1
    fi

    echo "🔧 Using package manager: $PKG_MGR"

    # Install curl if not available
    if ! command -v curl >/dev/null 2>&1; then
        sudo $PKG_MGR install -y curl
    fi

    # Add NodeSource repository
    echo "🔄 Adding NodeSource repository..."
    curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -

    # Install Node.js
    sudo $PKG_MGR install -y nodejs

    verify_installation
}

# Function to install on Alpine Linux
install_alpine() {
    echo "📦 Installing Node.js on Alpine Linux..."

    # Update package index
    sudo apk update

    # Install Node.js and npm
    sudo apk add --update nodejs npm

    verify_installation
}

# Function to install via NVM (fallback)
install_via_nvm() {
    echo "📦 Installing Node.js via NVM (Node Version Manager)..."

    # Install curl if not available
    if ! command -v curl >/dev/null 2>&1; then
        case "$OS" in
            "Ubuntu"*|"Debian"*)
                sudo apt update && sudo apt install -y curl
                ;;
            "CentOS"*|"Red Hat"*|"Rocky"*)
                if command -v dnf >/dev/null 2>&1; then
                    sudo dnf install -y curl
                else
                    sudo yum install -y curl
                fi
                ;;
            "Alpine"*)
                sudo apk add --update curl
                ;;
        esac
    fi

    # Install NVM
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

    # Source NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

    # Install latest LTS Node.js
    nvm install --lts
    nvm use --lts
    nvm alias default node

    # Add to bashrc if not already there
    if ! grep -q "NVM_DIR" ~/.bashrc; then
        echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
        echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
        echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
    fi

    verify_installation
}

# Main installation logic
case "$OS" in
    "Ubuntu"*|"Debian"*)
        install_ubuntu_debian
        ;;
    "CentOS"*|"Red Hat"*|"Rocky"*|"AlmaLinux"*)
        install_rhel_based
        ;;
    "Alpine"*)
        install_alpine
        ;;
    *)
        echo "⚠️  Unsupported OS detected: $OS"
        echo "🔄 Attempting installation via NVM..."
        install_via_nvm
        ;;
esac

echo ""
echo "🎉 Setup complete! Node.js and npx are ready to use."
echo "💡 You may need to restart your terminal or run 'source ~/.bashrc' to use the new installation."
echo "🔧 Test the installation with: npx --version"

# Additional setup for VS Code Server (if detected)
if [ -d "$HOME/.vscode-server" ] || [ -d "$HOME/.vscode-server-insiders" ]; then
    echo ""
    echo "🔍 VS Code Server detected. Node.js is now available for extensions like GistPad."
fi
