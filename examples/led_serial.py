#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

from omron_2jcie_bu01.serial import Omron2JCIE_BU01_Serial

s = Omron2JCIE_BU01_Serial("COM3")
#s = Omron2JCIE_BU01_Serial("/dev/ttyUSB0")

# Show current setting
print(s.led())

# rule=0x06 (noise)
# rgb=(0, 255, 200)
s.led(0x06, (0, 255, 200))
