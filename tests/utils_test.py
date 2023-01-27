import unittest
import ski.utils as undertest


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
