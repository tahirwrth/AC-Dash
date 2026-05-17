#!/bin/bash
sudo systemctl stop emulationstation
sleep 1
sudo sh -c "clear > /dev/tty1"

sudo SDL_NOMOUSE=1 SDL_MOUSEDEV=/dev/null SDL_MOUSEDRV=dummy \
     SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb0 \
     python3 /home/ark/AC-Dash/Scripts/dash_receiver.py

sudo systemctl start emulationstation