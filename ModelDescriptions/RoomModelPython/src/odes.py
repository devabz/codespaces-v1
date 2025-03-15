import numpy as np
from src.heating_constants import *
from src.value_table import ValueTable, autofill_and_initiate_value_table


class ODE:
    def __init__(self, notation):
        self.notation = notation
        self.expr = {self.notation: f'{self.notation}_rate'}
        self.rate = 0
        self.state = 0

        self.dq = 0

    def update_state(self, state_value):
        self.state = state_value

    def dy_dt(self, t):
        pass

    @property
    def ics(self):
        return {self.notation: self.state}


class Boiler(ODE):
    def __init__(self, notation):
        super().__init__(notation=notation)
        self.state = 40

    def dy_dt(self, t):
        return 0


class Rate(ODE):
    def __init__(self, notation):
        super().__init__(notation=notation)

    def dy_dt(self, t):
        self.rate = 0
        return 0

    def set_state(self, state):
        self.state = state


class Environment(ODE):
    def __init__(self, notation):
        super().__init__(notation=notation)
        self.vTable = self.get_value_table()
        self.state = self.vTable.currentTemp

    def compute_temp(self, t):
        # return 5 * np.sin(2 * np.pi * (t/3600 - 10)/24) + 10
        return self.vTable.linear(t)

    def dy_dt(self, t):
        vt = self.compute_temp(t=t)
        self.rate = self.state - vt
        self.rate = (self.vTable.nextTemp - vt) / (self.vTable.nextTime - self.vTable.currentTime)
        return self.rate

    @staticmethod
    def get_value_table():
        path = r'data/environment/temperature_data.csv'
        return autofill_and_initiate_value_table(csv_path=path, value_table=ValueTable(unit=TimeUnits.hour))

    def refresh_value_table(self):
        self.vTable = self.get_value_table()


class Room(ODE):
    def __init__(self, notation):
        super().__init__(notation=notation)
        self.state = TEMP_NIGHT_NOMINAL
        self.open = False

    def dy_dt(self, t):
        radiator_power = K_RADIATOR * A_RADIATOR * (radiator.state - self.state)
        wall_loss_rate = A_WALL * K_WALL * (self.state - env.state)
        window_loss_rate = A_WINDOW * {False: U.wi_closed, True: U.wi_open}[self.open] * (self.state - env.state)
        self.rate = (radiator_power - window_loss_rate - wall_loss_rate) / (C_AIR * D_AIR * V_ROOM)
        return self.rate

    def set_open(self, open):
        self.open = open


class Radiator(ODE):
    def __init__(self, notation, hyst=1):
        super().__init__(notation=notation)
        self.on: bool = False
        self.state = TEMP_NIGHT_NOMINAL
        self.tempNominal = TEMP_NIGHT_NOMINAL
        self.hyst = hyst
        self.temp_diff = 0

    def dy_dt(self, t):
        opening = self.opening()
        self.dq = (self.state - room.state) * A_RADIATOR * U.he
        dt_gain = opening * (F_WATER / V_RADIATOR) * (boiler.state - self.state)
        dt_loss = self.dq / (D_AIR * C_WATER * V_RADIATOR)
        self.rate = dt_gain - dt_loss
        return self.rate

    def opening(self):
        self.temp_diff = self.tempNominal - room.state
        if self.temp_diff <= 0:
            res = 0

        elif self.temp_diff >= self.hyst:
            res = 1

        else:
            res = self.temp_diff / self.hyst

        return res


class WaterRadiator(Radiator):
    def __init__(self, notation, init_temp, init_hyst):
        super().__init__(notation=notation, hyst=init_hyst)
        self.hyst = init_hyst
        self.state = init_temp

    def dy_dt(self, t):
        temp_in = boiler.state
        opening = self.opening()
        T1 = opening * (F_WATER / V_RADIATOR_WATER) * (temp_in - self.state)
        T2 = K_RADIATOR * A_RADIATOR * (room.state - self.state) / (V_RADIATOR_WATER * D_WATER * C_WATER)
        self.rate = T1 + T2
        return self.rate


class ElectricalRadiator(Radiator):
    def __init__(self, notation, init_hyst, init_temp):
        super().__init__(notation=notation, hyst=init_hyst)
        self.state = init_temp
        self.hyst = init_hyst

    def dy_dt(self, t):
        inpPower = (self.opening() * P_RADIATOR) / (C_WATER * V_RADIATOR_WATER * D_WATER)
        outPower = K_RADIATOR * A_RADIATOR * (room.state - self.state) / (V_RADIATOR_WATER * D_WATER * C_WATER)
        self.rate = inpPower + outPower
        return self.rate


TEMP_NIGHT_NOMINAL = 15
TEMP_DAY_NOMINAL = 22

# Instantiate the ODE's
env = Environment(notation='env')
boiler = Boiler(notation='boiler')
room = Room(notation='room')
water_radiator = WaterRadiator(notation='radiator', init_temp=TEMP_NIGHT_NOMINAL, init_hyst=1)
electric_radiator = ElectricalRadiator(notation='radiator', init_temp=TEMP_NIGHT_NOMINAL, init_hyst=0.2)
radiator = [water_radiator, electric_radiator][0]
window_rate = Rate(notation='window')
opening_rate = Rate(notation='opening')
wanted_temperature = Rate(notation='wanted')
wanted_temperature.state = TEMP_NIGHT_NOMINAL  # Set the initial states
room.state = TEMP_NIGHT_NOMINAL  # Set the initial states
