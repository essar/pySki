"""
"""

import unittest

from ski.io.gsd import *


class TestGsd(unittest.TestCase):

    def setUp(self):
        pass

    def test_parse_gsd_line(self):
        res = parse_gsd_line('1=45180950,6351140,90200,270219,1360,24770000')
        self.assertEqual(res.ts, 1551258120)
        self.assertEqual(res.lat, 45.30158333333333)
        self.assertEqual(res.lon, 6.585233333333333)
        self.assertEqual(res.spd, 13.6)
        self.assertEqual(res.alt, 2477)

    def test_parse_gsd_line_not_gsd_data(self):
        res = parse_gsd_line('This is invalid GSD data')
        self.assertEqual(res.ts, 0)
        self.assertEqual(res.lat, 0)
        self.assertEqual(res.lon, 0)
        self.assertEqual(res.spd, 0)
        self.assertEqual(res.alt, 0)

    def test_parse_gsd_line_no_values(self):
        res = parse_gsd_line('1=1234567890')
        self.assertEqual(res.ts, 0)
        self.assertEqual(res.lat, 0)
        self.assertEqual(res.lon, 0)
        self.assertEqual(res.spd, 0)
        self.assertEqual(res.alt, 0)

    def test_parse_gsd_line_invalid_speed(self):
        res = parse_gsd_line('1=45180950,6351140,90200,270219,abcd,abcd')
        self.assertEqual(res.ts, 1551258120)
        self.assertEqual(res.lat, 45.30158333333333)
        self.assertEqual(res.lon, 6.585233333333333)
        self.assertEqual(res.spd, 0)
        self.assertEqual(res.alt, 0)

    def test_parse_gsd_line_missing_alt(self):
        res = parse_gsd_line('1=45180950,6351140,90200,270219,1360')
        self.assertEqual(res.ts, 1551258120)
        self.assertEqual(res.lat, 45.30158333333333)
        self.assertEqual(res.lon, 6.585233333333333)
        self.assertEqual(res.spd, 13.6)
        self.assertEqual(res.alt, 0)

    def test_parse_gsd_line_none(self):
        res = parse_gsd_line(None)
        self.assertIsNone(res)

    def test_split_line(self):
        res = split_line('1=45180950,6351140,90200,270219,1360,24770000')
        self.assertEqual(len(res), 6)

    def test_split_line_missing_am(self):
        res = split_line('45180950,6351140,90200,270219,1360,24770000')
        self.assertEqual(len(res), 6)

    def test_split_line_extra_parts(self):
        res = split_line('1=45180950,6351140,90200,270219,1360,24770000,12345678')
        self.assertEqual(len(res), 6)

    def test_split_line_missing_parts(self):
        res = split_line('1=45180950,6351140,90200,270219,1360')
        self.assertEqual(len(res), 6)

    def test_split_line_header(self):
        res = split_line('1=001,2019-02-27:09:02:00', as_header=True)
        self.assertEqual(len(res), 2)

    def test_split_line_header_missing_am(self):
        res = split_line('001,2019-02-27:09:02:00', as_header=True)
        self.assertEqual(len(res), 2)

    def test_split_line_header_extra_parts(self):
        res = split_line('1=001,2019-02-27:09:02:00,12345678', as_header=True)
        self.assertEqual(len(res), 2)

    def test_split_line_header_missing_parts(self):
        res = split_line('1=001', as_header=True)
        self.assertEqual(len(res), 2)


if __name__ == '__main__':
    unittest.main()
