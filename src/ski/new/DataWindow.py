
__author__ = 'Steve Roberts'
__version__ = 1.0

import unittest


class DataWindow:

    capacity = 0
    data = []

    def __init__(self, capacity):
        self.capacity = capacity
        self.data = []

    def add(self, value):
        data = self.data[-(self.capacity - 1):] + [value]
        self.data = data
        print(self.data)

    def avg(self):
        return sum(self.data) / len(self.data)

    def max(self):
        return max(self.data)

    def min(self):
        return min(self.data)


class TestDataWindow(unittest.TestCase):

    def test_avg(self):

        w = DataWindow(3)

        w.add(2.0)
        self.assertEqual(w.avg(), 2.0)

        w.add(2.0)
        self.assertEqual(w.avg(), 2.0)

        w.add(5.0)
        self.assertEqual(w.avg(), 3.0)

        w.add(5.0)
        self.assertEqual(w.avg(), 4.0)

        w.add(5.0)
        self.assertEqual(w.avg(), 5.0)