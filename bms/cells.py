from bms.conf import *


class Cell:
    def __init__(self, index, id):
        self.index = index
        self.id = id
        self.voltage = 0

    def soc(self):
        return (self.voltage - CELL_MIN_V) / (CELL_MAX_V - CELL_MIN_V)

    def adjacent_to(self, other):
        if abs(other.index - self.index) != 1:
            return False
        elif (self.id == 5 and other.id == 6) or (self.id == 6 and other.id == 5):
            return False
        elif (self.id == 10 and other.id == 11) or (self.id == 11 and other.id == 10):
            return False
        else:
            return True



def ids_to_cells(ids):
    cells = []
    for i in range(len(ids)):
        cells.append(Cell(i, ids[i]))
    return cells


class Cells:
    def __init__(self, bq, count):
        self.bq = bq
        self.count = count
        if count == 15:
            self._cells = ids_to_cells((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
        elif count == 14:
            self._cells = ids_to_cells((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15))
        elif count == 13:
            self._cells = ids_to_cells((1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15))
        elif count == 12:
            self._cells = ids_to_cells((1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15))
        elif count == 11:
            self._cells = ids_to_cells((1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 15))
        elif count == 10:
            self._cells = ids_to_cells((1, 2, 3, 5, 6, 7, 10, 11, 12, 15))
        elif count == 9:
            self._cells = ids_to_cells((1, 2, 5, 6, 7, 10, 11, 12, 15))

    def __getitem__(self, i):
        return self._cells[i]

    def by_id(self, id):
        for cell in self:
            if cell.id == id:
                return cell

    def setup(self):
        pass

    def update_voltages(self):
        for cell in self:
            v = self.bq.cell_voltage(cell.id)
            cell.voltage = v

    def serial_voltage(self):
        sum = 0.0
        for cell in self:
            sum += cell.voltage
        return sum

    def soc(self):
        result = 2
        for cell in self:
            soc = cell.soc()
            if soc < result:
                result = soc
        return result

    def update_balancing(self):
        to_balance = self.cells_to_balance()
        last = None
        non_adjacent = []
        for cell in to_balance:
            if not last or not cell.adjacent_to(last):
                last = cell
                non_adjacent.append(cell)

        ids = []
        for cell in non_adjacent:
            ids.append(cell.id)
        self.bq.set_balance_cells(ids)

    def cells_to_balance(self):
        cells = sorted(self._cells, key=lambda c: c.voltage)
        min_v = cells[0].voltage
        cells.reverse()
        to_balance = []
        for cell in cells:
            if cell.voltage - min_v > CELL_BALANCE_THRESH:
                to_balance.append(cell)
            else:
                break
        return to_balance







