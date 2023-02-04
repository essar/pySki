from statistics import mean


class MovingWindow:

    def __init__(self, size) -> None:
        self.size = size
        self.data = []

    def add_point(self, point) -> None:
        self.data.insert(0, point)
        self.data = self.data[0:self.size]

    def average(self, key:str) -> int:
        if len(self.data) < 1:
            return 0
        return mean([x[key] for x in self.data])
    
    def delta(self, key:str) -> int:
        if len(self.data) < 2:
            return 0
        return self.data[0][key] - self.data[-1][key]

    def first(self):
        return self.data[0] if len(self.data) > 0 else None

    def last(self):
        return self.data[-1] if len(self.data) > 0 else None

    def sum(self, key:str) -> int:
        if len(self.data) < 1:
            return 0
        return sum((x[key] for x in self.data))
