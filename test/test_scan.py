#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

import unittest
from omron_2jcie_bu01 import Omron2JCIE_BU01

class BLEScanTestCase(unittest.TestCase):
    ADDRESS = None

    @classmethod
    def setUpClass(cls):
        sensor = Omron2JCIE_BU01.ble()
        cls.ADDRESS = sensor.address
        print(f"Target HW address: {cls.ADDRESS}")

    def setUp(self):
        self.sensor = Omron2JCIE_BU01.ble(self.ADDRESS)

    def tearDown(self): pass

    def test_scan_passive(self):
        # Passive Scan: Advertise mode 0x01
        def on_scan(tpl):
            print(tpl)
            self.assertEqual(tpl.__class__.__name__, "Adv_0x01")

        # Advertise mode 0x01
        self.sensor.advertise_setting(mode=0x01)
        self.sensor.disconnect()
        self.sensor.scan(on_scan, 5)

    def test_scan_active(self):
        # Active Scan: Advertise mode 0x03
        def on_scan(tpl):
            print(tpl)
            self.assertEqual(tpl.__class__.__name__, "Adv_0x03")

        # Advertise mode 0x03
        self.sensor.advertise_setting(mode=0x03)
        self.sensor.disconnect()
        self.sensor.scan(on_scan, 5, active=True)

if __name__ == "__main__":
    unittest.main()
