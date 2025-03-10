import unittest

from bms.cells import Cells
from test.mock_bq import MockBQ


class CellsTest(unittest.TestCase):

    def setUp(self):
        self.bq = MockBQ()
        self.conf = self.bq.conf
        self.cells = Cells(self.conf, self.bq, 10)

    def test_bq(self):
        self.assertEqual(self.bq, self.cells.bq)

    def createCellsAndTest(self, count, ids):
        cells = Cells(self.conf, self.bq, count)
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

    def test_connections(self):
        self.assertEqual(None, self.cells[0].left)
        self.assertEqual(self.cells[1], self.cells[0].right)

        self.assertEqual(self.cells[0], self.cells[1].left)
        self.assertEqual(self.cells[2], self.cells[1].right)

        self.assertEqual(self.cells[1], self.cells[2].left)
        self.assertEqual(self.cells[3], self.cells[2].right)

        self.assertEqual(self.cells[2], self.cells[3].left)
        self.assertEqual(None, self.cells[3].right)

        self.assertEqual(None, self.cells[4].left)
        self.assertEqual(self.cells[5], self.cells[4].right)

        self.assertEqual(self.cells[4], self.cells[5].left)
        self.assertEqual(self.cells[6], self.cells[5].right)

        self.assertEqual(self.cells[5], self.cells[6].left)
        self.assertEqual(None, self.cells[6].right)

        self.assertEqual(None, self.cells[7].left)
        self.assertEqual(self.cells[8], self.cells[7].right)

        self.assertEqual(self.cells[7], self.cells[8].left)
        self.assertEqual(self.cells[9], self.cells[8].right)

        self.assertEqual(self.cells[8], self.cells[9].left)
        self.assertEqual(None, self.cells[9].right)

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
        cells = Cells(self.conf, self.bq, 15)
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
        cells = Cells(self.conf, self.bq, 15)
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
        cells = Cells(self.conf, self.bq, 15)
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
        cells = Cells(self.conf, self.bq, 9)
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

    def test_reset_balancing(self):
        self.cells[1].set_balance(self.bq, True)
        self.cells[3].set_balance(self.bq, True)
        self.cells[5].set_balance(self.bq, True)

        self.cells.reset_balancing()

        for cell in self.cells:
            self.assertEqual(False, cell.balancing)
        self.assertEqual([], self.bq.balancing_cells)

    def test_has_low_voltage(self):
        for cell in self.cells:
            cell.voltage = 3.6

        self.assertEqual(False, self.cells.has_low_voltage())

        self.cells[5].voltage = 2.5
        self.assertEqual(True, self.cells.has_low_voltage())

        self.cells[5].voltage = 2.51
        self.assertEqual(False, self.cells.has_low_voltage())

        self.cells[8].voltage = 2.49
        self.assertEqual(True, self.cells.has_low_voltage())


    def test_fully_charged(self):
        self.conf.CELL_FULL_V = 4.1
        for cell in self.cells:
            cell.voltage = 4.2

        self.assertEqual(True, self.cells.fully_charged())

        self.cells[5].voltage = 4.0
        self.assertEqual(False, self.cells.fully_charged())
        self.assertEqual(True, self.cells.fully_charged(-0.1))

        self.cells[5].voltage = 4.1
        self.assertEqual(True, self.cells.fully_charged())
        self.assertEqual(False, self.cells.fully_charged(0.1))

        self.cells[2].voltage = 4.0
        self.assertEqual(False, self.cells.fully_charged())
        self.assertEqual(True, self.cells.fully_charged(-0.1))


    def test_any_cell_full(self):
        self.conf.CELL_FULL_V = 4.1
        for cell in self.cells:
            cell.voltage = 4.0

        self.assertEqual(False, self.cells.any_cell_full())
        self.assertEqual(True, self.cells.any_cell_full(-0.11))

        self.cells[5].voltage = 4.2
        self.assertEqual(True, self.cells.any_cell_full())
        self.assertEqual(False, self.cells.any_cell_full(0.2))

        self.cells[5].voltage = 4.1
        self.assertEqual(True, self.cells.any_cell_full())
        self.assertEqual(False, self.cells.any_cell_full(0.1))

        self.cells[5].voltage = 4.09
        self.assertEqual(False, self.cells.any_cell_full())

        self.cells[2].voltage = 4.1
        self.assertEqual(True, self.cells.any_cell_full())

    def test_load(self):
        self.cells.load()
        self.assertEqual(True, self.bq.voltages_loaded)

    def test_cache_set_and_reset(self):
        self.assertEqual(False, self.cells.loaded)
        self.cells.load()
        self.assertEqual(True, self.cells.loaded)
        self.cells.expire()
        self.assertEqual(False, self.cells.loaded)


