"""Accessing ESI."""

import logging
from typing import Collection, Dict

import aiohttp

from .eveuniverse import EveEntity
from .helpers import chunks

ESI_EVEUNIVERSE_NAMES_URL = "https://esi.evetech.net/latest/universe/names"


logger = logging.getLogger("zkillboard")


async def create_eve_entities_from_ids(ids: Collection[int]) -> Dict[int, EveEntity]:
    """Create EveEntity objects from IDs."""
    ids = list({int(id) for id in ids if id != 1})  # 1 is not a valid ID

    data = []
    async with aiohttp.ClientSession() as session:
        for ids_chunk in chunks(ids, 999):
            logger.info("Requesting details from ESI for %d IDs", len(ids_chunk))
            async with session.post(ESI_EVEUNIVERSE_NAMES_URL, json=ids_chunk) as resp:
                data += await resp.json()
                logger.debug("Received response from ESI: %s", data)

    esi_category_map = {
        "alliance": EveEntity.Category.ALLIANCE,
        "character": EveEntity.Category.CHARACTER,
        "constellation": EveEntity.Category.CONSTELLATION,
        "corporation": EveEntity.Category.CORPORATION,
        "faction": EveEntity.Category.FACTION,
        "inventory_type": EveEntity.Category.INVENTORY_TYPE,
        "region": EveEntity.Category.REGION,
        "solar_system": EveEntity.Category.SOLAR_SYSTEM,
        "station": EveEntity.Category.STATION,
    }

    entities = {}
    for obj in data:
        category = esi_category_map[obj["category"]]
        entity = EveEntity(id=obj["id"], name=obj["name"], category=category)
        entities[entity.id] = entity
    return entities
