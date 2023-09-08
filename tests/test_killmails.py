import datetime as dt
from unittest import TestCase

from zkillboard.killmails import Killmail

from .factories import KillmailFactory
from .fixtures import killmails_raw

MODULE_PATH = "killtracker.core.killmails"


class TestKillmailSerialization(TestCase):
    def test_dict_serialization(self):
        killmail = KillmailFactory()
        dct_1 = killmail.asdict()
        killmail_2 = Killmail.from_dict(dct_1)
        self.assertEqual(killmail, killmail_2)

    def test_json_serialization(self):
        killmail = KillmailFactory()
        json_1 = killmail.asjson()
        killmail_2 = Killmail.from_json(json_1)
        self.assertEqual(killmail, killmail_2)


class TestKillmail(TestCase):
    def test_should_parse_killmail_time(self):
        # when
        result = Killmail.parse_killmail_time("2023-09-08T17:18:46Z")
        # then
        self.assertEqual(
            result, dt.datetime(2023, 9, 8, 17, 18, 46, tzinfo=dt.timezone.utc)
        )

    def test_should_create_killmail_from_raw_data(self):
        # given
        killmail_data = killmails_raw[111519365]
        # when
        killmail = Killmail.create_from_zkb_data(killmail_data)
        # then
        self.assertEqual(killmail.id, 111519365)
        self.assertEqual(killmail.solar_system_id, 30001994)

    def test_should_return_all_entity_ids(self):
        # given
        killmail = KillmailFactory()
        # when
        result = killmail.entity_ids()
        # then
        expected = {
            killmail.solar_system_id,
            killmail.victim.corporation_id,
            killmail.victim.alliance_id,
            killmail.victim.faction_id,
            killmail.victim.ship_type_id,
            killmail.zkb.location_id,
        }
        for attacker in killmail.attackers:
            expected.update(
                {
                    attacker.corporation_id,
                    attacker.alliance_id,
                    attacker.faction_id,
                    attacker.ship_type_id,
                    attacker.weapon_type_id,
                }
            )
        self.assertSetEqual(result, expected)


# class TestKillmailBasics(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.killmail = load_killmail(10000001)

#     def test_str(self):
#         self.assertEqual(str(self.killmail), "Killmail(id=10000001)")

#     def test_repr(self):
#         self.assertEqual(repr(self.killmail), "Killmail(id=10000001)")

#     def test_entity_ids(self):
#         result = self.killmail.entity_ids()
#         expected = {
#             1011,
#             2011,
#             3011,
#             603,
#             30004984,
#             1001,
#             1002,
#             1003,
#             2001,
#             3001,
#             34562,
#             2977,
#             3756,
#             2488,
#             500001,
#             500004,
#         }
#         self.assertSetEqual(result, expected)

#     def test_should_return_attacker_alliance_ids(self):
#         # when
#         result = self.killmail.attackers_distinct_alliance_ids()
#         # then
#         self.assertSetEqual(set(result), {3001})

#     def test_should_return_attacker_corporation_ids(self):
#         # when
#         result = self.killmail.attackers_distinct_corporation_ids()
#         # then
#         self.assertSetEqual(set(result), {2001})

#     def test_should_return_attacker_character_ids(self):
#         # when
#         result = self.killmail.attackers_distinct_character_ids()
#         # then
#         self.assertSetEqual(set(result), {1001, 1002, 1003})

#     def test_attackers_ships_types(self):
#         self.assertListEqual(
#             self.killmail.attackers_ship_type_ids(), [34562, 3756, 3756]
#         )

#     def test_ships_types(self):
#         self.assertSetEqual(self.killmail.ship_type_distinct_ids(), {603, 34562, 3756})
