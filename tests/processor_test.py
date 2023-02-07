import datetime
import unittest
import ski.processor as undertest


class TestAddTimezone(unittest.TestCase):

    def test_add_timezone_invalid_cached_tz(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        tz = {'zonename': 'Invalid'}
        result = undertest.add_timezone(point, tz)
        self.assertEqual('America/Denver', tz['zonename'])
        self.assertTrue('dt' in point)
        self.assertEqual('America/Denver', result['dt'].tzinfo.key)

    def test_add_timezone_missing_lat_lon(self):
        point = { 'ts': 1518711415, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        tz = {}
        result = undertest.add_timezone(point, tz)
        self.assertTrue('dt' in point)
        self.assertEqual('UTC', result['dt'].tzinfo.key)

    def test_add_timezone_no_cache(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        tz = {}
        result = undertest.add_timezone(point, tz)
        self.assertEqual('America/Denver', tz['zonename'])
        self.assertTrue('dt' in point)
        self.assertEqual('America/Denver', result['dt'].tzinfo.key)

    def test_add_timezone_with_cache(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        tz = { 'zonename': 'America/Denver' }
        result = undertest.add_timezone(point, tz)
        self.assertEqual('America/Denver', tz['zonename'])
        self.assertTrue('dt' in point)
        self.assertEqual('America/Denver', result['dt'].tzinfo.key)


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


class TestLinearInterpolate(unittest.TestCase):

    def test_linear_interpolate_single_point(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        self.assertListEqual([point], list(undertest.linear_interpolate((x for x in [point]))))

    def test_linear_interpolate_duplicate_point(self):
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        self.assertListEqual([point], list(undertest.linear_interpolate((x for x in [point, point]))))

    def test_linear_interpolate_adjuct_point(self):
        points = [
            { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 },
            { 'ts': 1518711416, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        ]
        self.assertListEqual(points, list(undertest.linear_interpolate((x for x in points))))
        
    def test_linear_interpolate_missing_single_point(self):
        points = [
            { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 },
            { 'ts': 1518711417, 'lat': 39.8858, 'lon': -105.7634, 'x': 434762, 'y': 4415348, 'spd': 1.81, 'alt': 2776 }
        ]
        exp_points = [
            points[0],
            { 'ts': 1518711416, 'lat': 39.8857, 'lon': -105.7632, 'x': 434761, 'y': 4415346, 'spd': 1.805, 'alt': 2776 },
            points[1]
        ]

        self.assertListEqual(exp_points, list(undertest.linear_interpolate((x for x in points))))
    
    def test_linear_interpolate_missing_multiple_points(self):
        points = [
            { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 },
            { 'ts': 1518711419, 'lat': 39.8860, 'lon': -105.7638, 'x': 434800, 'y': 4415352, 'spd': 1.82, 'alt': 2772 }
        ]
        exp_points = [
            points[0],
            { 'ts': 1518711416, 'lat': 39.8857, 'lon': -105.7632, 'x': 434770, 'y': 4415346, 'spd': 1.805, 'alt': 2775 },
            { 'ts': 1518711417, 'lat': 39.8858, 'lon': -105.7634, 'x': 434780, 'y': 4415348, 'spd': 1.810, 'alt': 2774 },
            { 'ts': 1518711418, 'lat': 39.8859, 'lon': -105.7636, 'x': 434790, 'y': 4415350, 'spd': 1.815, 'alt': 2773 },
            points[1]
        ]

        self.assertListEqual(exp_points, list(undertest.linear_interpolate((x for x in points))))
        

class TestSummary(unittest.TestCase):

    def test_summary_alt_extend_min(self):
        summary = {'min_alt': 3000, 'max_alt': 3000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(2776, summary['min_alt'])
        self.assertEqual(3000, summary['max_alt'])

    def test_summary_alt_extend_max(self):
        summary = {'min_alt': 2000, 'max_alt': 2000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(2000, summary['min_alt'])
        self.assertEqual(2776, summary['max_alt'])

    def test_summary_alt_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(2776, summary['min_alt'])
        self.assertEqual(2776, summary['max_alt'])

    def test_summary_descent_no_alt_d(self):
        summary = {'total_desc': 1000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(1000, summary['total_desc'])

    def test_summary_descent_nve_delta(self):
        summary = {'total_desc': 1000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776, 'alt_d': -5 }
        undertest.summary(summary, point)
        self.assertEqual(1005, summary['total_desc'])

    def test_summary_descent_pve_delta(self):
        summary = {'total_desc': 1000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776, 'alt_d': 5 }
        undertest.summary(summary, point)
        self.assertEqual(1000, summary['total_desc'])

    def test_summary_descent_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776, 'alt_d': -5 }
        undertest.summary(summary, point)
        self.assertEqual(5, summary['total_desc'])

    def test_summary_alt_no_alt(self):
        summary = {'min_alt': 2000, 'max_alt': 3000}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80 }
        undertest.summary(summary, point)
        self.assertEqual(2000, summary['min_alt'])
        self.assertEqual(3000, summary['max_alt'])

    def test_summary_distance(self):
        summary = {'total_dist': 120}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776, 'd': 2.543 }
        undertest.summary(summary, point)
        self.assertEqual(122.543, summary['total_dist'])

    def test_summary_distance_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776, 'd': 2.543 }
        undertest.summary(summary, point)
        self.assertEqual(2.543, summary['total_dist'])

    def test_summary_distance_no_d(self):
        summary = {'total_dist': 1234}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(1234, summary['total_dist'])

    def test_summary_spd_extend(self):
        summary = {'max_spd': 1.50}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(1.80, summary['max_spd'])

    def test_summary_spd_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(1.80, summary['max_spd'])

    def test_summary_spd_no_spd(self):
        summary = {'max_spd': 1.50}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertEqual(1.50, summary['max_spd'])

    def test_summary_x_bounds_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([434760, 434760], summary['x_bounds'])

    def test_summary_x_bounds_extend_lower(self):
        summary = {'x_bounds': [434770, 434770]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([434760, 434770], summary['x_bounds'])

    def test_summary_x_bounds_extend_upper(self):
        summary = {'x_bounds': [434750, 434750]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([434750, 434760], summary['x_bounds'])

    def test_summary_x_bounds_no_x(self):
        summary = {'x_bounds': [434750, 434750]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([434750, 434750], summary['x_bounds'])

    def test_summary_y_bounds_empty_summary(self):
        summary = {}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([4415344, 4415344], summary['y_bounds'])

    def test_summary_y_bounds_extend_lower(self):
        summary = {'y_bounds': [4415364, 4415364]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([4415344, 4415364], summary['y_bounds'])

    def test_summary_y_bounds_extend_upper(self):
        summary = {'y_bounds': [4415324, 4415324]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'x': 434760, 'y': 4415344, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([4415324, 4415344], summary['y_bounds'])

    def test_summary_y_bounds_no_y(self):
        summary = {'y_bounds': [4415344, 4415344]}
        point = { 'ts': 1518711415, 'lat': 39.8856, 'lon': -105.7630, 'spd': 1.80, 'alt': 2776 }
        undertest.summary(summary, point)
        self.assertListEqual([4415344, 4415344], summary['y_bounds'])
