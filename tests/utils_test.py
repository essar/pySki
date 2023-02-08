import unittest
import ski.utils as undertest
from datetime import datetime
from json import dumps
from zoneinfo import ZoneInfo

class TestDateAwareJsonEncoder(unittest.TestCase):

    def test_default_with_date(self):
        dt = datetime(2023, 2, 1, 12, 1, 2, tzinfo=ZoneInfo('UTC'))
        self.assertEqual('2023-02-01T12:01:02+00:00', undertest.DateAwareJSONEncoder().default(dt))
        self.assertEqual('{"date": "2023-02-01T12:01:02+00:00"}', dumps({ 'date' : dt }, cls=undertest.DateAwareJSONEncoder))

    def test_default_with_string(self):
        self.assertRaises(TypeError, lambda: undertest.DateAwareJSONEncoder().default('test'))
        self.assertEqual('{"str": "test"}', dumps({ 'str' : 'test' }, cls=undertest.DateAwareJSONEncoder))


class TestMovingWindow(unittest.TestCase):

    def test_average_empty_window(self):
        window = undertest.MovingWindow(1)
        self.assertEqual(0, window.average(None))

    def test_average_single_point(self):
        window = undertest.MovingWindow(1)
        window.add_point({'test': 1})
        self.assertEqual(1, window.average('test'))

    def test_average_multiple_point(self):
        window = undertest.MovingWindow(2)
        window.add_point({'test': 1})
        window.add_point({'test': 2})
        window.add_point({'test': 3})
        self.assertEqual(2.5, window.average('test'))

    def test_delta_empty_window(self):
        window = undertest.MovingWindow(1)
        self.assertEqual(0, window.delta(None))

    def test_delta_single_point(self):
        window = undertest.MovingWindow(1)
        window.add_point({'test': 1})
        self.assertEqual(0, window.delta('test'))

    def test_delta_multiple_point(self):
        window = undertest.MovingWindow(2)
        window.add_point({'test': 1})
        window.add_point({'test': 2})
        window.add_point({'test': 3})
        self.assertEqual(1, window.delta('test'))

    def test_sum_empty_window(self):
        window = undertest.MovingWindow(1)
        self.assertEqual(0, window.sum(None))

    def test_sum_single_point(self):
        window = undertest.MovingWindow(1)
        window.add_point({'test': 1})
        self.assertEqual(1, window.sum('test'))

    def test_sum_multiple_points(self):
        window = undertest.MovingWindow(2)
        window.add_point({'test': 1})
        window.add_point({'test': 2})
        window.add_point({'test': 3})
        self.assertEqual(5, window.sum('test'))
