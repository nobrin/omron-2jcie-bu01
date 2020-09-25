#!/usr/bin/env python3
import sys
sys.path.insert(0, "../lib-ext")
sys.path.insert(0, "..")

import unittest
from omron_2jcie_bu01 import Omron2JCIE_BU01

class BLEConnectionTestCase(unittest.TestCase):
    ADDRESS = None

    @classmethod
    def setUpClass(cls):
        sensor = Omron2JCIE_BU01.ble()
        cls.ADDRESS = sensor.address
        print(f"Target HW address: {cls.ADDRESS}")

    def setUp(self):
        self.sensor = Omron2JCIE_BU01.ble(self.ADDRESS)

    def tearDown(self): pass

    def test_connect(self):
        """
        0x5012: "latest_sensing_data",
        0x5013: "latest_calculation_data",
        0x5021: "latest_data_long",
        0x5031: "vibration_count",
        0x5111: "led_setting",
        0x5115: "advertising_setting",
        """

        self.assertTrue(self.sensor.address)
        self.sensor.connect()
        self.assertTrue(self.sensor.is_connected())

        tpl = self.sensor.latest_sensing_data()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "latest_sensing_data")

        tpl = self.sensor.latest_calculation_data()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "latest_calculation_data")

        tpl = self.sensor.vibration_count()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "vibration_count")

        tpl = self.sensor.led()
        print(tpl)
        self.assertEqual(type(tpl).__name__, "led_setting")

        self.sensor.disconnect()
        self.assertFalse(self.sensor.is_connected())

if __name__ == "__main__":
    unittest.main()
