import zkillboard


class MyClient(zkillboard.ClientKillStream):
    async def on_new_killmail(self, killmail: zkillboard.Killmail):
        print(killmail)


# class MyClient(zkillboard.ClientFiltered):
#     async def on_new_killmail(self, killmail: dict):
#         print(killmail)


# filter = zkillboard.Filter(zkillboard.FilterType.REGION, 10000070)
# client = MyClient(filters=[filter])
# client.run()

client = MyClient()
client.run()
