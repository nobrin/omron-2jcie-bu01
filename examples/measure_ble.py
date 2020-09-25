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

#s = Omron2JCIE_BU01.ble("AA:BB:CC:DD:EE:FF")
s = Omron2JCIE_BU01.ble()
data1 = s.latest_sensing_data()
data2 = s.latest_calculation_data()
dt = datetime.now(CurrentTZ)

print("================================================")
print(f" Date                : {dt.strftime('%Y-%m-%d %H:%M:%S%z')}")
print(f" Sequence Number     : {data1.seq}")
print(f" Temperature         : {data1.temperature} degC")
print(f" Relative humidity   : {data1.humidity} %RH")
print(f" Ambient light       : {data1.light} lx")
print(f" Barometric pressure : {data1.pressure} hPa")
print(f" Sound noise         : {data1.noise} dB")
print(f" eTVOC               : {data1.eTVOC} ppb")
print(f" eCO2                : {data1.eCO2} ppm")
print(f" Discomfort index    : {data2.thi}")
print(f" Heat stroke         : {data2.wbgt} degC")
print(f" Vibration info      : {s.VI[data2.vibration]}")
print(f" SI value            : {data2.si} kine")
print(f" PGA                 : {data2.pga} gal")
print(f" Seismic intensity   : {data2.seismic_intensity}")
print("================================================")
