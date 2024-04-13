from typing import Callable

import tibber

from smartthings.api import Api
from smartthings.capabilities import FlowTemperatureCapability
from smartthings.devices import Device
from utils.moving_average import MovingAverage
from wingst import settings


class PowerMeter:
    def __init__(self, track_last_n_measurements: int = 50):
        account = tibber.Account(settings.TOKEN_TIBBER)
        self.home = [home for home in account.homes if home.id == settings.HOME_ID_TIBBER][0]
        self.callback_registrator = self.home.event("live_measurement")
        self.track_last_n_measurements = track_last_n_measurements
        self.measurements_balance = MovingAverage(size=track_last_n_measurements)

    def start_measuring(self, measurement_callback: Callable, exit_condition: Callable):
        async def append_measurement(data):
            consumption = data.power
            production = data.power_production
            self.measurements_balance.append(int(consumption - production))

        self.callback_registrator(append_measurement)
        self.callback_registrator(measurement_callback)

        self.home.start_live_feed(user_agent="UserAgent/0.0.1", exit_condition=exit_condition)

    def moving_average_power_balance(self):
        return self.measurements_balance.average()


class HeatPump(Device):
    def __init__(self):
        api = Api(settings.TOKEN_SMARTTHINGS)
        super().__init__(api=api, device_id=settings.HEAT_PUMP_DEVICE_ID)
        self.module_water = settings.HEAT_PUMP_MODULE_WATER
        self.module_heating = settings.HEAT_PUMP_MODULE_HEATING
        self.flow_temperature_capability = FlowTemperatureCapability

    def set_flow_temperature(self, temperature: int):
        command = self.flow_temperature_capability.set_flow_temperature(
            temperature, module=settings.HEAT_PUMP_MODULE_HEATING
        )
        self.execute_command(command)
        command = self.flow_temperature_capability.set_flow_temperature(
            temperature, module=settings.HEAT_PUMP_MODULE_WATER
        )
        self.execute_command(command)
