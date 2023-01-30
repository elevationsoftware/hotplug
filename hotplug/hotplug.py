import usb1
from AsyncEventEmitter import AsyncEventEmitter

def list_devices():
    with usb1.USBContext() as context:
        for d in context.getDeviceIterator(skip_on_error=True):
            try:
                serial_num = d.getSerialNumber()
            except Exception:
                serial_num = None
                pass
            yield d.getVendorID(), d.getProductID(), d.getBusNumber(), d.getDeviceAddress(), serial_num


def _find(lst, vid, pid, buss, address, _):
    for d in lst:
        if d[0] == vid and d[1] == pid and d[2] == buss and d[3] == address:
            return d


class HotPlug(AsyncEventEmitter):
    def __init__(self):
        super().__init__()
        self.devices = set()
        self.__update()

    def __update(self):
        latest = set()

        # On Windows: once a USB device has been claimed,
        # we can't access getSerialNumber(). So, we need
        # to keep the old version if it had a serial.
        for d_new in list_devices():
            d_old = _find(self.devices, *d_new)
            if d_old is not None:
                d_new = d_old if d_old[4] is not None else d_new
            latest.add(d_new)

        added = [x for x in latest if x not in self.devices]
        removed = [x for x in self.devices if x not in latest]
        self.devices = latest
        return added, removed

    def _handle_change(self):
        added, removed = self.__update()
        for d in added:
            vid, pid, bus, address, serial_num = d
            self.emit_and_forget('change', 'added', d)
            self.emit_and_forget('added', d)
            self.emit_and_forget(f"{vid:04x}:{pid:04x}", 'added', d)
        for d in removed:
            vid, pid, bus, address, serial_num = d
            self.emit_and_forget('change', 'removed', d)
            self.emit_and_forget('removed', d)
            self.emit_and_forget(f"{vid:04x}:{pid:04x}", 'removed', d)

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
