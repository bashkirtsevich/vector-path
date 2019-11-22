class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __iadd__(self, other):
        self._x += other.x
        self._y += other.y
        return self

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def c(self):
        return self._x + self._y * 1j
