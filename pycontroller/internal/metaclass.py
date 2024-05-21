import inspect
from typing import _ProtocolMeta

from pycontroller.internal.manager import ControllerManager


class MetaController(_ProtocolMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name == "Controller":
            return

        # Get the current frame
        current_frame = inspect.currentframe()

        # Move to the previous frame (namespace_test's frame)
        previous_frame = current_frame.f_back

        # hide the controller logic behind this member variable so the child classes namespace doesn't get cluttered
        cls._controller_manager = ControllerManager(cls, name, attrs, previous_frame)
