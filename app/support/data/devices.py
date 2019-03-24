from typing import Dict

from uuid import UUID

from ..DeviceDefinition import DeviceDefinition


def __register_devices(*definitions: DeviceDefinition) -> Dict[UUID, DeviceDefinition]:
    registry = {}  # type: Dict[UUID, DeviceDefinition]
    for definition in definitions:
        if definition.guid in registry:
            raise ValueError("Duplicate device `{0}` defined with uuid:{1}".format(definition.title, definition.guid))

        registry[definition.guid] = definition

    return registry


# noinspection SpellCheckingInspection
devices = __register_devices(
    DeviceDefinition(guid="DF98399F-32C7-4EB8-8435-A9F7EA1F9857", driver_guid="8315EF32-8028-4489-BFA7-6C94841EFB15",
                     title="Sony BVM-D series",
                     maximum_inputs=99),
    DeviceDefinition(guid="B176EB07-C112-41E8-909F-AB532975B377", driver_guid="BFAFDC37-C351-4FE7-99B1-AA922EE3469C",
                     title="Extron 12x8 SIS compatible matrix switch",
                     maximum_inputs=12, maximum_outputs=8,
                     capabilities=DeviceDefinition.HAS_DECOUPLED_AUDIO),
    DeviceDefinition(guid="9BE9DC48-C637-42AC-891A-0D8A842E0460", driver_guid="BFAFDC37-C351-4FE7-99B1-AA922EE3469C",
                     title="Extron 8x8 SIS compatible matrix switch",
                     maximum_inputs=8, maximum_outputs=8,
                     capabilities=DeviceDefinition.HAS_DECOUPLED_AUDIO),
    DeviceDefinition(guid="AED4225A-3164-4FEE-A44A-4E90D0F041DB", driver_guid="BFAFDC37-C351-4FE7-99B1-AA922EE3469C",
                     title="Extron 8x4 RGB SIS compatible matrix switchV",
                     maximum_inputs=8, maximum_outputs=4,
                     capabilities=DeviceDefinition.HAS_DECOUPLED_AUDIO),
    DeviceDefinition(guid="FE62D1EC-9D1B-488E-966D-581C5D162324", driver_guid="BFAFDC37-C351-4FE7-99B1-AA922EE3469C",
                     title="Extron 4x4 RGB SIS compatible matrix switchV",
                     maximum_inputs=4, maximum_outputs=4,
                     capabilities=DeviceDefinition.HAS_DECOUPLED_AUDIO),
    DeviceDefinition(guid="2BFB6B5B-F599-46CC-ADB0-09B67F1F08F5", driver_guid="09A4AFA3-4C01-47ED-9BCC-0AD6436652BB",
                     title="Tesla smart 16x1 compatible switch",
                     maximum_inputs=16),
    DeviceDefinition(guid="7C630854-C8DA-4FA1-A323-843E852978C5", driver_guid="09A4AFA3-4C01-47ED-9BCC-0AD6436652BB",
                     title="Tesla smart 8x1 compatible switch",
                     maximum_inputs=8),
)
