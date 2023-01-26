import unittest
import ski.coordinate as undertest


class TestDMStoWGS(unittest.TestCase):

    def test_latitude(self):
        dms = undertest.DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
        wgs = undertest.DMS_to_WGS(dms)
        dms2 = undertest.WGS_to_DMS(wgs)

        lat_drift = (((dms2.latitude.degrees - dms.latitude.degrees) * 3600.0)
                + ((dms2.latitude.minutes - dms.latitude.minutes) * 60.0)
                + (dms2.latitude.seconds - dms.latitude.seconds)
        )
        self.assertAlmostEqual(0, lat_drift)

    def test_longitude(self):
        dms = undertest.DMSCoordinate(50, 50, 50.555555555, 120, 40, 22.222222222)
        wgs = undertest.DMS_to_WGS(dms)
        dms2 = undertest.WGS_to_DMS(wgs)

        lon_drift = (((dms2.longitude.degrees - dms.longitude.degrees) * 3600.0)
                + ((dms2.longitude.minutes - dms.longitude.minutes) * 60.0)
                + (dms2.longitude.seconds - dms.longitude.seconds)
        )
        self.assertAlmostEqual(0, lon_drift)


class TestWGStoDMS(unittest.TestCase):

    def test_latitude(self):
        wgs = undertest.WGSCoordinate(45.12345678, 12.3456789)
        dms = undertest.WGS_to_DMS(wgs)
        wgs2 = undertest.DMS_to_WGS(dms)
        
        lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
        self.assertAlmostEqual(0, lat_drift)

    def test_longitude(self):
        wgs = undertest.WGSCoordinate(45.12345678, 12.3456789)
        dms = undertest.WGS_to_DMS(wgs)
        wgs2 = undertest.DMS_to_WGS(dms)

        lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()
        self.assertAlmostEqual(0, lon_drift)


class TestUTMtoWGS(unittest.TestCase):

    def test_x(self):
        utm = undertest.UTMCoordinate(292303, 5013403, 33, 'N')
        wgs = undertest.UTM_to_WGS(utm)
        utm2 = undertest.WGS_to_UTM(wgs)
    
        x_drift = utm.x - utm2.x
        self.assertAlmostEqual(0, x_drift)

    def test_y(self):
        utm = undertest.UTMCoordinate(292303, 5013403, 33, 'N')
        wgs = undertest.UTM_to_WGS(utm)
        utm2 = undertest.WGS_to_UTM(wgs)

        y_drift = utm.y - utm2.y
        self.assertAlmostEqual(0, y_drift)


class TestWGStoUTM(unittest.TestCase):

    def test_latitude(self):
        wgs = undertest.WGSCoordinate(45.12345678, 12.3456789)
        utm = undertest.WGS_to_UTM(wgs)
        wgs2 = undertest.UTM_to_WGS(utm)
    
        lat_drift = wgs.get_latitude_degrees() - wgs2.get_latitude_degrees()
        self.assertAlmostEqual(0, lat_drift, 5)

    def test_longitude(self):
        wgs = undertest.WGSCoordinate(45.12345678, 12.3456789)
        utm = undertest.WGS_to_UTM(wgs)
        wgs2 = undertest.UTM_to_WGS(utm)

        lon_drift = wgs.get_longitude_degrees() - wgs2.get_longitude_degrees()
        self.assertAlmostEqual(0, lon_drift, 5)


if __name__ == '__main__':
    unittest.main()
