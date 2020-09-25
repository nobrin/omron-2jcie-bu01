# Project: OMRON 2JCIE-BU01
# Module:  omron_2jcie_bu01.ble
import asyncio
import struct
import traceback, platform
from warnings import warn
from bleak import BleakClient, BleakScanner, discover
from . import Omron2JCIE_BU01, DataParser

# Exceptions for skipping packets
class SkipData(Exception): pass
class NotTarget(SkipData): pass
class NoManufacturerData(SkipData): pass

class Omron2JCIE_BU01_BLE(Omron2JCIE_BU01):
    # Operate OMRON 2JCIE-BU01 via BLE
    BASEUUID = "ab70{addr:04x}-0a3a-11e8-ba89-0ed5f89f718b"

    def __init__(self, device_address=None):
        # If device_address is not specified, discover devices and set address
        self.loop = asyncio.get_event_loop()
        if device_address:
            self.address = device_address
        else:
            async def _discover_devices():
                for dev in await discover():
                    if dev.name == "Rbt": return dev.address
            self.address = self.loop.run_until_complete(_discover_devices())

        if not self.address:
            raise RuntimeError("Device address could not be determined.")

        self.seq = {}           # for Active scan
        self.parser = DataParser()
        self.last_seqno = None  # for distinct in scan

        # Initialize wrapper for coroutine
        class _BleakClientWrapper(object):
            # Wrapper class for async coroutine of BleakClient
            def __init__(self, address, loop):
                self._bleak_client = BleakClient(address)
                self.loop = loop

            def __getattr__(self, name):
                func = getattr(self._bleak_client, name)
                def _wrapper(*args, **kw):
                    return self.loop.run_until_complete(func(*args, **kw))
                return _wrapper

        self.client = _BleakClientWrapper(self.address, self.loop)

    @classmethod
    def uuid(cls, characteristic_address):
        # Service UUID
        return cls.BASEUUID.format(addr=characteristic_address)

    def _detection_callback(self, sender, eventargs, distinct):
        """ Callback for detection
            BleakScanner.parse_eventargs returns
            Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementReceivedEventArgs
            - address  -- peripheral address
            - details  -- BluetoothLEAdvertisementReceivedEventArgs
            - metadata -- {"uuid": [], "manufacturer_data": {}}
            - name     -- "Rbt"
            - rssi     -- Received Signal Strength Indicator (dBm)
        """
        try:
            ev = BleakScanner.parse_eventargs(eventargs)
            if ev.address.upper() != self.address.upper(): raise NotTarget(ev.address)

            data = ev.metadata["manufacturer_data"].get(725)
            if not data: raise NoManufacturerData()

            return self._parse_advertisement(data, distinct)
        except SkipData:
            # This data will not pass the callback
            raise
        except Exception as e:
            traceback.print_exc()

    def _detection_callback_Linux(self, scanner, msg, callback, distinct):
        # Callback for detection on Linux
        # - scanner -- BleakScanner object
        # - msg -- txdbus.message.SignalMessage
        #
        # NOTE: Bluez may not return all every received messages.
        for path, dev in scanner._devices.items():
            # Check address of advertised device
            target_path = None
            if dev["Address"] == self.address:
                target_path = path
                break

        # Received message does not match address
        if not target_path or msg.path != target_path: return

        if msg.member == "PropertiesChanged":
            iface, changed, invalidated = msg.body
            data = changed.get("ManufacturerData", {}).get(725)
            if data is None: return

            data = struct.pack(f"{len(data)}B", *data)
            try: res = self._parse_advertisement(data, distinct)
            except SkipData: pass
            except Exception as e: traceback.print_ext()
            else:
                try: callback(res)
                except Exception as e: traceback.print_exc()

    def _parse_advertisement(self, data, distinct):
        datatype, seqno = data[0], data[1]
        if datatype in (0x03, 0x04):
            # For active scan
            if len(data) == 19 and seqno not in self.seq:
                # Parse ADV_IND
                if distinct and seqno == self.last_seqno: raise NotTarget()
                self.last_seqno = seqno
                self.seq[seqno] = self.parser.parse_adv(data)
                raise NotTarget()   # Will proceed ADV_RSP

            if len(data) == 27 and seqno in self.seq:
                # Parse ADV_RSP
                # Add fields to ADV_IND
                a = self.parser.parse_adv(data)
                dct = self.seq.pop(seqno)._asdict()
                dct.update(a._asdict())
                return self.parser.get_adv_namedtuple(datatype)(**dct)
            raise NotTarget()
        # For passive scan
        if distinct and seqno == self.last_seqno: raise NotTarget()
        self.last_seqno = seqno
        return self.parser.parse_adv(data)

    def scan(self, callback, scantime=10, active=False, distinct=True):
        # Scan advertising packet
        # active   -- active scan (for 0x03, 0x04)
        # distinct -- exclude same sequence number
        async def _scan(loop):
            # Wrapped function for detection_callback
            def _wrapped(sender, eventargs):
                try:
                    res = self._detection_callback(sender, eventargs, distinct)
                except SkipData:
                    pass
                else:
                    try: callback(res)
                    except Exception as e: traceback.print_exc()

            def _wrapped_Linux(scanner):
                def _wrapped(msg):
                    self._detection_callback_Linux(scanner, msg, callback, distinct)
                return _wrapped

            # Scan rsp can be obtained with active scan
            if active: kw = {}                          # Active scan (for 0x03, 0x04)
            else: kw = {"scanning_mode": "passive"}     # Passive scan(default)
            async with BleakScanner(loop=loop, **kw) as scanner:
                if platform.system() == "Linux":
                    # NOTE: Bluez 5.50 may not return all every received messages.
                    # Data seems to be detected every 11 seconds.
                    # In mode 0x03, ADV_IND and ADV_RSP are not always aligned.
                    # So, it seems that complete data can only be obtained once in a white.
                    # Ex. The acquisition intervals was between 44 to 374 seconds.
                    # It seems random...
                    scanner.register_detection_callback(_wrapped_Linux(scanner))
                else:
                    # On Windows, data can be detected at intervals of 1 second or less.
                    # And complete data will be obtained about every 1 second.
                    scanner.register_detection_callback(_wrapped)
                await asyncio.sleep(scantime)

        if self.is_connected():
            warn("BLE is connected, scan() may not detect advertising packets.", stacklevel=2)
        self.loop.run_until_complete(_scan(self.loop))

    def connect(self):
        # Connect to device
        self.client.connect()

    def disconnect(self):
        # Disconnect from device
        self.client.disconnect()

    def is_connected(self):
        # Is connected
        if platform.system() == "Linux":
            # In Bleak 0.7.1 on Linux, client.is_connected() is called before connect(),
            # None value of client._bus causes raising AttributeError.
            # Checking BleakClientBlueZDBus._bus will avoids the exception.
            if self.client._bleak_client._bus is None: return False

        return self.client.is_connected()

    def get(self, chara, data=b"", name=None):
        # If not connected, connect first
        if not self.is_connected(): self.connect()
        if data:
            if isinstance(data, bytes): data = bytearray(data)
            return self.client.write_gatt_char(self.uuid(chara), data)
        res = self.client.read_gatt_char(self.uuid(chara))
        return self.parser.parse(struct.pack("<H", chara) + res, name)

    def latest_sensing_data(self):
        # 2.2 Latest Data Service (Service UUID: 0x5010)
        # 0x5012: Latest sensing data
        return self.get(0x5012)

    def latest_calculation_data(self):
        # 2.2 Latest Data Service (Service UUID: 0x5010)
        # 0x5013: Latest calculation data
        return self.get(0x5013)

    def start_notify(self, chara, callback):
        """ Activate notifications on a characteristic

                def callback(sender, tpl):
                    print(f"{sender} {tpl}")
                sensor.start_notify(0x5012, callback)
                sensor.start_notify(0x5013, callback)
                sensor.sleep(5)
                sensor.stop_notify(0x5012)
                sensor.stop_notify(0x5013)
        """
        # If not connected, connect first
        if not self.is_connected(): self.connect()

        def _on_notify(sender, data):
            # Callback for notify
            tpl = self.parser.parse(struct.pack("<H", chara) + data)
            try: callback(sender, tpl)
            except Exception as e: traceback.print_exc()

        self.client.start_notify(self.uuid(chara), _on_notify)

    def stop_notify(self, chara):
        self.client.stop_notify(self.uuid(chara))

    def sleep(self, seconds):
        self.loop.run_until_complete(asyncio.sleep(seconds))
