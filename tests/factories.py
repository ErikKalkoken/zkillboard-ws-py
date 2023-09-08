import datetime as dt
from typing import Generic, TypeVar

import factory
import factory.fuzzy

from zkillboard.eveuniverse import EveEntity
from zkillboard.killmails import (
    Killmail,
    KillmailAttacker,
    KillmailPosition,
    KillmailVictim,
    KillmailZkb,
    _KillmailCharacter,
)

T = TypeVar("T")


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class BaseMetaFactory(Generic[T], factory.base.FactoryMetaClass):
    def __call__(cls, *args, **kwargs) -> T:
        return super().__call__(*args, **kwargs)


class EveEntityCharacterFactory(factory.Factory, metaclass=BaseMetaFactory[EveEntity]):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 10000 + n)
    name = factory.faker.Faker("name")
    category = EveEntity.Category.CHARACTER


class EveEntityCorporationFactory(
    factory.Factory, metaclass=BaseMetaFactory[EveEntity]
):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 20000 + n)
    name = factory.faker.Faker("company")
    category = EveEntity.Category.CORPORATION


class EveEntityAllianceFactory(factory.Factory, metaclass=BaseMetaFactory[EveEntity]):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 30000 + n)
    name = factory.faker.Faker("company")
    category = EveEntity.Category.ALLIANCE


class EveEntityFactionFactory(factory.Factory, metaclass=BaseMetaFactory[EveEntity]):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 40000 + n)
    name = factory.faker.Faker("color_name")
    category = EveEntity.Category.FACTION


class EveEntityInventoryTypeFactory(
    factory.Factory, metaclass=BaseMetaFactory[EveEntity]
):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 50000 + n)
    name = factory.faker.Faker("color_name")
    category = EveEntity.Category.INVENTORY_TYPE


class EveEntitySolarSystemFactory(
    factory.Factory, metaclass=BaseMetaFactory[EveEntity]
):
    class Meta:
        model = EveEntity

    id = factory.Sequence(lambda n: 60000 + n)
    name = factory.faker.Faker("city")
    category = EveEntity.Category.SOLAR_SYSTEM


class _KillmailCharacterFactory(factory.Factory):
    class Meta:
        model = _KillmailCharacter

    character = factory.SubFactory(EveEntityCharacterFactory)
    corporation = factory.SubFactory(EveEntityCorporationFactory)
    alliance = factory.SubFactory(EveEntityAllianceFactory)
    faction = factory.SubFactory(EveEntityFactionFactory)
    ship_type = factory.SubFactory(EveEntityInventoryTypeFactory)


class KillmailVictimFactory(
    _KillmailCharacterFactory, metaclass=BaseMetaFactory[KillmailVictim]
):
    class Meta:
        model = KillmailVictim

    damage_taken = factory.fuzzy.FuzzyInteger(1_000_000)


class KillmailAttackerFactory(
    _KillmailCharacterFactory, metaclass=BaseMetaFactory[KillmailAttacker]
):
    class Meta:
        model = KillmailAttacker

    damage_done = factory.fuzzy.FuzzyInteger(1_000_000)
    security_status = factory.fuzzy.FuzzyFloat(-10.0, 5)
    weapon_type = factory.SubFactory(EveEntityInventoryTypeFactory)


class KillmailPositionFactory(
    factory.Factory, metaclass=BaseMetaFactory[KillmailPosition]
):
    class Meta:
        model = KillmailPosition

    x = factory.fuzzy.FuzzyFloat(-10_000, 10_000)
    y = factory.fuzzy.FuzzyFloat(-10_000, 10_000)
    z = factory.fuzzy.FuzzyFloat(-10_000, 10_000)


class KillmailZkbFactory(factory.Factory, metaclass=BaseMetaFactory[KillmailZkb]):
    class Meta:
        model = KillmailZkb

    location_id = factory.Sequence(lambda n: n + 60_000_000)
    hash = factory.fuzzy.FuzzyText()
    fitted_value = factory.fuzzy.FuzzyFloat(10_000, 100_000_000)
    total_value = factory.LazyAttribute(lambda o: o.fitted_value)
    points = factory.fuzzy.FuzzyInteger(1000)
    is_npc = False
    is_solo = False
    is_awox = False


class KillmailFactory(factory.Factory, metaclass=BaseMetaFactory[Killmail]):
    class Meta:
        model = Killmail

    id = factory.Sequence(lambda n: n + 1800000000001)
    victim = factory.SubFactory(KillmailVictimFactory)
    position = factory.SubFactory(KillmailPositionFactory)
    zkb = factory.SubFactory(KillmailZkbFactory)
    solar_system = factory.SubFactory(EveEntitySolarSystemFactory)
    time = factory.LazyFunction(now)

    @factory.lazy_attribute
    def attackers(self):
        amount = factory.fuzzy.FuzzyInteger(1, 10).fuzz()
        my_attackers = [KillmailAttackerFactory() for _ in range(amount)]
        my_attackers[0].is_final_blow = True
        return my_attackers
