import os
import sys
import ac
import acsys
import configparser
import platform
import json

# library setup
path_to_app = os.path.dirname(__file__)
if path_to_app not in sys.path:
    sys.path.insert(0, path_to_app)

sysdir = os.path.join(path_to_app, 'stdlib64' if platform.architecture()[0] == '64bit' else 'stdlib')
sys.path.insert(0, sysdir)
os.environ['PATH'] += ';.'
import ctypes
import socket

try:
    from sim_info import info
except ImportError:
    info = None

# global settings
PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_to_dash(ip, speed, gear, rpm, max_rpm, pressures, temps, max_slip, pit_lim, delta):
    try:
        message = json.dumps({
            "speed": speed, 
            "gear": gear,
            "rpm": rpm,
            "max_rpm": max_rpm,
            "p": pressures,
            "t": temps,
            "slip": max_slip,
            "pl": pit_lim,
            "d": delta
        })
        sock.sendto(message.encode(), (ip, PORT))
    except:
        pass

def acMain(ac_version):
    appWindow = ac.newApp("Dashboard")
    ac.setSize(appWindow, 200, 60)
        
    return "Dashboard"

def acUpdate(deltaT):
    global ser, peak_speed, last_car, timer
    
    speed = ac.getCarState(0, acsys.CS.SpeedMPH)
    gear_num = ac.getCarState(0, acsys.CS.Gear)
    rpm = ac.getCarState(0, acsys.CS.RPM)

    if info:
        max_rpm = info.static.maxRpm
        p_raw = info.physics.wheelsPressure 
        t_raw = info.physics.tyreCoreTemperature
        delta = info.physics.performanceMeter
        slips = info.physics.wheelSlip
        max_slip = max(slips)
        is_pit_limiter = info.physics.pitLimiterOn

        pressures = [round(p_raw[i], 1) for i in range(4)]
        temps = [int(t_raw[i]) for i in range(4)]
    else:
        # defaults
        max_rpm = 7500
        max_slip = 0
        is_pit_limiter = 0
        pressures = [0.0] * 4
        temps = [0] * 4

    # gear number mapping
    gears_map = ["R", "N", "1", "2", "3", "4", "5", "6", "7", "8"]
    gear_str = gears_map[gear_num] if gear_num < len(gears_map) else str(gear_num - 1)

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), "settings.ini"))

    # send data to device with target IP specified in Content Manager
    ip = config.get("Settings", "IP_ADDRESS", fallback = "127.0.0.0")
    send_to_dash(ip, int(speed), gear_str, int(rpm), int(max_rpm), pressures, temps, max_slip, is_pit_limiter, delta)

def acShutdown():
    global ser
    if ser:
        ser.close()