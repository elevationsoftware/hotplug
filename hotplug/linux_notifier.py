import asyncio

import usb
import logging
from usb.core import Device
from usb.backend.libusb1 import (
    CFUNCTYPE, POINTER, c_int, c_void_p, _libusb_device_handle, c_uint, py_object,
    _objfinalizer, byref, _Device
)
from hotplug.hotplug import HotPlug

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# # # # # #  PATCH pyusb for hotplug # # # # # #
# Extracted from: https://github.com/pyusb/pyusb/pull/160
backend = usb.backend.libusb1.get_backend()

_libusb_hotplug_callback_handle = c_int
_libusb_hotplug_callback_fn = CFUNCTYPE(c_int, c_void_p, _libusb_device_handle, c_uint, py_object)
backend.lib.libusb_hotplug_register_callback.argtypes = [
    c_void_p, c_int, c_int, c_int, c_int, c_int,
    _libusb_hotplug_callback_fn, py_object,
    POINTER(_libusb_hotplug_callback_handle)
]
backend.lib.libusb_hotplug_deregister_callback.argtypes = [
    c_void_p, _libusb_hotplug_callback_handle
]


class _HotplugHandle(_objfinalizer.AutoFinalizedObject):
    def __init__(self, backend, events, flags, vendor_id, product_id, dev_class, user_callback, user_data):
        self.user_callback = user_callback
        self.__callback = _libusb_hotplug_callback_fn(self.callback)
        self.__backend = backend
        # If an object is passed directly and never stored anywhere,
        # the pointer will remain and user data might be wrong!
        # therefore we have to keep a refernce here
        self.__user_data = py_object(user_data)
        handle = _libusb_hotplug_callback_handle()
        backend.lib.libusb_hotplug_register_callback(backend.ctx, events, flags, vendor_id, product_id, dev_class,
                                                     self.__callback, self.__user_data, byref(handle))

    def callback(self, ctx, dev, evnt, user_data):
        dev = Device(_Device(dev), self.__backend)
        return self.user_callback(dev, evnt, user_data)


def register_callback(callback, *,
                      user_data=None,
                      events=0x01 | 0x02,  # arrive and exit
                      flags=0,  # do not emumerate on register
                      vendor_id=-1,  # match any
                      product_id=-1,  # match any
                      dev_class=-1  # match any
                      ):
    return _HotplugHandle(backend, events, flags, vendor_id, product_id, dev_class, callback, user_data)


def deregister_callback(handle):
    backend.lib.libusb_hotplug_deregister_callback(backend.ctx, handle.handle)


class LinuxNotifier(HotPlug):
    def __init__(self, loop=None):
        super().__init__()
        self.loop = loop or asyncio.get_running_loop()
        self.handle = register_callback(self.__handle_notification)

    def __handle_notification(self, *args):
        asyncio.run_coroutine_threadsafe(self.__async_emit(), self.loop)
        return 0

    async def __async_emit(self):
        await self._handle_change()

    async def start(self):
        logger.debug(f'Listening to messages')
        loop = asyncio.get_running_loop()
        while True:
            await loop.run_in_executor(None, backend.lib.libusb_handle_events, backend.ctx)
            await asyncio.sleep(.2)  # allow the loop to run
