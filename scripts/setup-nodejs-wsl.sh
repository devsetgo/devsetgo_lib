#!/bin/bash

# Node.js and NPX Setup Script for WSL
# This script installs Node.js and npm in WSL environments

set -e

echo "🚀 Setting up Node.js and NPX for WSL..."

# Detect WSL distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Cannot detect OS. This script is for WSL environments."
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

# Function to install via NVM (recommended)
install_via_nvm() {
    echo "📦 Installing Node.js via NVM (Node Version Manager)..."

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

# Function to install via package manager
install_via_package_manager() {
    case "$OS" in
        "Ubuntu"*)
            echo "📦 Installing Node.js via apt package manager..."
            sudo apt update

            # Check if NodeSource repository should be added
            echo "🔄 Adding NodeSource repository for latest Node.js..."
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "Debian"*)
            echo "📦 Installing Node.js via apt package manager..."
            sudo apt update
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        *)
            echo "❌ Unsupported OS for package manager installation: $OS"
            echo "🔄 Falling back to NVM installation..."
            install_via_nvm
            return
            ;;
    esac

    verify_installation
}

# Main installation logic
echo "🤔 Choose installation method:"
echo "1) NVM (Node Version Manager) - Recommended"
echo "2) Package Manager (apt)"
echo "3) Auto-detect best method"

read -p "Enter your choice (1-3) [default: 3]: " choice
choice=${choice:-3}

case $choice in
    1)
        install_via_nvm
        ;;
    2)
        install_via_package_manager
        ;;
    3)
        # Auto-detect: prefer NVM if curl is available
        if command -v curl >/dev/null 2>&1; then
            echo "🎯 Auto-detected: Using NVM (recommended)"
            install_via_nvm
        else
            echo "🎯 Auto-detected: Using package manager"
            install_via_package_manager
        fi
        ;;
    *)
        echo "❌ Invalid choice. Using auto-detect."
        if command -v curl >/dev/null 2>&1; then
            install_via_nvm
        else
            install_via_package_manager
        fi
        ;;
esac

echo ""
echo "🎉 Setup complete! Node.js and npx are ready to use."
echo "💡 You may need to restart your terminal or run 'source ~/.bashrc' to use the new installation."
echo "🔧 Test the installation with: npx --version"
