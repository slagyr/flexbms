# From: http: // www.rapidonline.com / pdf / 61 - 0500e.pdf
THERM_TABLE = [(329500, -50.0),
               (247700, -45.0),
               (188500, -40.0),
               (144100, -35.0),
               (111300, -30.0),
               (86430, -25.0),
               (67770, -20.0),
               (53410, -15.0),
               (42470, -10.0),
               (33900, -5.0),
               (27280, 0.0),
               (22050, 5.0),
               (17960, 10.0),
               (14690, 15.0),
               (12090, 20.0),
               (10000, 25.0),
               (8313, 30.0),
               (6940, 35.0),
               (5827, 40.0),
               (4911, 45.0),
               (4160, 50.0),
               (3536, 55.0),
               (3020, 60.0),
               (2588, 65.0),
               (2228, 70.0),
               (1924, 75.0),
               (1668, 80.0),
               (1451, 85.0),
               (1266, 90.0),
               (1108, 95.0),
               (973, 100.0),
               (857, 105.0),
               (757, 110.0)]

class Temps:
    def __init__(self, bq):
        self.bq = bq
        self.temp1 = 0
        self.temp2 = 0
        self.temp3 = 0
        self.loaded = False

    def load(self):
        my = self
        if my.loaded:
            return
        my.temp1 = my.read_temp1()
        my.temp2 = my.read_temp2()
        my.temp3 = my.read_temp3()
        my.loaded = True

    def therm_r_to_c(self, r):
        table = THERM_TABLE
        (pr, pt) = table[0]
        if r >= pr:
            return pt
        for i in range(1, len(table)):
            (nr, nt) = table[i]
            if r >= nr:
                diff = r - nr
                perc = diff / (pr - nr)
                return nt - ((nt - pt) * perc)
            else:
                pr = nr
                pt = nt
        return table[-1][1]

    def read_temp1(self):
        r = self.bq.therm_r(0)
        return self.therm_r_to_c(r)

    def read_temp2(self):
        r = self.bq.therm_r(1)
        return self.therm_r_to_c(r)

    def read_temp3(self):
        r = self.bq.therm_r(2)
        return self.therm_r_to_c(r)

    def expire(self):
        self.loaded = False
