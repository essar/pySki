import datetime
import logging
import unittest
import ski.gsd as undertest

undertest.log.setLevel(logging.DEBUG)

class TestConvertGsdAlt(unittest.TestCase):

    def test_convert_alt(self):
        self.assertEqual(12, undertest.convert_gsd_alt('123456'))

    def test_convert_alt_not_number(self):
        self.assertEqual(0, undertest.convert_gsd_alt('1234ab'))


class TestConvertGsdCoord(unittest.TestCase):

    def test_convert_coord_7digits(self):
        coord = undertest.convert_gsd_coord('1234567')
        self.assertEqual(12, coord[0], 'Degrees')
        self.assertEqual(34, coord[1], 'Minutes')
        self.assertAlmostEqual(0.567 * 60.0, coord[2], msg='Seconds')

    def test_convert_coord_8digits(self):
        coord = undertest.convert_gsd_coord('12345678')
        self.assertEqual(123, coord[0], 'Degrees')
        self.assertEqual(45, coord[1], 'Minutes')
        self.assertAlmostEqual(0.678 * 60.0, coord[2], msg='Seconds')

    def test_convert_coord_not_number(self):
        self.assertIsNone(undertest.convert_gsd_coord('123456ab'))

    def test_convert_coord_negative(self):
        coord = undertest.convert_gsd_coord('-1234567')
        self.assertEqual(-12, coord[0], 'Degrees')
        self.assertEqual(34, coord[1], 'Minutes')
        self.assertAlmostEqual(0.567 * 60.0, coord[2], msg='Seconds')

    def test_convert_coord_negative_8digits(self):
        coord = undertest.convert_gsd_coord('-12345678')
        self.assertEqual(-123, coord[0], 'Degrees')
        self.assertEqual(45, coord[1], 'Minutes')
        self.assertAlmostEqual(0.678 * 60.0, coord[2], msg='Seconds')


class TestConvertGsdDate(unittest.TestCase):

    def test_convert_date(self):
        date = undertest.convert_gsd_date('011020', '091011')
        self.assertEqual(2020, date.year, 'Year')
        self.assertEqual(10, date.month, 'Month')
        self.assertEqual(1, date.day, 'Day')
        self.assertEqual(9, date.hour, 'Hour')
        self.assertEqual(10, date.minute, 'Minute')
        self.assertEqual(11, date.second, 'Second')

    def test_convert_date_date_not_number(self):
        self.assertIsNone(undertest.convert_gsd_date('1234ab', '091011'))

    def test_convert_date_time_not_number(self):
        self.assertIsNone(undertest.convert_gsd_date('011020', '091011ab'))

    def test_convert_date_date_invalid(self):
        self.assertIsNone(undertest.convert_gsd_date('987654', '091011'))

    def test_convert_date_time_invalid(self):
        self.assertIsNone(undertest.convert_gsd_date('011020', '234567'))


class TestConvertGsdSpeed(unittest.TestCase):

    def test_convert_speed(self):
        self.assertEqual(12.34, undertest.convert_gsd_speed('1234'))

    def test_convert_speed_not_number(self):
        self.assertEqual(0, undertest.convert_gsd_speed('1234ab'))
