"""Parser tests for Sensirion SCD4x CO2 Gadget BLE advertisements."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scd4x_gadget import COMPANY_ID, parse_advertisement

# Public sample from akx/sensirion-ble: MyCO2 / SCD4x type-8 payload
SENSOR_DATA_1 = b"\x00\x08\x84\xe3>_3G\xd4\x02"


class ParseAdvertisementTests(unittest.TestCase):
    def test_parse_type8_sample(self):
        sample = parse_advertisement(SENSOR_DATA_1)
        self.assertIsNotNone(sample)
        self.assertEqual(sample.device_id, "84E3")
        self.assertEqual(sample.co2_ppm, 724)
        self.assertEqual(sample.temperature_c, 20.1)
        self.assertEqual(sample.humidity_rh, 27.8)

    def test_parse_rejects_unknown_type(self):
        self.assertIsNone(parse_advertisement(b"\x00\x99\x00\x00"))

    def test_parse_rejects_short(self):
        self.assertIsNone(parse_advertisement(b"\x00\x08"))

    def test_company_id_is_sensirion(self):
        self.assertEqual(COMPANY_ID, 0x06D5)


if __name__ == "__main__":
    unittest.main()
