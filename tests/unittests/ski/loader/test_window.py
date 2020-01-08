"""
"""

import unittest

from ski.loader.window import *

# Set up logger
logging.basicConfig()
log.setLevel(logging.INFO)


class TestBatchWindow(unittest.TestCase):
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

        batch.load_points(new_data, lambda body, tail: self.fail('Batch not full'))
        self.assertEqual(batch_size, len(batch.body))
        self.assertEqual(0, len(batch.tail))
        self.assertListEqual(new_data, batch.body)

    def test_BatchWindow_load_points_batch_filled(self):
        body_size = 10
        overlap = 3
        batch_size = body_size

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda body, tail: self.assertEqual(body_size, len(body)))
        self.assertEqual(0, len(batch.body))
        self.assertEqual(overlap, len(batch.tail))
        self.assertListEqual(new_data[-overlap:], batch.tail)

    def test_BatchWindow_load_points_batch_filled_no_function(self):
        body_size = 10
        overlap = 3
        batch_size = body_size

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data)
        self.assertEqual(0, len(batch.body))
        self.assertEqual(overlap, len(batch.tail))
        self.assertListEqual(new_data[-overlap:], batch.tail)

    def test_BatchWindow_load_points_batch_filled_twice(self):
        body_size = 10
        overlap = 3
        batch_size = body_size * 2

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda body, tail: self.assertEqual(body_size, len(body)))
        self.assertEqual(0, len(batch.body))
        self.assertEqual(overlap, len(batch.tail))
        self.assertListEqual(new_data[-overlap:], batch.tail)

    def test_BatchWindow_load_points_batch_filled_and_overflow(self):
        body_size = 10
        overlap = 3
        overflow = 5
        batch_size = body_size + overflow

        batch = BatchWindow(body_size=body_size, overlap=overlap)
        new_data = [x for x in range(0, batch_size)]

        batch.load_points(new_data, lambda body, tail: self.assertEqual(body_size, len(body)))
        self.assertEqual(overflow, len(batch.body))
        self.assertEqual(overlap, len(batch.tail))
        self.assertListEqual(new_data[-overlap - overflow:-overflow], batch.tail)

    """
    PointWindow.extract(window_key)
    """
    def test_PointWindow_extract_forwards(self):
        head = [x for x in range(0, 10)]

        window = PointWindow(head=head)
        window.process()

        extract_size = 5

        extract = window.extract(WindowKey.FORWARD, extract_size)
        self.assertEqual(extract_size, len(extract))
        self.assertListEqual(head[:extract_size], extract)

    def test_PointWindow_extract_forwards_short_head(self):
        head = [x for x in range(0, 10)]

        window = PointWindow(head=head)
        window.process()

        extract_size = 15

        extract = window.extract(WindowKey.FORWARD, extract_size)
        self.assertEqual(len(head), len(extract))
        self.assertListEqual(head, extract)

    def test_PointWindow_extract_backwards(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail)
        window.process()

        extract_size = 5

        extract = window.extract(WindowKey.BACKWARD, extract_size)
        self.assertEqual(extract_size, len(extract))
        self.assertListEqual(tail[-4:] + [head[0]], extract)

    def test_PointWindow_extract_backwards_short_tail(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail)
        window.process()

        extract_size = 15

        extract = window.extract(WindowKey.BACKWARD, extract_size)
        self.assertEqual(len(tail) + 1, len(extract))
        self.assertListEqual(tail + [head[0]], extract)

    def test_PointWindow_extract_midpoint(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail)
        window.process()

        extract_size = 5

        extract = window.extract(WindowKey.MIDPOINT, extract_size)
        self.assertEqual(extract_size, len(extract))
        self.assertListEqual(tail[-2:] + head[:3], extract)

    def test_PointWindow_extract_midpoint_short_head(self):
        head = [x for x in range(0, 5)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail)
        window.process()

        extract_size = 15

        extract = window.extract(WindowKey.MIDPOINT, extract_size)
        self.assertEqual(floor(extract_size / 2) + len(head), len(extract))
        self.assertListEqual(tail[-7:] + head, extract)

    def test_PointWindow_extract_midpoint_short_tail(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 5)]

        window = PointWindow(head=head, tail=tail)
        window.process()

        extract_size = 15

        extract = window.extract(WindowKey.MIDPOINT, extract_size)
        self.assertEqual(floor(extract_size / 2) + 1 + len(tail), len(extract))
        self.assertListEqual(tail + head[:8], extract)

    """
    PointWindow.load_points(points)
    """
    def test_PointWindow_load_points(self):
        # Prepare data
        w = PointWindow()
        points = [x for x in range(5)]
        w.load_points(points)

        self.assertListEqual([0, 1, 2, 3, 4], w.head)
        self.assertListEqual([], w.tail)

    def test_PointWindow_load_points_to_existing_head(self):
        # Prepare data
        w = PointWindow()
        points = [x for x in range(5)]
        w.head += [x for x in range(5)]
        w.tail += [x for x in range(5)]

        w.load_points(points)

        self.assertEqual(10, len(w.head))
        self.assertEqual(5, len(w.tail))

    """
    PointWindow.process()
    """
    def test_PointWindow_process(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail, head_length=10)

        self.assertTrue(window.process())

    def test_PointWindow_process_points_remain(self):
        head = [x for x in range(0, 15)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail, head_length=10)

        self.assertTrue(window.process())

    def test_PointWindow_process_draining(self):
        head = [x for x in range(0, 10)]
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail, head_length=10)
        window.drain = True

        self.assertTrue(window.process())

    def test_PointWindow_process_empty_head(self):
        head = []
        tail = [x for x in range(0, 10)]

        window = PointWindow(head=head, tail=tail, head_length=10)

        self.assertFalse(window.process())


if __name__ == '__main__':
    unittest.main()
