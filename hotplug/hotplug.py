import usb1
from pyee import AsyncIOEventEmitter


def list_devices():
    with usb1.USBContext() as context:
        for d in context.getDeviceIterator(skip_on_error=True):
            try:
                serial_num = d.getSerialNumber()
            except Exception:
                serial_num = None
                pass
            yield d.getVendorID(), d.getProductID(), d.getBusNumber(), d.getDeviceAddress(), serial_num


class HotPlug(AsyncIOEventEmitter):
    def __init__(self):
        super().__init__()
        self.devices = set()
        self.__update()

    def __update(self):
        latest = set(list_devices())
        added = [x for x in latest if x not in self.devices]
        removed = [x for x in self.devices if x not in latest]
        self.devices = latest
        return added, removed

    def _handle_change(self):
        added, removed = self.__update()
        for d in added:
            vid, pid, bus, address, serial_num = d
            self.emit('change', 'added', d)
            self.emit('added', d)
            self.emit(f"{vid:04x}:{pid:04x}", 'added', d)
        for d in removed:
            vid, pid, bus, address, serial_num = d
            self.emit('change', 'removed', d)
            self.emit('removed', d)
            self.emit(f"{vid:04x}:{pid:04x}", 'removed', d)

    def contains(self, vid, pid, serial_num=None):
        for d in self.devices:
            v, p, b, a, s = d
            if v == vid and p == pid:
                if serial_num:
                    if s == serial_num:
                        return True
                    else:
                        continue
                else:
                    return True
        return False
