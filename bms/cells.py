from bms.conf import CONF


class Cell:
    def __init__(self, index, id):
        self.index = index
        self.id = id
        self.voltage = 0
        self.balancing = False
        self.left = None
        self.right = None

    def soc(self):
        return (self.voltage - CONF.CELL_MIN_V) / (CONF.CELL_MAX_V - CONF.CELL_MIN_V)

    def adjacent_to(self, other):
        if abs(other.index - self.index) != 1:
            return False
        elif (self.id == 5 and other.id == 6) or (self.id == 6 and other.id == 5):
            return False
        elif (self.id == 10 and other.id == 11) or (self.id == 11 and other.id == 10):
            return False
        else:
            return True

    def should_balance(self, min_v):
        my = self
        if (my.voltage - min_v) <= CONF.BALANCE_THRESH:
            return False
        if my.left and my.left.balancing and my.left.voltage >= my.voltage:
            return False
        if my.right and my.right.balancing and my.right.voltage >= my.voltage:
            return False
        return True

    def set_balance(self, bq, on):
        bq.set_balance_cell(self.id, on)
        self.balancing = on


def ids_to_cells(ids):
    cells = []
    for i in range(len(ids)):
        cells.append(Cell(i, ids[i]))
    return cells


class Cells:
    def __init__(self, bq, count):
        self.bq = bq
        self.count = count
        self.loaded = False
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

        for cell in self:
            self.connect_adjacent_cells(cell)

    def __getitem__(self, i):
        return self._cells[i]

    def by_id(self, id):
        for cell in self:
            if cell.id == id:
                return cell

    def setup(self):
        pass

    def serial_voltage(self):
        sum = 0.0
        for cell in self:
            sum += cell.voltage
        return sum

    def max_serial_voltage(self):
        return self.count * CONF.CELL_MAX_V

    def soc(self):
        result = 2
        for cell in self:
            soc = cell.soc()
            if soc < result:
                result = soc
        return result

    def connect_adjacent_cells(self, cell):
        i = cell.index
        id = cell.id
        cell.left = self[i - 1] if id != 1 and id != 6 and id != 11 else None
        cell.right = self[i + 1] if id != 5 and id != 10 and id != 15 else None

    def update_balancing(self):
        cells = sorted(self._cells, key=lambda c: c.voltage)
        min_v = cells[0].voltage
        cells.reverse()
        for cell in cells:
            should_balance = cell.should_balance(min_v)
            if should_balance != cell.balancing:
                cell.set_balance(self.bq, should_balance)

    def reset_balancing(self):
        for cell in self:
            cell.set_balance(self.bq, False)

    def has_low_voltage(self):
        for cell in self:
            if cell.voltage <= CONF.CELL_MIN_V:
                return True
        return False

    def fully_charged(self):
        for cell in self:
            if cell.voltage < CONF.CELL_FULL_V - 0.01:
                return False
        return True

    def any_cell_full(self):
        for cell in self:
            if cell.voltage >= CONF.CELL_FULL_V:
                return True
        return False

    def load(self):
        if self.loaded:
            return
        self.bq.load_cell_voltages(self)
        self.loaded = True

    def expire(self):
        self.loaded = False
