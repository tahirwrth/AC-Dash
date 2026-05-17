#!/bin/bash

REPO_RAW="https://github.com/tahirwrth/AC-Dash"
INSTALL_DIR="/home/ark/AC-Dash"
PORT_LINK="/roms/ports/SimDashboard.sh"

echo "R36S Sim Dashboard Installer by wrth"
echo "--------------------------------"

echo "Installing system dependencies..."
sudo apt update && sudo apt install -y python3-pygame git

echo "Preparing directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d ".git" ]; then
    git init
    git remote add -f origin "$REPO_RAW.git"
    git config core.sparseCheckout true
    echo "Scripts" >> .git/info/sparse-checkout
fi

echo "Fetching latest dashboard scripts..."
git pull --depth=1 origin main

echo "Finalising installation..."
sudo chmod +x "$INSTALL_DIR/Scripts/"*.sh

ln -sf "$INSTALL_DIR/Scripts/SimDashboard.sh" "$PORT_LINK"

echo "--------------------------------"
echo "Success"
echo "You can now find SimDashboard in your PORTS menu."
echo "Your IP for Assetto Corsa: $(hostname -I | awk '{print $1}')"