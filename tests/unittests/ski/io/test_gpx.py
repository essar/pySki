"""
"""

import unittest

from xml.dom.minidom import parseString

from ski.io.gpx import *


class TestGpx(unittest.TestCase):

    def setUp(self):
        pass

    def test_parse_gpx_elem(self):
        elem = parseString('<trkpt lat="45.30158333333333" lon="6.585233333333333"><time>2019-02-27T09:02:00Z</time>'
                           '<ele>2477</ele><speed>3.7777777777777778</speed></trkpt>')

        res = parse_gpx_elem(elem.getElementsByTagName('trkpt')[0])
        self.assertEqual(res.ts, 1551258120)
        self.assertEqual(res.lat, 45.30158333333333)
        self.assertEqual(res.lon, 6.585233333333333)
        self.assertEqual(res.spd, 13.6)
        self.assertEqual(res.alt, 2477)


if __name__ == '__main__':
    unittest.main()
