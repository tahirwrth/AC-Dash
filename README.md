# AC Dash

## Overview
A Python App for Assetto Corsa providing low latency data transmission to a connected python-capable device for use as a dash screen.

This can also be used locally on the same computer, for example to have the dash on a second display.

Features include displaying speed, gear, RPM, tire pressures, lap time performance delta, and more.
Inspired by minimalist design and GT3 dash screens.

This project has been catered around the use of a connected R36S linux-based gaming device running ArkOS and Emulation Station as a dashboard screen, however it can be simply modified to work on any connected device that can run PyGame.

## Instructions

### Installation & Setup
#### Assetto Corsa Installation
- Download the `Dashboard` folder or clone the repository
- Copy `Dashboard` folder into Assetto Corsa's Python App directory. By default this is `C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\apps\python\`

#### R36S Device Installation & Setup
- Connect device to internet, open terminal with a connected keyboard or connect to device via SSH
- In the terminal, run `curl -sL https://raw.githubusercontent.com/tahirwrth/AC-Dash/main/installES.sh | bash`
- Restart your device

#### Local PC Dash or other device Installation
- Install Python 3.13 or older (tested on 3.12.10)
- Install py-game using `pip install pygame` in terminal
- Download the `Scripts` folder or clone the repository

#### Assetto Corsa Setup
- Open Content Manager
- Navigate to `SETTINGS -> ASSETTO CORSA -> PYTHON APPS` and ensure the `Enable Python Apps` option is ticked
- Navigate to `SETTINGS -> ASSETTO CORSA -> PYTHON APP SETTINGS -> Dashboard` and tick the option next to Dashboard. Edit the `Ip address:` field with the address of your device. If running dash on the same computer, set IP to `127.0.0.1`

### Usage Instructions

#### R36S:
- Power on R36S device and connect to the network using Wi-Fi or USB tethering
- On R36S, navigate to `Ports` and run SimDashboard. If successful, it will display the message "Ready for Assetto"

#### Local PC Dash or other device:
- Run `dash_receiver.py`, it will display the message "Ready for Assetto"

#### PC Assetto Corsa:
- On PC, launch an Assetto Corsa race. In the game, once pressing 'Drive' the dash will appear on the R36S
- To exit the dash, press SELECT to exit back to the Emulation Station menu
