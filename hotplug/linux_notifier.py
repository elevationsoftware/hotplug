import usb
import asyncio
from hotplug.hotplug import HotPlug
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LinuxNotifier(HotPlug):
    def __init__(self, loop=None):
        super().__init__()

    async def start(self):
        logger.debug(f'Listening to messages')
        backend = usb.backend.libusb1.get_backend()
        devices = set([d.devid for d in backend.enumerate_devices()])
        while True:
            await asyncio.sleep(.5)  # allow the loop to run
            latest = set([d.devid for d in backend.enumerate_devices()])
            if latest != devices:
                devices = latest
                self._handle_change()
