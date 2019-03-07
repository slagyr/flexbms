import unittest

from bms.cells import Cells
from test.mock_bq import MockBQ


class CellsTest(unittest.TestCase):

    def setUp(self):
        self.bq = MockBQ()
        self.cells = Cells(self.bq, 10)

    def createCellsAndTest(self, count):
        cells = Cells(self.bq, count)
        self.assertEqual(count, cells.count)
        self.assertEqual(count, len(cells.voltages))
        for i in cells.voltages:
            self.assertEqual(0, cells.voltages[i])
        return cells

    def test_creation_with_15_cells(self):
        cells = self.createCellsAndTest(15)
        self.assertEqual((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15), cells.ids)

    def test_creation_with_14_cells(self):
        cells = self.createCellsAndTest(14)
        self.assertEqual((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15), cells.ids)

    def test_creation_with_13_cells(self):
        cells = self.createCellsAndTest(13)
        self.assertEqual((1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15), cells.ids)

    def test_creation_12_cells(self):
        cells = self.createCellsAndTest(12)
        self.assertEqual((1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15), cells.ids)

    def test_creation_11_cells(self):
        cells = self.createCellsAndTest(11)
        self.assertEqual((1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 15), cells.ids)

    def test_creation_10_cells(self):
        cells = self.createCellsAndTest(10)
        self.assertEqual((1, 2, 3, 5, 6, 8, 10, 12, 13, 15), cells.ids)

    def test_creation_9_cells(self):
        cells = self.createCellsAndTest(9)
        self.assertEqual((1, 2, 5, 6, 8, 10, 12, 13, 15), cells.ids)

    def test_read_voltages(self):
        self.bq.voltages = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
        self.cells.update_voltages()
        self.assertEqual(1.1, self.cells.voltages[0])
        self.assertEqual(1.2, self.cells.voltages[1])
        self.assertEqual(1.3, self.cells.voltages[2])
        self.assertEqual(1.5, self.cells.voltages[3])
        self.assertEqual(1.6, self.cells.voltages[4])
        self.assertEqual(1.8, self.cells.voltages[5])
        self.assertEqual(2.0, self.cells.voltages[6])
        self.assertEqual(2.2, self.cells.voltages[7])
        self.assertEqual(2.3, self.cells.voltages[8])
        self.assertEqual(2.5, self.cells.voltages[9])
