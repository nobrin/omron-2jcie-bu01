#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

import unittest
from omron_2jcie_bu01.ble import Omron2JCIE_BU01_BLE

class BLENotificationTestCase(unittest.TestCase):
    ADDRESS = None

    @classmethod
    def setUpClass(cls):
        sensor = Omron2JCIE_BU01_BLE()
        cls.ADDRESS = sensor.address
        print(f"Target HW address: {cls.ADDRESS}")

    def setUp(self):
        self.sensor = Omron2JCIE_BU01_BLE(self.ADDRESS)

    def tearDown(self): pass

    def test_notify(self):
        def callback(sender, tpl):
            print(f"{sender} {tpl}")
        self.sensor.start_notify(0x5012, callback)
        self.sensor.start_notify(0x5013, callback)
        self.sensor.sleep(5)
        self.sensor.stop_notify(0x5012)
        self.sensor.stop_notify(0x5013)

if __name__ == "__main__":
    unittest.main()
