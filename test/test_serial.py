#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

import unittest
from omron_2jcie_bu01 import Omron2JCIE_BU01

class BLEConnectionTestCase(unittest.TestCase):
    def setUp(self): pass
    def tearDown(self): pass

    def test_connect(self):
        """
        0x5012: "latest_sensing_data",
        0x5013: "latest_calculation_data",
        0x5021: "latest_data_long",
        0x5031: "vibration_count",
        0x5111: "led_setting",
        0x5115: "advertise_setting",
        """
        sensor = Omron2JCIE_BU01.serial("COM3")

        tpl = sensor.latest_data_long()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "latest_data_long")

        tpl = sensor.vibration_count()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "vibration_count")

        tpl = sensor.led()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "led_setting")

        tpl = sensor.info()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "device_info")

        tpl = sensor.advertise_setting()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "advertise_setting")

        tpl = sensor.advertise_setting(mode=0x03)
        print(tpl)
        self.assertEqual(type(tpl).__name__, "advertise_setting")
        self.assertEqual(tpl.mode, 0x03)

        tpl = sensor.advertise_setting(interval=0x00a0)
        print(tpl)
        self.assertEqual(tpl.interval, 0x00a0)

if __name__ == "__main__":
    unittest.main()
