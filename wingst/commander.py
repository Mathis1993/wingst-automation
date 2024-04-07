import logging
from dataclasses import dataclass

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
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def command_heatpump(self):
        async def heatpump_power_measurement_callback(data):
            moving_average_balance = self.power_meter.moving_average_power_balance()
            if not moving_average_balance:
                self.logger.info("No moving average balance available (yet).")
                return

            self.logger.info(f"Moving average balance: {moving_average_balance} Watts.")

            if (
                moving_average_balance < self.config.power_production_threshold
                and not self.power_production_mode
            ):
                self.power_production_mode = True
                self.logger.info(
                    f"Power production threshold exceeded. Setting heat pump flow temperature to "
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
                    f"Power consumption threshold exceeded. Setting heat pump flow temperature to "
                    f"{self.config.power_consumption_threshold}°C."
                )
                self.heat_pump.set_flow_temperature(self.config.power_consumption_threshold)

        self.power_meter.start_measuring(heatpump_power_measurement_callback)
