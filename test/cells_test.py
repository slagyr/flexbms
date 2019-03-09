import unittest

from bms.cells import Cells
from test.mock_bq import MockBQ


class CellsTest(unittest.TestCase):

    def setUp(self):
        self.bq = MockBQ()
        self.cells = Cells(self.bq, 10)

    def createCellsAndTest(self, count, ids):
        cells = Cells(self.bq, count)
        self.assertEqual(count, cells.count)

        self.assertEqual(cells.count, len(ids))
        for i in range(cells.count):
            self.assertEqual(ids[i], cells[i].id)

        for cell in cells:
            self.assertEqual(0, cell.voltage)


    def test_creation_with_15_cells(self):
        self.createCellsAndTest(15, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    def test_creation_with_14_cells(self):
        self.createCellsAndTest(14, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15))

    def test_creation_with_13_cells(self):
        self.createCellsAndTest(13, (1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15))

    def test_creation_12_cells(self):
        self.createCellsAndTest(12, (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15))

    def test_creation_11_cells(self):
        self.createCellsAndTest(11, (1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 15))

    def test_creation_10_cells(self):
        self.createCellsAndTest(10, (1, 2, 3, 5, 6, 7, 10, 11, 12, 15))

    def test_creation_9_cells(self):
        self.createCellsAndTest(9, (1, 2, 5, 6, 7, 10, 11, 12, 15))

    def test_by_id(self):
        self.assertEqual(0, self.cells.by_id(1).index)
        self.assertEqual(1, self.cells.by_id(2).index)
        self.assertEqual(2, self.cells.by_id(3).index)
        self.assertEqual(None, self.cells.by_id(4))
        self.assertEqual(3, self.cells.by_id(5).index)
        self.assertEqual(4, self.cells.by_id(6).index)
        self.assertEqual(5, self.cells.by_id(7).index)
        self.assertEqual(None, self.cells.by_id(8))
        self.assertEqual(None, self.cells.by_id(9))
        self.assertEqual(6, self.cells.by_id(10).index)
        self.assertEqual(7, self.cells.by_id(11).index)
        self.assertEqual(8, self.cells.by_id(12).index)
        self.assertEqual(None, self.cells.by_id(13))
        self.assertEqual(None, self.cells.by_id(14))
        self.assertEqual(9, self.cells.by_id(15).index)

    def test_read_voltages(self):
        self.bq.voltages = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
        self.cells.update_voltages()
        self.assertEqual(1.1, self.cells[0].voltage)
        self.assertEqual(1.2, self.cells[1].voltage)
        self.assertEqual(1.3, self.cells[2].voltage)
        self.assertEqual(1.5, self.cells[3].voltage)
        self.assertEqual(1.6, self.cells[4].voltage)
        self.assertEqual(1.7, self.cells[5].voltage)
        self.assertEqual(2.0, self.cells[6].voltage)
        self.assertEqual(2.1, self.cells[7].voltage)
        self.assertEqual(2.2, self.cells[8].voltage)
        self.assertEqual(2.5, self.cells[9].voltage)

    def test_cell_state_of_charge(self):
        self.cells[0].voltage = 2.4
        self.assertAlmostEqual(-0.06, self.cells[0].soc(), 2)
        self.cells[1].voltage = 2.5
        self.assertAlmostEqual(0.0, self.cells[1].soc(), 2)
        self.cells[2].voltage = 2.6
        self.assertAlmostEqual(0.06, self.cells[2].soc(), 2)
        self.cells[3].voltage = 3.6
        self.assertAlmostEqual(0.65, self.cells[3].soc(), 2)
        self.cells[4].voltage = 4.1
        self.assertAlmostEqual(0.94, self.cells[4].soc(), 2)
        self.cells[5].voltage = 4.2
        self.assertAlmostEqual(1.00, self.cells[5].soc(), 2)
        self.cells[6].voltage = 4.3
        self.assertAlmostEqual(1.06, self.cells[6].soc(), 2)

    def test_pack_soc(self):
        for cell in self.cells:
            cell.voltage = 4.0
        self.cells[2].voltage = 3.6
        self.assertAlmostEqual(self.cells[2].soc(), self.cells.soc(), 2)
        
    def test_serial_voltage(self):
        for cell in self.cells:
            cell.voltage = 3.6
        self.assertAlmostEqual(36.0, self.cells.serial_voltage(), 2)

    def test_balancing_with_all_cells_within_threshold(self):
        cells = Cells(self.bq, 15)
        for i in range(15):
            cells[i].voltage = 3.654
        cells.update_balancing()
        self.assertEqual([], self.bq.balancing_cells)

        cells[0].voltage = 3.655
        cells[2].voltage = 3.653
        cells.update_balancing()
        for cell in cells:
            self.assertFalse(cell.balancing)
        self.assertEqual([], self.bq.balancing_cells)

    def test_balancing_with_non_adjacent_cells(self):
        cells = Cells(self.bq, 15)
        for i in range(15):
            cells[i].voltage = 3.654

        cells[0].voltage = 3.8
        cells[2].voltage = 3.9
        cells[10].voltage = 4.0
        cells.update_balancing()
        self.assertTrue(cells[0].balancing)
        self.assertTrue(cells[2].balancing)
        self.assertTrue(cells[10].balancing)
        self.assertEqual([11, 3, 1], self.bq.balancing_cells)

    def test_wont_balance_adjacent_cells(self):
        cells = Cells(self.bq, 15)
        for i in range(15):
            cells[i].voltage = 3.654

        cells[14].voltage = 4.0
        cells[13].voltage = 4.0
        cells[12].voltage = 4.0
        cells[11].voltage = 4.0
        cells[10].voltage = 4.0
        cells[9].voltage = 4.0
        cells[8].voltage = 4.0

        cells.update_balancing()
        self.assertEqual([15, 13, 11, 10], self.bq.balancing_cells)

    def test_wont_balance_adjacent_cells_9(self):
        cells = Cells(self.bq, 9)
        for i in range(9):
            cells[i].voltage = 3.654

        cells[8].voltage = 4.0
        cells[7].voltage = 4.0
        cells[6].voltage = 4.0
        cells[5].voltage = 4.0
        cells[4].voltage = 4.0
        cells[3].voltage = 4.0
        cells[2].voltage = 4.0

        cells.update_balancing()
        self.assertEqual([15, 11, 10, 6, 5], self.bq.balancing_cells)
