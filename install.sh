#!/bin/bash

set -e

echo "==> Detectare distribuție..."

if [ -f /etc/debian_version ]; then
    sudo apt update
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0
elif [ -f /etc/arch-release ]; then
    sudo pacman -S --noconfirm python-gobject webkit2gtk
elif [ -f /etc/fedora-release ]; then
    sudo dnf install -y python3-gobject webkit2gtk4.1
else
    echo "Distribuție nerecunoscută. Instalează manual: python3-gi și webkit2gtk."
    exit 1
fi

echo "==> Instalare dependențe Python..."
pip install -r requirements.txt

echo "==> Instalare simple-linux..."
pip install .

echo ""
echo "✓ Gata! Rulează cu: simple-linux"