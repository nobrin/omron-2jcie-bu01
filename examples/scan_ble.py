#!/usr/bin/env python3
""" NOTE: Bluez 5.50 may not return all every received messages.
    Data seems to be detected every 11 seconds.
    In mode 0x03, ADV_IND and ADV_RSP are not always aligned.
    So, it seems that complete data can only be obtained once in a white.
    The acquisition intervals was between 44 to 374 seconds.
    It seems random...

    Test result on Raspbian GNU/Linux 10 (buster)
    Linux raspberrypi 5.4.51+ #1333 Mon Aug 10 16:38:02 BST 2020 armv6l GNU/Linux
    Package: bluetooth / Version: 5.50-1.2~deb10u1+rpt2
    Python 3.7.3 / Bleak 0.7.1

    $ ./scan_blt.py  (scan 1200 seconds)
    Adv_0x03(type=3, seq=27, temperature=Decimal('27.93'), ...
    Adv_0x03(type=3, seq=13, temperature=Decimal('28.68'), ...
    Adv_0x03(type=3, seq=112, temperature=Decimal('28.83'), ...
    Adv_0x03(type=3, seq=178, temperature=Decimal('28.91'), ...
    Adv_0x03(type=3, seq=222, temperature=Decimal('28.95'), ...
    Adv_0x03(type=3, seq=241, temperature=Decimal('28.87'), ...
    Adv_0x03(type=3, seq=103, temperature=Decimal('29.05'), ...

    Intervals(seconds)
    - 242
    -  99
    -  66
    -  44
    - 275
    - 374

    If you need scan on Linux, consider notify method.
    ---
    On Windows, data can be detected at intervals of 1 second or less.
    And complete data will be obtained about every 1 second.
"""
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

from omron_2jcie_bu01 import Omron2JCIE_BU01

#s = Omron2JCIE_BU01.ble("AA:BB:CC:DD:EE:FF")
s = Omron2JCIE_BU01.ble()

# Scan
def on_scan(data):
    print(data)

# Set Advertising mode: 0x03 (Active scan)
# The setting is retained even when the power is turned off the device.
s.advertise_setting(mode=0x03)

# Scanning needs to disconnect
# If connected, advertising packets will not be detected.
s.disconnect()

s.scan(on_scan, scantime=10, active=True)

# Mode: 0x01 (Passive scan)
#s.advertise_setting(mode=0x01)
#s.disconnect()
#s.scan(on_scan, scantime=10)
