"""
"""

import unittest

from ski.data.coordinate import *


class TestGpx(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_seconds(self):
        d, m, s = add_seconds(60, 0.75)

        self.assertEqual(d, 60)
        self.assertEqual(m, 0)
        self.assertEqual(s, 45)

    def test_add_seconds_and_minutes(self):
        d, m, s = add_seconds(60, 5.75)

        self.assertEqual(d, 60)
        self.assertEqual(m, 5)
        self.assertEqual(s, 45)

    def test_dms_to_wgs(self):
        accuracy = 8
        dms = DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
        dms2 = wgs_to_dms(dms_to_wgs(dms))
        lat_drift = (((dms2.latitude.degrees - dms.latitude.degrees) * 3600.0)
                     + ((dms2.latitude.minutes - dms.latitude.minutes) * 60.0)
                     + (dms2.latitude.seconds - dms.latitude.seconds)
                     )
        lon_drift = (((dms2.longitude.degrees - dms.longitude.degrees) * 3600.0)
                     + ((dms2.longitude.minutes - dms.longitude.minutes) * 60.0)
                     + (dms2.longitude.seconds - dms.longitude.seconds)
                     )
        self.assertAlmostEqual(lat_drift, 0.0, accuracy)
        self.assertAlmostEqual(lon_drift, 0.0, accuracy)

    def test_utm_to_wgs(self):
        accuracy = 8

        utm = UTMCoordinate(292303, 5013403, 33, 'N')
        utm2 = wgs_to_utm(utm_to_wgs(utm))
        x_drift = utm.x - utm2.x
        y_drift = utm.y - utm2.y

        self.assertAlmostEqual(x_drift, 0.0, accuracy)
        self.assertAlmostEqual(y_drift, 0.0, accuracy)

    def test_wgs_to_dms(self):
        accuracy = 8

        wgs = WGSCoordinate(45.12345678, 12.3456789)
        wgs2 = dms_to_wgs(wgs_to_dms(wgs))
        lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
        lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()

        self.assertAlmostEqual(lat_drift, 0.0, accuracy)
        self.assertAlmostEqual(lon_drift, 0.0, accuracy)

    def test_wgs_to_utm(self):
        accuracy = 5

        wgs = WGSCoordinate(45.12345678, 12.3456789)
        wgs2 = utm_to_wgs(wgs_to_utm(wgs))
        lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
        lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()

        self.assertAlmostEqual(lat_drift, 0.0, accuracy)
        self.assertAlmostEqual(lon_drift, 0.0, accuracy)


if __name__ == '__main__':
    unittest.main()
