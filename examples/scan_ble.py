#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

from envsensor.ble import Omron2JCIE_BU01_BLE

s = Omron2JCIE_BU01_BLE()

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
