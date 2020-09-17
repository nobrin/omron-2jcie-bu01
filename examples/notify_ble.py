#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

from envsensor.ble import Omron2JCIE_BU01_BLE

s = Omron2JCIE_BU01_BLE()

# Notify
def on_notify(sender, tpl):
    print(f"{sender} {tpl}")
s.start_notify(0x5012, on_notify)
s.start_notify(0x5013, on_notify)
s.sleep(5)
s.stop_notify(0x5012)
s.stop_notify(0x5013)
