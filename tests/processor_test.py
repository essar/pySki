import datetime
import unittest
import ski.processor as undertest


class TestBuildPointFromGSD(unittest.TestCase):

    def test_build_point_from_gsd_invalid_line(self):
        self.assertIsNone(undertest.build_point_from_gsd(['39531388', '-105457814', '161655', '150218', '180']))

    def test_build_point_from_gsd_valid_line(self):
        line = ['39531388', '-105457814', '161655', '150218', '180', '27760000']
        point = undertest.build_point_from_gsd(line)
        self.assertEqual(1518711415, point['ts'], 'ts')
        self.assertEqual(datetime.datetime(2018, 2, 15, 16, 16, 55), point['dt'], 'dt')
        self.assertAlmostEqual(39.8856, point['lat'], places=3, msg='lat')
        self.assertAlmostEqual(-105.7630, point['lon'], places=4, msg='lon')
        self.assertEqual(434760, point['x'], 'x')
        self.assertEqual(4415344, point['y'], 'y')
        self.assertEqual(1.80, point['spd'], 'spd')
        self.assertEqual(2776, point['alt'], 'alt')

    def test_build_point_from_gsd_no_convert_coords(self):
        line = ['39531388', '-105457814', '161655', '150218', '180', '27760000']
        point = undertest.build_point_from_gsd(line, convert_coords=False)
        self.assertFalse('x' in point, 'x')
        self.assertFalse('y' in point, 'y')


class TestEnrichPoint(unittest.TestCase):

    def test_enrich_point_1point(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point)
        self.assertEqual(0.0, result['d'], 'd')
        self.assertEqual(0, result['hdg'], 'hdg')
        self.assertEqual(0, result['alt_d'], 'alt_d')
        self.assertEqual(0.0, result['spd_d'], 'spd_d')

    def test_enrich_point_2points(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        window = undertest.MovingWindow(2)
        window.add_point({ 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 })
        point = { 'ts': 1518711440, 'lat': 39.8855, 'lon': -105.7630, 'x': 434761, 'y': 4415329, 'spd': 1.20, 'alt': 2776 }

        result = undertest.enrich_point(window, point)
        self.assertAlmostEqual(15.033, result['d'], places=3, msg='d')
        self.assertAlmostEqual(176.186, result['hdg'], places=3, msg='hdg')
        self.assertEqual(0, result['alt_d'], 'alt_d')
        self.assertAlmostEqual(-0.600, result['spd_d'], msg='spd_d')

    def test_enrich_point_1point_missing_xy(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'spd': 1.80, 'alt': 2776 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point)
        self.assertFalse('d' in result, 'd')
        self.assertFalse('hdg' in result, 'hdg')
        self.assertEqual(0, result['alt_d'], 'alt_d')
        self.assertEqual(0.0, result['spd_d'], 'spd_d')

    def test_enrich_point_1point_missing_no_calc_distance(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point, add_distance=False)
        self.assertFalse('d' in result, 'd')
        self.assertFalse('hdg' in result, 'hdg')
        self.assertEqual(0, result['alt_d'], 'alt_d')
        self.assertEqual(0.0, result['spd_d'], 'spd_d')

    def test_enrich_point_1point_missing_no_calc_deltas(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point, add_deltas=False)
        self.assertEqual(0.0, result['d'], 'd')
        self.assertEqual(0, result['hdg'], 'hdg')
        self.assertFalse('alt_d' in result, 'alt_d')
        self.assertFalse('spd_d' in result, 'spd_d')

    def test_enrich_point_1point_missing_alt(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point)
        self.assertEqual(0.0, result['d'], 'd')
        self.assertEqual(0, result['hdg'], 'hdg')
        self.assertFalse('alt_d' in result, 'alt_d')
        self.assertEqual(0.0, result['spd_d'], 'spd_d')

    def test_enrich_point_1point_missing_spd(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'alt': 2776 }
        result = undertest.enrich_point(undertest.MovingWindow(2), point)
        self.assertEqual(0.0, result['d'], 'd')
        self.assertEqual(0, result['hdg'], 'hdg')
        self.assertEqual(0, result['alt_d'], 'alt_d')
        self.assertFalse('spd_d' in result, 'spd_d')