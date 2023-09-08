"""Accessing ESI eveuniverse."""

import enum
import logging
from dataclasses import dataclass
from typing import Collection, Dict

import aiohttp

from .helpers import chunks

ESI_EVEUNIVERSE_NAMES_URL = "https://esi.evetech.net/latest/universe/names"


logger = logging.getLogger("zkillboard")


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

        @classmethod
        def from_esi_data(cls, esi_category: str) -> "EveEntity.Category":
            """Create new obj from the corresponding ESI category."""
            esi_category_map = {
                "alliance": cls.ALLIANCE,
                "character": cls.CHARACTER,
                "constellation": cls.CONSTELLATION,
                "corporation": cls.CORPORATION,
                "faction": cls.FACTION,
                "inventory_type": cls.INVENTORY_TYPE,
                "region": cls.REGION,
                "solar_system": cls.SOLAR_SYSTEM,
                "station": cls.STATION,
            }
            return esi_category_map[esi_category]

    id: int
    name: str = ""
    category: Category = Category.UNDEFINED

    @classmethod
    def from_esi_data(cls, data: dict) -> "EveEntity":
        """Create new object from an ESI data."""
        category = cls.Category.from_esi_data(data["category"])
        return cls(id=data["id"], name=data["name"], category=category)

    @classmethod
    async def create_objs_from_esi(cls, ids: Collection[int]) -> Dict[int, "EveEntity"]:
        """Create EveEntity objects from ESI."""
        ids = list({int(id) for id in ids if id != 1})  # 1 is not a valid ID

        data = []
        async with aiohttp.ClientSession() as session:
            for ids_chunk in chunks(ids, 999):
                logger.info("Requesting details from ESI for %d IDs", len(ids_chunk))
                async with session.post(
                    ESI_EVEUNIVERSE_NAMES_URL, json=ids_chunk
                ) as resp:
                    data += await resp.json()
                    logger.debug("Received response from ESI: %s", data)

        entities = {}
        for obj in data:
            entity = EveEntity.from_esi_data(obj)
            entities[entity.id] = entity
        return entities
