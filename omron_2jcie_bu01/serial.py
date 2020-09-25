# Project: OMRON 2JCIE-BU01
# Module:  omron_2jcie_bu01.serial
import struct
from collections import namedtuple
from serial import Serial
from . import Omron2JCIE_BU01, DataParser

class Omron2JCIE_BU01_Serial(Omron2JCIE_BU01):
    # Operate OMRON 2JCIE-BU01 via serial
    BAUDRATE = 115200
    MAGIC = b"\x52\x42" # Magic Number: b"RB"

    def __init__(self, portname):
        # Connect to serial
        self.conn = Serial(portname, self.BAUDRATE, timeout=1.0)
        self.parser = DataParser()

    def command(self, address, data=b""):
        # Generate command frame
        header = self.MAGIC
        mode = b"\x02" if data else b"\x01"
        payload = mode + struct.pack("<h", address) +data
        cmd = header + struct.pack("<H", len(payload) + 2) + payload
        crc = self.crc16(cmd)
        return cmd + crc

    def write_command(self, address, data=b""):
        # Write command to 2JCIE-BU01
        frame = self.command(address, data)
        self.conn.write(frame)

    def read_response(self):
        # Read response and return data body
        # Read header part(magic+data length)
        header = self.conn.read(4)
        magic, length = struct.unpack("<2sH", header)
        if magic != self.MAGIC: raise IOError("Invalid response.")

        # Read data part(Command+Address+Payload+CRC)
        data = self.conn.read(length)
        cmdtype, address = struct.unpack("<Bh", data[:3])

        # Verify CRC16
        crc = self.crc16(header + data[:-2])
        if crc != data[-2:]: raise ValueError("Response CRC not match.")

        return data[1:-2]

    def get(self, address, data=b"", name=None):
        # Write command, get the response data and parse it
        self.write_command(address, data)
        data = self.read_response()
        return self.parser.parse(data, name)

    def crc16(self, s):
        # Calculate CRC16
        crc = 0xffff
        for c in s:
            crc = crc ^ c
            for n in range(8):
                lsb = crc & 1
                crc = (crc >> 1) & 0x7fff
                if lsb == 1: crc = crc ^ 0xa001
        return struct.pack("<H", crc)

    def latest_data_long(self):
        # 4.4.3 Latest data long (Address: 0x5021)
        return self.get(0x5021)

    def info(self):
        # 4.5.25 Device information (Address: 0x180a)
        nmd = namedtuple("device_info", ["model", "serial", "fw_rev", "hw_rev", "manufacturer"])
        self.write_command(0x180a)
        data = self.read_response()
        return nmd(*[x.decode("utf8") for x in struct.unpack("<10s10s5s5s5s", data[2:])])
