"""Fetching killmails from ZKB."""

# pylint: disable = redefined-builtin

import datetime as dt
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from .eveuniverse import EveEntity

logger = logging.getLogger("zkillboard")


@dataclass
class _KillmailBase:
    """Base class for all Killmail."""

    def asdict(self) -> dict:
        """Return this object as dict."""
        return asdict(self)


@dataclass
class _KillmailCharacter(_KillmailBase):
    _DATA_MAP = {
        "character": "character_id",
        "corporation": "corporation_id",
        "alliance": "alliance_id",
        "faction": "faction_id",
        "ship_type": "ship_type_id",
    }

    character: Optional[EveEntity] = None
    corporation: Optional[EveEntity] = None
    alliance: Optional[EveEntity] = None
    faction: Optional[EveEntity] = None
    ship_type: Optional[EveEntity] = None

    def entities(self) -> List[EveEntity]:
        """Return EveEntity objs."""
        objs = []
        if self.character:
            objs.append(self.character)
        if self.corporation:
            objs.append(self.corporation)
        if self.alliance:
            objs.append(self.alliance)
        if self.faction:
            objs.append(self.faction)
        if self.ship_type:
            objs.append(self.ship_type)
        return objs


@dataclass
class KillmailVictim(_KillmailCharacter):
    """A victim on a killmail."""

    damage_taken: Optional[int] = None


@dataclass
class KillmailAttacker(_KillmailCharacter):
    """An attacker on a killmail."""

    _DATA_MAP = {**_KillmailCharacter._DATA_MAP, **{"weapon_type": "weapon_type_id"}}

    damage_done: Optional[int] = None
    is_final_blow: Optional[bool] = None
    security_status: Optional[float] = None
    weapon_type: Optional[EveEntity] = None

    def entities(self) -> List[EveEntity]:
        """Return EveEntity objects."""
        objs = super().entities()
        if self.weapon_type:
            objs.append(self.weapon_type)
        return objs


@dataclass
class KillmailPosition(_KillmailBase):
    "A position for a killmail."
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


# pylint: disable = too-many-instance-attributes
@dataclass
class KillmailZkb(_KillmailBase):
    """A ZKB entry for a killmail."""

    location_id: Optional[int] = None
    hash: Optional[str] = None
    fitted_value: Optional[float] = None
    total_value: Optional[float] = None
    points: Optional[int] = None
    is_npc: Optional[bool] = None
    is_solo: Optional[bool] = None
    is_awox: Optional[bool] = None


@dataclass
class Killmail(_KillmailBase):
    """A killmail in Eve Online."""

    id: int
    time: datetime
    victim: KillmailVictim
    attackers: List[KillmailAttacker]
    position: KillmailPosition
    zkb: KillmailZkb
    solar_system: Optional[EveEntity] = None

    def entities(self) -> List[EveEntity]:
        """Return EveEntity objects."""
        objs = []
        if self.solar_system:
            objs.append(self.solar_system)
        if self.victim:
            objs += self.victim.entities()
        for attacker in self.attackers:
            objs += attacker.entities()
        return objs

    def attacker_final_blow(self) -> Optional[KillmailAttacker]:
        """Returns the attacker with the final blow or None if not found."""
        for attacker in self.attackers:
            if attacker.is_final_blow:
                return attacker
        return None

    async def resolve_entities(self):
        """Resolve all eve entities from ESI."""
        entities = self.entities()
        ids = [obj.id for obj in entities]
        resolved_entities = await EveEntity.create_objs_from_esi(ids)
        for entity in entities:
            if entity.id in resolved_entities:
                resolved_entity = resolved_entities[entity.id]
                entity.name = resolved_entity.name
                entity.category = resolved_entity.category

    @classmethod
    def create_from_zkb_data(cls, killmail_data: dict) -> "Killmail":
        """Create a new object from raw killmail data
        as returned by zkillboard WS API."""

        victim, position = cls._extract_victim_and_position(killmail_data)
        attackers = cls._extract_attackers(killmail_data)
        zkb = cls._extract_zkb(killmail_data)

        params = {
            "id": killmail_data["killmail_id"],
            "time": cls.parse_killmail_time(killmail_data["killmail_time"]),
            "victim": victim,
            "position": position,
            "attackers": attackers,
            "zkb": zkb,
        }
        if entity_id := killmail_data.get("solar_system_id"):
            params["solar_system"] = EveEntity(entity_id)

        return Killmail(**params)

    @staticmethod
    def parse_killmail_time(date_string: str) -> dt.datetime:
        """Parse date string into datetime object."""
        my_dt = dt.datetime.strptime(date_string, r"%Y-%m-%dT%H:%M:%SZ")
        return my_dt.replace(tzinfo=dt.timezone.utc)

    @classmethod
    def _extract_victim_and_position(
        cls, killmail_data: dict
    ) -> Tuple[Optional[KillmailVictim], Optional[KillmailPosition]]:
        victim = None
        position = None
        if "victim" in killmail_data:
            victim_data = killmail_data["victim"]
            params = {}
            for obj_prop, data_prop in KillmailVictim._DATA_MAP.items():
                if entity_id := victim_data.get(data_prop):
                    params[obj_prop] = EveEntity(entity_id)

            victim = KillmailVictim(**params)

            if "position" in victim_data:
                position_data = victim_data["position"]
                params = {}
                for prop in ["x", "y", "z"]:
                    if prop in position_data:
                        params[prop] = position_data[prop]

                position = KillmailPosition(**params)

        return victim, position

    @classmethod
    def _extract_attackers(cls, killmail_data: dict) -> List[KillmailAttacker]:
        attackers = []
        for attacker_data in killmail_data.get("attackers", []):
            params = {}
            for obj_prop, data_prop in KillmailVictim._DATA_MAP.items():
                if entity_id := attacker_data.get(data_prop):
                    params[obj_prop] = EveEntity(entity_id)

            if "final_blow" in attacker_data:
                params["is_final_blow"] = attacker_data["final_blow"]

            attackers.append(KillmailAttacker(**params))
        return attackers

    @classmethod
    def _extract_zkb(cls, package_data) -> Optional[KillmailZkb]:
        if "zkb" not in package_data:
            return None

        zkb_data = package_data["zkb"]
        params = {}
        params["location_id"] = zkb_data.get("locationID")

        for prop, mapping in (
            ("hash", None),
            ("fittedValue", "fitted_value"),
            ("totalValue", "total_value"),
            ("points", None),
            ("npc", "is_npc"),
            ("solo", "is_solo"),
            ("awox", "is_awox"),
        ):
            if prop in zkb_data:
                if mapping:
                    params[mapping] = zkb_data[prop]
                else:
                    params[prop] = zkb_data[prop]

        return KillmailZkb(**params)
