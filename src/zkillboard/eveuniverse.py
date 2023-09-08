"""EVE universe classes."""

# pylint: disable = redefined-builtin

import enum
from dataclasses import dataclass


@dataclass
class EveEntity:
    """An entity in Eve Online."""

    class Category(enum.Enum):
        """A category of an EveEntity object."""

        ALLIANCE = enum.auto()
        CHARACTER = enum.auto()
        CONSTELLATION = enum.auto()
        CORPORATION = enum.auto()
        FACTION = enum.auto()
        INVENTORY_TYPE = enum.auto()
        REGION = enum.auto()
        SOLAR_SYSTEM = enum.auto()
        STATION = enum.auto()
        UNDEFINED = enum.auto()

    id: int
    name: str = ""
    category: Category = Category.UNDEFINED
