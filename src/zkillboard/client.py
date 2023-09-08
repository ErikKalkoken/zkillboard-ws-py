"""Clients for zkillboard WS API."""

import asyncio
import enum
import logging
from abc import ABC, abstractmethod
from typing import List, NamedTuple

import aiohttp
import aiorun

from . import config
from .killmails import Killmail

logger = logging.getLogger("zkillboard")


class FilterType(str, enum.Enum):
    """A type for filtering killmails.."""

    ALLIANCE = "alliance"
    CHARACTER = "character"
    CORPORATION = "corporation"
    FACTION = "faction"
    SHIP = "ship"
    GROUP = "group"
    SYSTEM = "system"
    CONSTELLATION = "constellation"
    REGION = "region"
    LOCATION = "location"
    LABEL = "label"
    ALL = "all"


class Filter(NamedTuple):
    """A filter for filtering killmails."""

    type: FilterType
    id: int

    def channel(self) -> str:
        """Return channel name for this filter."""
        filter_id = "*" if self.type == FilterType.ALL else self.id
        return f"{self.type}:{filter_id}"


class _Client(ABC):
    """Base class for all client variants."""

    def __init__(self) -> None:
        super().__init__()
        self.channels = []

    @abstractmethod
    async def on_new_killmail(self, killmail: Killmail):
        """This method is called when a new killmail is received from zkillboard API."""

    async def _subscribe_channels(self, ws: aiohttp.ClientWebSocketResponse):
        for channel in self.channels:
            await ws.send_json({"action": "sub", "channel": str(channel)})
            logger.info("subscribed to %s", channel)

    async def _parse_killmail(self, killmail_data: dict):
        killmail = Killmail.create_from_zkb_data(killmail_data)
        await self.on_new_killmail(killmail)

    async def run_client(self):
        """Run the client for receiving events from the zkillboard websocket API."""

        while True:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.ws_connect(config.ZKB_WS_URL) as ws:
                        logger.info("Connected to zKillboard websocket API")
                        await self._subscribe_channels(ws)

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                killmail_data = msg.json()
                                logger.info(
                                    "Received killmail: %s",
                                    killmail_data["killmail_id"],
                                )
                                asyncio.create_task(self._parse_killmail(killmail_data))

                    logger.info("ZKB API closed connection")

                except aiohttp.ClientError as ex:
                    logger.error("client error when listening to websocket API: %s", ex)

            logger.info(
                "Trying to re-connect to ZKB API in %d seconds",
                config.RECONNECT_TIMEOUT_SECONDS,
            )
            await asyncio.sleep(config.RECONNECT_TIMEOUT_SECONDS)

    def run(self):
        """Run the client standalone."""
        logging.basicConfig(level=config.LOG_LEVEL_DEFAULT, format=config.LOG_FORMAT)
        aiorun.run(self.run_client())


class ClientKillStream(_Client):
    """A client for receiving the complete killmail stream."""

    def __init__(self) -> None:
        super().__init__()
        self.channels = ["killstream"]


class ClientFiltered(_Client):
    """A client for receiving killmails from filtered channels."""

    def __init__(self, filters: List[Filter]) -> None:
        super().__init__()
        self.channels = [filter.channel() for filter in filters]


class ClientPublic(_Client):
    """A client for receiving items from the public channel.."""

    def __init__(self) -> None:
        super().__init__()
        self.channels = ["killstream"]
