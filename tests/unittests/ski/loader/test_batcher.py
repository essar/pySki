"""
"""

import unittest

from ski.loader.batcher import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.DEBUG)


class TestBatcher(unittest.TestCase):
    """
    BatchWindow()
    """
    def test_BatchWindow_overlap_exceeds_size(self):
        body_size = 10
        overlap = body_size + 1

        with self.assertRaises(ValueError):
            BatchWindow(body_size=body_size, overlap=overlap)

    """
    BatchWindow.load_points(points)
    """
    def test_BatchWindow_load_points(self):
        body_size = 10
        overlap = 3
        batch_size = (body_size - 1)

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda pts: self.fail('Batch not full'))
        self.assertEqual(batch_size, len(batch.body))
        self.assertListEqual(new_data, batch.body)

    def test_BatchWindow_load_points_batch_filled(self):
        body_size = 10
        overlap = 3
        batch_size = body_size

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda pts: self.assertEqual(body_size, len(pts)))
        self.assertEqual(overlap, len(batch.body))

    def test_BatchWindow_load_points_batch_filled_no_function(self):
        body_size = 10
        overlap = 3
        batch_size = body_size

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data)
        self.assertEqual(overlap, len(batch.body))

    def test_BatchWindow_load_points_batch_filled_twice(self):
        body_size = 10
        overlap = 3
        batch_size = body_size * 2 - overlap

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda pts: self.assertEqual(body_size, len(pts)))
        self.assertEqual(overlap, len(batch.body))

    def test_BatchWindow_load_points_batch_filled_and_overflow(self):
        body_size = 10
        overlap = 3
        overflow = 5
        batch_size = body_size + overflow

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda pts: self.assertEqual(body_size, len(pts)))
        self.assertEqual(overlap + overflow, len(batch.body))


if __name__ == '__main__':
    unittest.main()
