from wingst import settings
from wingst.commander import Commander, Config


def run():
    """
    Accumulate a moving average of power balance (consumption - production) values.
    If the moving average is below a threshold, increase the heat pump flow temperature for heating
    (radiators) in order to use the produced power.
    If the moving average is above a threshold, decrease the heat pump flow temperature again.
    """
    config = Config(
        heat_pump_flow_temperature_power_production=settings.HEAT_PUMP_FLOW_TEMPERATURE_POWER_PRODUCTION,  # noqa E501
        heat_pump_flow_temperature_power_consumption=settings.HEAT_PUMP_FLOW_TEMPERATURE_POWER_CONSUMPTION,  # noqa E501
        power_production_threshold=settings.POWER_PRODUCTION_THRESHOLD,
        power_consumption_threshold=settings.POWER_CONSUMPTION_THRESHOLD,
        track_last_n_power_measurements=settings.TRACK_LAST_N_POWER_MEASUREMENTS,
    )
    commander = Commander(config=config)
    commander.command_heatpump()


if __name__ == "__main__":
    run()
