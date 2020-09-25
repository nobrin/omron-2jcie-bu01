# Project: OMRON 2JCIE-BU01
# Module:  omron_2jcie_bu01.__init__
"""
Module and sample code for obtaining data with OMRON 2JCIE-BU01 Environment
Sensor by Python. The codes work with Python 3.6 and above. This module supports
USB serial communication and BLE. This module depends on pySerial(serial
communication) and Bleak(BLE).

Example::

    # Obtain sensing data via serial communication
    from omron_2jcie_bu01 import Omron2JCIE_BU01
    sensor = Omron2JCIE_BU01.serial("/dev/ttyUSB0") # Linux
    sensor = Omron2JCIE_BU01.serial("COM5")         # Windows
    devinfo = sensor.info()
    data = sensor.latest_data_long()

    # Obtain sensing data via BLE communication
    # Read latest data with connection
    from omron_2jcie_bu01 import Omron2JCIE_BU01
    sensor = Omron2JCIE_BU01.ble("AA:BB:CC:DD:EE:FF")
    data1 = sensor.latest_sensing_data()
    data2 = sensor.latest_calculation_data()

    # Read latest data by scan
    def on_scan(data):
        print("SCAN", data)

    # Advertising mode: 0x01 (Passive)
    sensor.scan(on_scan, scantime=3)

    # Advertising mode: 0x03 (Active)
    sensor.scan(on_scan, scantime=3, active=True)

    # Notify sensing data
    def on_notify(sender, tpl):
        print(f"{sender} {tpl}")

    sensor.start_notify(0x5012, on_notify)
    sensor.start_notify(0x5013, on_notify)
    sensor.sleep(5)
    sensor.stop_notify(0x5012)
    sensor.stop_notify(0x5013)
"""

import struct
from collections import namedtuple
from decimal import Decimal

__author__  = "Nobuo Okazaki"
__version__ = "0.1.0"
__license__ = "MIT License"

class Omron2JCIE_BU01(object):
    # Base class for Serial/BLE implementation

    # Description for Vibration Information
    VI = ["NONE", "During vibration (Earthquake judgment in progress)", "During earthquake"]

    @classmethod
    def serial(cls, portname):
        from .serial import Omron2JCIE_BU01_Serial
        return Omron2JCIE_BU01_Serial(portname)

    @classmethod
    def ble(cls, device_address=None):
        from .ble import Omron2JCIE_BU01_BLE
        return Omron2JCIE_BU01_BLE(device_address)

    def get(self, address, data=b"", name=None):
        # Write command, get the response data and parse it
        raise NotImplementedError()

    def vibration_count(self):
        # 4.5.7 Vibration count (Address: 0x5031)
        return self.get(0x5031)

    def led(self, rule=None, rgb=None):
        # 4.5.8 LED setting [normal state] (Address: 0x5111)
        # Get/Set LED setting
        # - rule: Display rule -- See Table 105
        # - rgb:  Intensity of LED(RGB) -- tuple(red, green, blue)
        cur = self.get(0x5111)
        if not rule and not rgb: return cur
        if rule is None: rule = cur.rule
        if rgb: red, green, blue = rgb
        else: red, green, blue = cur.red, cur.green, cur.blue
        data = struct.pack("<HBBB", rule, red, green, blue)
        return self.get(0x5111, data)

    def advertise_setting(self, interval=None, mode=None):
        # 4.5.12 Advertise setting (Address: 0x5115)
        # Get/Set Advertise setting
        # - intarval: Advertising interval, unit 0.625ms
        # - mode:     Advertising mode, See Table 109
        cur = self.get(0x5115)
        if not interval and not mode: return cur
        if interval is None: interval = cur.interval
        if mode is None: mode = cur.mode
        data = struct.pack("<HB", interval, mode)
        return self.get(0x5115, data)

class DataParser(object):
    # Parser for data body
    # Common for Serial/BLE
    TYPE = {
        "UInt8" : "B",  # unsigned short
        "UInt16": "H",  # unsigned int
        "SInt16": "h",  # int
        "UInt32": "L",  # unsigned long
        "SInt32": "l",  # long
    }

    # Field definition
    # tuple(name, description, datatype, unitsize(inverse), unit)
    ADV_TYPE = [("type", "Data Type", "UInt8", 1, "")]
    SEQ = [("seq", "Sequence number", "UInt8", 1, "")]

    SENSING = [
        ("temperature",         "Temperature",           "SInt16", 100,  "degC"),
        ("humidity",            "Relative humidity",     "SInt16", 100,  "%RH"),
        ("light",               "Ambient light",         "SInt16", 1,    "lx"),
        ("pressure",            "Barometric pressure",   "SInt32", 1000, "hPa"),
        ("noise",               "Sound noise",           "SInt16", 100,  "dB"),
        ("eTVOC",               "eTVOC",                 "SInt16", 1,    "ppb"),
        ("eCO2",                "eCO2",                  "SInt16", 1,    "ppm"),
    ]

    CALCULATION = [
        ("thi",                 "Discomfort index; THI", "SInt16", 100,  ""),
        ("wbgt",                "Heat stroke; WBGT",     "SInt16", 100,  "degC"),
        ("vibration",           "Vibration information", "UInt8",  1,    ""),
        ("si",                  "SI value",              "UInt16", 10,   "kine"),
        ("pga",                 "PGA",                   "UInt16", 10,   "gal"),
        ("seismic_intensity",   "Seismic intensity",     "UInt16", 1000, ""),
    ]

    ACCELERATION = [
        ("acc_x",               "Acceleration (X-axis)", "SInt16", 10,   "gal"),
        ("acc_y",               "Acceleration (Y-axis)", "SInt16", 10,   "gal"),
        ("acc_z",               "Acceleration (Z-axis)", "SInt16", 10,   "gal"),
    ]

    SENSING_FLAGS = [
        ("f_temperature",       "Temperature flag",           "UInt16", 1, ""),
        ("f_humidity",          "Relative humidity flag",     "UInt16", 1, ""),
        ("f_light",             "Ambient light flag",         "UInt16", 1, ""),
        ("f_pressure",          "Barometric pressure flag",   "UInt16", 1, ""),
        ("f_noise",             "Sound noise flag",           "UInt16", 1, ""),
        ("f_eTVOC",             "eTVOC flag",                 "UInt16", 1, ""),
        ("f_eCO2",              "eCO2 flag",                  "UInt16", 1, ""),
    ]

    CALCULATION_FLAGS = [
        ("f_thi",               "Discomfort index flag; THI", "UInt16", 1, ""),
        ("f_wbgt",              "Heat stroke flag; WBGT",     "UInt16", 1, ""),
        ("f_si",                "SI value flag",              "UInt8",  1, ""),
        ("f_pga",               "PGA flag",                   "UInt8",  1, ""),
        ("f_seismic_intensity", "Seismic intensity flag",     "UInt8",  1, ""),
    ]

    # For advatising packets
    # - Key: Data Type
    # - Value: Fields ("ind" for ADV_IND, "rsp" for ADV_RSP)
    ADV = {
        0x01: ADV_TYPE + SEQ + SENSING + [("_reserved", 1)],
        0x03: {
            "ind": ADV_TYPE + SEQ + SENSING + [("_reserved", 1)],
            "rsp": ADV_TYPE + SEQ + CALCULATION + ACCELERATION + [("_reserved", 8)],
        },
    }

    # For communication packets
    # - Key: Address
    # - Value: Fields
    FIELDS = {
        0x5012: SEQ + SENSING,
        0x5013: SEQ + CALCULATION + ACCELERATION,
        0x5021: SEQ + SENSING + CALCULATION + SENSING_FLAGS + CALCULATION_FLAGS,
        0x5031: [
            ("earthquake",      "Earthquake count",      "UInt32", 1, ""),
            ("vibration",       "Vibration count",       "UInt32", 1, ""),
        ],
        0x5111: [
            ("rule",            "Display rule (normal state)", "UInt16", 1, ""),
            ("red",             "Intensity of LED (Red)",      "UInt8",  1, ""),
            ("green",           "Intensity of LED (Green)",    "UInt8",  1, ""),
            ("blue",            "Intensity of LED (Blue)",     "UInt8",  1, ""),
        ],
        0x5115: [
            ("interval",        "Advertising interval",        "UInt16", 1, ""),
            ("mode",            "Advertising mode",            "UInt8",  1, ""),
        ],
    }

    TPLNAME = {
#        0x01:   "scan_passive",
#        0x03:   "scan_active",
        0x5012: "latest_sensing_data",
        0x5013: "latest_calculation_data",
        0x5021: "latest_data_long",
        0x5031: "vibration_count",
        0x5111: "led_setting",
        0x5115: "advertise_setting",
    }

    @classmethod
    def generate_struct_format(cls, fields):
        # Generate format for struct.unpack from fields
        fmt = "<"
        for fld in fields:
            if fld[0] == "_reserved": fmt += f"{fld[1]}x"
            else: fmt += cls.TYPE[fld[2]]
        return fmt

    def _parse_content(self, data, fields, tplname):
        # Parse main data
        fmt = self.generate_struct_format(fields)
        a = list(struct.unpack(fmt, data))
        for idx in range(len(fields)):
            fld = fields[idx]
            if fld[0] != "_reserved" and fld[3] != 1:
                a[idx] = Decimal(a[idx]) / fld[3]
        names = [f[0] for f in filter(lambda x: not x[0].startswith("_"), fields)]
        nmd = namedtuple(tplname, names)
        return nmd(*a)

    def parse(self, data, tplname=None):
        # Parse for communication data
        address = struct.unpack("<H", data[:2])[0]
        if address not in self.FIELDS: return data
        tplname = tplname or self.TPLNAME.get(address, f"Address_0x{address:04x}")
        return self._parse_content(data[2:], self.FIELDS[address], tplname)

    def parse_adv(self, data, tplname=None):
        # Parse for advertising data
        datatype = data[0]
        if datatype not in self.ADV: return data

        if datatype in (0x03, 0x04):
            if len(data) == 19: pk = "ind"
            elif len(data) == 27: pk = "rsp"
            tplname = tplname or f"Adv_0x{datatype:02x}{pk}"
            return self._parse_content(data, self.ADV[datatype][pk], tplname)

        tplname = tplname or self.TPLNAME.get(datatype, f"Adv_0x{datatype:02x}")
        return self._parse_content(data, self.ADV[datatype], tplname)

    def get_adv_namedtuple(self, datatype, name=None):
        # Create named tuple for special use
        if datatype == 0x03:
            fields = self.ADV_TYPE + self.SEQ + self.SENSING + self.CALCULATION + self.ACCELERATION
        names = [fld[0] for fld in fields]
        tplname = name or self.TPLNAME.get(datatype, f"Adv_0x{datatype:02x}")
        return namedtuple(tplname, names)
