from typing import Dict

from uuid import UUID

from ..DriverDefinition import DriverDefinition
from ..drivers.SonyMonitor import SonyBvmDSeries
from ..drivers.Extron import Extron
from ..drivers.TeslaSmart import TeslaSmart


def __register_drivers(*definitions: DriverDefinition) -> Dict[UUID, DriverDefinition]:
    registry = {}  # type: Dict[UUID, DriverDefinition]
    for definition in definitions:
        if definition.guid in registry:
            raise ValueError("Duplicate driver `{0}` defined for uuid:{1}".format(definition.title, definition.guid))

        registry[definition.guid] = definition

    return registry


# noinspection SpellCheckingInspection
drivers = __register_drivers(
    DriverDefinition(guid="8315EF32-8028-4489-BFA7-6C94841EFB15",
                     title="Sony BVM-D series",
                     factory=lambda: SonyBvmDSeries({}),
                     flags=DriverDefinition.USES_STREAMS),
    DriverDefinition(guid="BFAFDC37-C351-4FE7-99B1-AA922EE3469C",
                     title="Extron SIS compatible matrix switch",
                     factory=lambda: Extron({}),
                     flags=DriverDefinition.USES_STREAMS),
    DriverDefinition(guid="09A4AFA3-4C01-47ED-9BCC-0AD6436652BB",
                     title="TeslaSmart compatible switch",
                     factory=lambda: TeslaSmart({}),
                     flags=DriverDefinition.USES_STREAMS)
)
