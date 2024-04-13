import logging
import time
from dataclasses import dataclass
from datetime import datetime

from wingst.devices import HeatPump, PowerMeter


@dataclass
class Config:
    heat_pump_flow_temperature_power_production: int
    heat_pump_flow_temperature_power_consumption: int
    power_production_threshold: int
    power_consumption_threshold: int
    track_last_n_power_measurements: int


class Commander:
    def __init__(self, config: Config):
        self.config = config
        self.power_meter = PowerMeter(
            track_last_n_measurements=config.track_last_n_power_measurements
        )
        self.heat_pump = HeatPump()
        self.power_production_mode = False
        self.last_heat_pump_status_check = datetime.now()
        self.last_moving_average_log = datetime.now()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def command_heatpump(self):
        while True:
            self._command_heatpump()

    def _command_heatpump(self):
        online = self.heat_pump.online()
        while not online:
            self.logger.info("Heat pump is offline. Waiting for 15 minutes.")
            time.sleep(15 * 60)
            online = self.heat_pump.online()

        self.logger.info("Heat pump is online.")
        self.restore_default_flow_temperature()
        self.logger.info("Starting power measurement.")

        async def heatpump_power_measurement_callback(data):
            moving_average_balance = self.power_meter.moving_average_power_balance()
            if not moving_average_balance:
                self.logger.info("No moving average balance available (yet).")
                return

            if (datetime.now() - self.last_moving_average_log).seconds > 5 * 60:
                self.last_moving_average_log = datetime.now()
                self.logger.info(f"Moving average balance: {moving_average_balance} Watts.")

            if (
                moving_average_balance < self.config.power_production_threshold
                and not self.power_production_mode
            ):
                self.power_production_mode = True
                self.logger.info(
                    f"Power production at {moving_average_balance}, threshold exceeded. "
                    f"Setting heat pump flow temperature to "
                    f"{self.config.heat_pump_flow_temperature_power_production}°C."
                )
                self.heat_pump.set_flow_temperature(
                    self.config.heat_pump_flow_temperature_power_production
                )

            if (
                moving_average_balance > self.config.power_consumption_threshold
                and self.power_production_mode
            ):
                self.power_production_mode = False
                self.logger.info(
                    f"Power consumption at {moving_average_balance},"
                    f" threshold exceeded. Setting heat pump flow temperature to "
                    f"{self.config.power_consumption_threshold}°C."
                )
                self.heat_pump.set_flow_temperature(
                    self.config.heat_pump_flow_temperature_power_consumption
                )

        def exit_condition(data):
            if (datetime.now() - self.last_heat_pump_status_check).seconds > 15 * 60:
                self.last_heat_pump_status_check = datetime.now()
                exit = not self.heat_pump.online()
                if exit:
                    self.logger.info("Heat pump is offline. Exiting power measurement.")
                return exit
            return False

        self.power_meter.start_measuring(
            measurement_callback=heatpump_power_measurement_callback, exit_condition=exit_condition
        )

    def restore_default_flow_temperature(self):
        self.logger.info(
            f"Setting default flow temperature "
            f"({self.config.heat_pump_flow_temperature_power_consumption}°C)."
        )
        self.heat_pump.set_flow_temperature(
            self.config.heat_pump_flow_temperature_power_consumption
        )
        self.power_production_mode = False
