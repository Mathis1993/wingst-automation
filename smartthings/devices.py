from smartthings.api import Api
from smartthings.commands import Command


class Device:
    def __init__(self, device_id: str, api: Api):
        self.device_id = device_id
        self.api = api

    def execute_command(self, command: Command):
        return self.api.command(self.device_id, command)
