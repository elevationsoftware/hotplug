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
        latest = set((d.idVendor, d.idProduct, d.bus, d.address) for d in devices)
        added = [x for x in latest if x not in self.devices]
        removed = [x for x in self.devices if x not in latest]
        self.devices = latest
        return added, removed

    def _handle_change(self):
        added, removed = self.__update()
        for d in added:
            vid, pid, bus, address = d
            self.emit('change', 'added', d)
            self.emit('added', d)
            self.emit(f"{vid:04x}:{pid:04x}", 'added', d)
        for d in removed:
            vid, pid, bus, address = d
            self.emit('change', 'removed', d)
            self.emit('removed', d)
            self.emit(f"{vid:04x}:{pid:04x}", 'removed', d)

    def contains(self, vid, pid):
        for d in self.devices:
            v, p, b, a = d
            if v == vid and p == pid:
                return True
        return False
