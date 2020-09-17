# OMRON 2JCIE-BU01

- JAPANESE document is available: See README_ja.md

## Synopsis
Module and sample code for obtaining data with OMRON 2JCIE-BU01 Environment Sensor by Python.
The codes work with Python 3.6 and above. This module supports USB serial communication and BLE.
This module depends on pySerial(serial communication) and Bleak(BLE).

## Example
### Obtain sensing data _via_ serial communication

    from envsensor.serial import Omron2JCIE_BU01_Serial
    sensor = Omron2JCIE_BU01_Serial("/dev/ttyUSB0") # Linux
    sensor = Omron2JCIE_BU01_Serial("COM5")         # Windows
    devinfo = sensor.info()
    data = sensor.latest_data_long()

### Obtain sensing data _via_ BLE communication

    # Read latest data with connection
    from envsensor.serial import Omron2JCIE_BU01_BLE
    sensor = Omron2JCIE_BU01_BLE("AA:BB:CC:DD:EE:FF")
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

## Files
- envsensor/ -- This module
  - __init__.py -- Common class for serial and BLE
  - ble.py -- Omron2JCIE_BU01_BLE class for BLE
  - serial.py -- Omron2JCIE_BU01_Serial class for serial
- test/ -- Unit test (for minimum operation check)
- examples/ -- Example codes

## Installation dependencies
### For serial communication
- pySerial 3.4

    pip3 install pyserial

### For BLE
- Bleak 0.7.1
- Codes was confirmed the operation on Windows 10

    pip3 install bleak

## Module
### _class_ envsensor.DataParser()

### _class_ envseosor.Omron2JCIE_BU01_Base()

### _class_ envsensor.serial.Omron2JCIE_BU01_Serial(_port_)
Class for serial communication.
Parameter _port_ is for example, /dev/ttyUSB0 (Linux), COM5 (Windows).

### _class_ envsensor.ble.Omron2JCIE_BU01_BLE(_hardware_address=None_)
Class for BLE communication.
Hardware address is optional. If ommited, the address will be specified by discover().
The discover() takes time, specifying address are recommended.

### Omron2JCIE_BU01_Base object
Do not instantiate it directly, but inherit it.

- get(_address_, _data=b""_, _name=None_)
  - Returns data which is parsed by DataParser.
- vibration_count()
  - 4.5.7 Vibration count (Address: 0x5031)
    - earthquake: Earthquake count
    - vibration: Vibration count
- led(rule: int=None, rgb: tuple=None)
  - 4.5.8 LED setting [normal state] (Address: 0x5111)
    - Get/Set LED setting
    - rule: Display rule (normal state)
    - rgb: (red、green、blue) Tuple of intensity
- advertise_setting(interval=None, mode=None)

### Omron2JCIE_BU01_Serial object
- latest_data_long()
  - 4.4.3 Latest data long (Address: 0x5021) [USB original address]
    - seq: Sequence number (UInt8)
    - temperature: Temerature (SInt16); 0.01 degC
    - humidity: Relative humidity (SInt16); 0.01 %RH
    - light: Ambient light (SInt16); 1 lx
    - pressure: Barometric pressure (SInt32); 0.001 hPa
    - noise: Sound noise (SInt16); 0.01 dB
    - eTVOC: eTVOC (SInt16); 1 ppb
    - eCO2: eCO2 (SInt16); 1 ppm
    - thi: Discomfort index; THI (SInt16); 0.01
    - wbgt: Heat stroke; WBGT (SInt16); 0.01 degC
    - vibration: Vibration information (UInt8); See Table 124
    - si: SI value (UInt16); 0.1 kine
    - pga: PGA (UInt16); 0.1 gal
    - seismic_intensity: Seismic intensity (UInt16); 0.001
- info()
  - 4.5.25 Device information (Address: 0x180a)
    - model: Model
    - serial: Serial number
    - fw_rev: Firmware version
    - hw_rev: Hardware version
    - manufacturer: Manufacturer name

### Omron2JCIE_BU01_BLE object
- scan(_callback_, _scantime=10_, _active=False_, _distinct=True_)
- connect()
- disconnect()
- is_connected()
- latest_sensing_data()
  - 2.2 Latest Data Service (Service UUID: 0x5010)
    - 0x5012: Latest sensing data
- latest_calculation_data()
  - 2.2 Latest Data Service (Service UUID: 0x5010)
    - 0x5013: Latest calculation data
- start_notify(_characteristic_uuid_, _callback_):
  - Activate notifications on a characteristic
	```
    	def callback(sender, tpl):
        	print(f"{sender} {tpl}")
        sensor.start_notify(0x5012, callback)
        sensor.start_notify(0x5013, callback)
        sensor.sleep(5)
        sensor.stop_notify(0x5012)
        sensor.stop_notify(0x5013)
	```
  - The _callback_ will be called every time notification arrives.
  - Arguments of _callback_ are sender and parsed data.
- stop_notify(characteristic_uuid)
  - Stop notification.
- sleep(seconds)
  - Call asyncio.sleep()

## 参考サイト
- OMRON 2JCIE-BU Environment Sensor USB型
  - https://www.components.omron.com/product-detail?partId=73065