import asyncio
from pyee import AsyncIOEventEmitter
import usb.core


class HotPlug(AsyncIOEventEmitter):
    def __init__(self):
        super().__init__()
        self.devices = set()
        self.__update()

    def __update(self):
        devices = usb.core.find(find_all=True)
        latest = set(f"{d.idVendor:04x}:{d.idProduct:04x}" for d in devices)
        added = [x for x in latest if x not in self.devices]
        removed = [x for x in self.devices if x not in latest]
        self.devices = latest
        return added, removed

    async def _handle_change(self):
        added, removed = self.__update()
        self.emit('change', added, removed)

