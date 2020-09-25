# OMRON 2JCIE-BU01のデータ取得
## 概要
OMRON環境センサー2JCIE-BU01からPythonで測定データを取得するためのクラスとサンプルプログラムです。
Python 3.6以上で動作します。クラスはUSBシリアル通信およびBLEに対応しています。

## Example
### シリアル通信で測定値を取得する

```python
from omron_2jcie_bu01 import Omron2JCIE_BU01
sensor = Omron2JCIE_BU01.serial("/dev/ttyUSB0") # Linux
sensor = Omron2JCIE_BU01.serial("COM5")         # Windows
devinfo = sensor.info()
data = sensor.latest_data_long()
```

### BLE通信で測定値を取得する

```python
# Read latest data with connection
from omron_2jcie_bu01 import Omron2JCIE_BU01
sensor = Omron2JCIE_BU01.ble("AA:BB:CC:DD:EE:FF")
data1 = sensor.latest_sensing_data()
data2 = sensor.latest_calculation_data()
```

```python
# Read latest data by scan
def on_scan(data):
    print("SCAN", data)

# Advertising mode: 0x01 (Passive)
sensor.scan(on_scan, scantime=3)

# Advertising mode: 0x03 (Active)
sensor.scan(on_scan, scantime=3, active=True)
```

```python
# Notify sensing data
def on_notify(sender, tpl):
    print(f"{sender} {tpl}")

sensor.start_notify(0x5012, on_notify)
sensor.start_notify(0x5013, on_notify)
sensor.sleep(5)
sensor.stop_notify(0x5012)
sensor.stop_notify(0x5013)
```

## ファイル
- omron_2jcie_bu01/ -- モジュール本体ディレクトリ
  - __init__.py -- シリアルおよびBLEでの共通クラス
  - ble.py -- BLE用クラスOmron2JCIE_BU01_BLEクラスの定義
  - serial.py -- シリアル通信用クラスOmron2JCIE_BU01_Serialクラスの定義
- test/ -- ユニットテスト(動作確認程度のテスト)
- measure.py
  - Omron2JCIE_BU01クラス使用サンプル

## インストール
### 2JCIE-BU01本体の認識(シリアル通信)
PCとシリアル通信するためにハードウェアを認識させる。
BLEの場合はBluetoothが使えれば設定不要。

#### Linux(CentOS 7.7)
- USBポートに挿して認識させる

```
$ dmesg
...
[2865803.861939] usb 3-2: new full-speed USB device number 2 using uhci_hcd
[2865804.027026] usb 3-2: New USB device found, idVendor=0590, idProduct=00d4, bcdDevice=10.00
[2865804.027035] usb 3-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[2865804.027040] usb 3-2: Product: 2JCIE-BU01
[2865804.027056] usb 3-2: Manufacturer: OMRON
[2865804.027061] usb 3-2: SerialNumber: XXXXXXXX
...
```

- ftdi_sioドライバを読み込み、new_idを書き込むことで認識させる

```
$ sudo modprobe ftdi_sio
$ sudo echo "0590 00d4" > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
```

```
$ dmesg
...
[2865878.528581] usbcore: registered new interface driver ftdi_sio
[2865878.528622] usbserial: USB Serial support registered for FTDI USB Serial Device
[2865897.783478] ftdi_sio 3-2:1.0: FTDI USB Serial Device converter detected
[2865897.783557] usb 3-2: Detected FT-X
[2865897.787100] usb 3-2: FTDI USB Serial Device converter now attached to ttyUSB0
...
```

これで/dev/ttyUSB0(番号は環境による)にセンサーのシリアルポートが割り当てられます。

#### Windows10(Version 1909)
- OMRON 2JCIE-BU01のページからソフトウェアをダウンロードし、ドライバの更新でインストールする
- デバイスマネージャで確認するとポート番号(例: COM5)を確認する

### シリアル接続
シリアル接続はpySerialを使用します。pySerial 3.4を使用しました。

    pip3 install pyserial

### Bluetooth接続
BluetoothはBleakを使用します。Bleak 0.7.1を使用しました。
Windows10で動作確認しました。

    pip3 install bleak

## モジュール
### _class_ omron_2jcie_bu01.DataParser()
得られたバイナリデータを解析するためのクラス。
応答の種類のフィールド定義を保持しています。
フィールドを定義することで他の機能の応答にも対応可能です。

### _class_ omron_2jcie_bu01.Omron2JCIE_BU01()
ベースクラス。

- serial(_port_)
  - Omron2JCIE_BU01_Serialインスタンスを返します。
- ble(_hardware_address=None_)
  - Omron2JCIE_BU01_BLEインスタンスを返します。

### _class_ omron_2jcie_bu01.serial.Omron2JCIE_BU01_Serial(_port_)
シリアル通信用クラス。
ポートはLinuxは/dev/ttyUSB0など、WindowsではCOM5などとなります。

### _class_ omron_2jcie_bu01.ble.Omron2JCIE_BU01_BLE(_hardware_address=None_)
BLE通信用クラス。
アドレスは省略可能。省略した場合はdiscoverして、最初に見つかったRbtデバイスをアドレスとして設定します。
省略した場合はdiscoverに時間がかかるので、アドレス指定を推奨します。

### Omron2JCIE_BU01オブジェクト
ベースクラスのため直接インスタンス化せず、継承して使用して下さい。

- get(_address_, _data=b""_, _name=None_)
  - DataParserでの解析後データを返します。
- vibration_count()
  - 4.5.7 Vibration count (Address: 0x5031)を取得します
    - earthquake: 地震の回数
    - vibration: 振動の回数
- led(rule: int=None, rgb: tuple=None)
  - 4.5.8 LED setting [normal state] (Address: 0x5111)を取得/設定します
    - rule: 表示設定
    - rgb: (赤、緑、青)の輝度のタプル
- advertise_setting(interval=None, mode=None)

### Omron2JCIE_BU01_Serialオブジェクト
- latest_data_long()
  - 4.4.3 Latest data long (Address: 0x5021)を取得します[USB original address]
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
  - 4.5.25 Device information (Address: 0x180a)を取得します
    - model: モデル番号
    - serial: シリアル番号
    - fw_rev: ファームウェアバージョン
    - hw_rev: ハードウェアバージョン
    - manufacturer: 製造メーカー

### Omron2JCIE_BU01_BLEオブジェクト
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
	```python
    	def callback(sender, tpl):
        	print(f"{sender} {tpl}")
        sensor.start_notify(0x5012, callback)
        sensor.start_notify(0x5013, callback)
        sensor.sleep(5)
        sensor.stop_notify(0x5012)
        sensor.stop_notify(0x5013)
	```
  - 通知が届くたびにcallbackが呼ばれます。その際の引数はsenderと解析後データです。
- stop_notify(characteristic_uuid)
  - notifyを停止します。
- sleep(seconds)
  - asyncio.sleep()をコールしてseconds秒間待機します。

## 参考サイト
- OMRON 形2JCIE-BU 環境センサ USB型
  - https://www.omron.co.jp/ecb/product-detail?partNumber=2JCIE-BU
- GitHub hito4t/Omron2JCIE-BU01
  - https://github.com/hito4t/Omron2JCIE-BU01
- Bleak
  - https://bleak.readthedocs.io/en/latest/index.html
- Pythonライブラリ bleakでWindows10/macOS/Linux上でtoioコアキューブを動かしてみる
  - https://qiita.com/kenichih/items/8baa27b3aecc94dd8193
- OMRON USB型環境センサー 2JCIE-BUをLinux(debian9/OpenBlocks IoT)からUSB接続して使用する
  - https://qiita.com/goto2048/items/d2706088af90503dd4c8
