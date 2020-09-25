#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

import time
from datetime import datetime, timedelta, tzinfo
from omron_2jcie_bu01 import Omron2JCIE_BU01

CurrentTZ = type(time.tzname[0], (tzinfo,), {
    "tzname": lambda self, dt: time.tzname[0],
    "utcoffset": lambda self, dt: timedelta(seconds=-time.timezone),
    "dst": lambda self, dt: timedelta(seconds=time.timezone - time.altzone),
})()

#s = Omron2JCIE_BU01.serial("/dev/ttyUSB0")
s = Omron2JCIE_BU01.serial("COM3")
dev = s.info()
info = s.latest_data_long()
dt = datetime.now(CurrentTZ)

print("================================================")
print(f" Model               : {dev.model}")
print(f" Serial              : {dev.serial}")
print(f" Firmware rev.       : {dev.fw_rev}")
print(f" Hardware rev.       : {dev.hw_rev}")
print(f" Manufacture         : {dev.manufacturer}")
print("------------------------------------------------")
print(f" Date                : {dt.strftime('%Y-%m-%d %H:%M:%S%z')}")
print(f" Sequence Number     : {info.seq}")
print(f" Temperature         : {info.temperature} degC")
print(f" Relative humidity   : {info.humidity} %RH")
print(f" Ambient light       : {info.light} lx")
print(f" Barometric pressure : {info.pressure} hPa")
print(f" Sound noise         : {info.noise} dB")
print(f" eTVOC               : {info.eTVOC} ppb")
print(f" eCO2                : {info.eCO2} ppm")
print(f" Discomfort index    : {info.thi}")
print(f" Heat stroke         : {info.wbgt} degC")
print(f" Vibration info      : {s.VI[info.vibration]}")
print(f" SI value            : {info.si} kine")
print(f" PGA                 : {info.pga} gal")
print(f" Seismic intensity   : {info.seismic_intensity}")
print("================================================")
