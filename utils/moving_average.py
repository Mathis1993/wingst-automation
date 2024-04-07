from collections import deque


class MovingAverage:
    def __init__(self, size: int):
        self.size = size
        self.current_values = deque(maxlen=size)
        self.sum = 0

    def append(self, value: int):
        if len(self.current_values) == self.size:
            self.sum -= self.current_values[0]
        self.current_values.append(value)
        self.sum += value

    def average(self):
        if len(self.current_values) != self.size:
            return None
        return int(self.sum / len(self.current_values))
