import asyncio
import logging
import win32api, win32con, win32gui

from hotplug.hotplug import HotPlug

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class WindowsNotifier(HotPlug):
    def __init__(self, loop=None):
        super().__init__()
        self.debouncing = False
        self.loop = loop or asyncio.get_running_loop()
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._on_message_sync
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        logger.debug(f'Created listener window with hwnd={self.hwnd:x}')

    async def start(self):
        logger.debug(f'Listening to messages')
        while True:
            win32gui.PumpWaitingMessages()
            await asyncio.sleep(.2)  # allow the loop to run

    def _on_message_sync(self, hwnd: int, msg: int, wparam: int, lparam: int):
        if msg == win32con.WM_DEVICECHANGE and wparam == 0x0007:
            asyncio.run_coroutine_threadsafe(self.__async_emit(), self.loop)
        return 0

    async def __async_emit(self):
        if self.debouncing:
            return
        self.debouncing = True
        self._handle_change()
        await asyncio.sleep(.5)
        self.debouncing = False
