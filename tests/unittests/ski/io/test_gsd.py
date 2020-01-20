"""
"""

import unittest

from io import StringIO

from ski.io.gsd import *


log.setLevel(logging.WARNING)


gsd_data = ("[Date]\n\n"
            "1=2019-01-01-18:00:00\n\n"
            "[TP]\n\n"
            "1=001,2019-01-01:08:00:00\n\n"
            "2=002,2019-01-01:08:00:10\n\n"
            "[001,2019-01-01:08:00:00]\n\n"
            "1=45180950,6351140,90200,270219,1360,24770000\n\n"
            "2=45180991,6351136,90202,270219,1380,24780000\n\n"
            "3=45181031,6351126,90203,270219,1380,24790000\n\n"
            "4=45181051,6351135,90204,270219,1360,24820000\n\n"
            "5=45181071,6351140,90205,270219,1250,24850000\n\n"
            "6=45181084,6351159,90206,270219,1280,24870000\n\n"
            "7=45181106,6351161,90207,270219,1330,24890000\n\n"
            "8=45181127,6351177,90208,270219,1440,24900000\n\n"
            "9=45181182,6351187,90210,270219,1700,24960000\n\n"
            "10=45181226,6351201,90212,270219,1490,25010000\n\n"
            "[002,2019-01-01:08:00:10]\n\n"
            "1=45180950,6351140,90200,270219,1360,24770000\n\n"
            "2=45180991,6351136,90202,270219,1380,24780000\n\n"
            "3=45181031,6351126,90203,270219,1380,24790000\n\n"
            )


class TestGsd(unittest.TestCase):

    def setUp(self):
        pass

    def test_GSDLoader(self):
        source = GSDSource(StringIO(gsd_data))
        self.assertEqual(len(source.sections), 2)

    def test_GSDLoader_with_limit(self):
        source = GSDSource(StringIO(gsd_data), section_limit=1)
        self.assertEqual(len(source.sections), 1)

    def test_GSDLoader_with_offset(self):
        source = GSDSource(StringIO(gsd_data), section_offset=1)
        self.assertEqual(len(source.sections), 1)

    def test_parse_gsd(self):
        source = GSDSource(StringIO(gsd_data))

        res = parse_gsd(source)
        self.assertEquals(len(res), 10)

    def test_parse_gsd_eof(self):
        source = GSDSource(StringIO(gsd_data), section_limit=0)

        res = parse_gsd(source)
        self.assertIsNone(res)

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
