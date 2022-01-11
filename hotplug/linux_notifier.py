from ctypes import byref

import usb1
import asyncio
from hotplug.hotplug import HotPlug, list_devices
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class LinuxNotifier(HotPlug):
    def __init__(self, loop=None):
        super().__init__()

    async def start(self):
        logger.debug(f'Listening to messages')
        devices = set(list_devices())
        while True:
            await asyncio.sleep(.5)  # allow the loop to run
            latest = set(list_devices())
            if latest != devices:
                devices = latest
                self._handle_change()
