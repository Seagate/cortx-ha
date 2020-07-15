from typing import NamedTuple, Optional
from pcswrap.types import Credentials


class Command():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class CLIContext(NamedTuple):
    command: Command
    auth: Optional[Credentials]
    verbose: bool
    timeout_sec: int


class MaintenanceAll(Command):
    pass


class UnmaintenanceAll(Command):
    pass


class StandbyAll(Command):
    pass


class Standby(Command):
    node: str


class UnstandbyAll(Command):
    pass


class Unstandby(Command):
    node: str


class Shutdown(Command):
    node: str


class Status(Command):
    is_full: bool


class NoOp(Command):
    pass
