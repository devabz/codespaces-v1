from abc import ABC
from typing import Set
from src.time_base_seconds import TimeUnits


class Point(ABC):
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __repr__(self):
        return f'Point(x={self.x}, y={self.y})'


class ValueTable:
    def __init__(self, unit: float) -> None:
        self.data: Set[Point] = set()
        self.currentTime: float = 0
        self.nextTime: float = 0
        self.currentTemp: float = 0
        self.nextTemp: float = 0
        self.granularity: float = unit

    def add(self, t, v) -> None:
        self.data.add(Point(x=t, y=v))

    def pop(self):
        self.data = sorted(self.data, key=lambda x: x.x)[::-1]
        return self.data.pop()

    def init(self) -> None:
        p = self.pop()
        self.currentTime = p.x * self.granularity
        self.currentTemp = p.y
        p = self.pop()
        self.nextTime = p.x * self.granularity
        self.nextTemp = p.y
        #print(self.nextTime)

    def refresh(self, t: float) -> None:
        if t >= self.nextTime:
            self.currentTime = self.nextTime
            self.currentTemp = self.nextTemp
            try:
                p = self.pop()
                self.nextTime = p.x * self.granularity
                self.nextTemp = p.y

            except IndexError:  # Happens when the set self.data is empty
                self.nextTime = self.currentTime + self.granularity

    def linear(self, t: float) -> float:
        self.refresh(t=t)
        numerator = self.nextTime - self.currentTime
        return self.currentTemp + (t - self.currentTime) / (numerator + 1e-4) * (self.nextTemp - self.currentTemp)


def autofill_and_initiate_value_table(csv_path, value_table: ValueTable) -> ValueTable:
    import pandas as pd
    data = pd.read_csv(csv_path, index_col=0)
    for _ in data.values:
        x, y = _[:2]
        value_table.add(t=x, v=y)

    value_table.data = sorted(value_table.data, key=lambda point: point.x)
    value_table.init()
    return value_table


"""
   The Value Table has a method called linear that computes a float value. 
   The linear method is used by the main script, furthermore the Value Table also has an autofill and initiate method
   meant to read float values from a csv file and store them in the data attribute as instances of the Point class,
   and finish off by calling the initiate method which pops a point of the data attribute, and computes the inital
   time and temperatures.
"""

path = r'data/environment/temperature_data.csv'
value_table: ValueTable = autofill_and_initiate_value_table(csv_path=path, value_table=ValueTable(unit=TimeUnits.hour))

