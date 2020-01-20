"""
"""

import unittest

from io import StringIO

from ski.io.gpx import *


gpx_data = ("<gpx><trk><trkseg>\n"
            "<trkpt lat=\"51.113521576\" lon=\"-115.768188477\"><ele>1746.000000</ele><time>2017-03-16T15:05:31Z</time><speed>5.305555</speed></trkpt>\n"
            "<trkpt lat=\"51.113494873\" lon=\"-115.768218994\"><ele>1737.000000</ele><time>2017-03-16T15:05:33Z</time><speed>4.666667</speed></trkpt>\n"
            "<trkpt lat=\"51.113475800\" lon=\"-115.768264771\"><ele>1736.000000</ele><time>2017-03-16T15:05:34Z</time><speed>4.750000</speed></trkpt>\n"
            "<trkpt lat=\"51.113460541\" lon=\"-115.768325806\"><ele>1735.000000</ele><time>2017-03-16T15:05:35Z</time><speed>4.916667</speed></trkpt>\n"
            "<trkpt lat=\"51.113441467\" lon=\"-115.768394470\"><ele>1736.000000</ele><time>2017-03-16T15:05:36Z</time><speed>4.750000</speed></trkpt>\n"
            "<trkpt lat=\"51.113422394\" lon=\"-115.768455505\"><ele>1738.000000</ele><time>2017-03-16T15:05:37Z</time><speed>4.666667</speed></trkpt>\n"
            "<trkpt lat=\"51.113403320\" lon=\"-115.768524170\"><ele>1739.000000</ele><time>2017-03-16T15:05:38Z</time><speed>5.083333</speed></trkpt>\n"
            "<trkpt lat=\"51.113384247\" lon=\"-115.768592834\"><ele>1740.000000</ele><time>2017-03-16T15:05:39Z</time><speed>5.166667</speed></trkpt>\n"
            "<trkpt lat=\"51.113365173\" lon=\"-115.768653870\"><ele>1741.000000</ele><time>2017-03-16T15:05:40Z</time><speed>4.888889</speed></trkpt>\n"
            "<trkpt lat=\"51.113346100\" lon=\"-115.768714905\"><ele>1742.000000</ele><time>2017-03-16T15:05:41Z</time><speed>4.777778</speed></trkpt>\n"
            "</trkseg></trk></gpx>\n"
            )

class TestGpx(unittest.TestCase):

    def setUp(self):
        pass

    def test_parse_gpx(self):

        gpx = GPXStringSource(gpx_data)
        res = parse_gpx(gpx)

        self.assertEqual(len(res), 10)

    def test_parse_gpx_eof(self):

        gpx = GPXStringSource("<gpx/>")
        res = parse_gpx(gpx)

        self.assertIsNone(res)

    def test_parse_gpx_overflow(self):

        gpx = GPXStringSource(gpx_data, batch_size=5)
        res = parse_gpx(gpx)

        self.assertEqual(len(res), 5)

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
