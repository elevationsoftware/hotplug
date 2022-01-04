import os
import asyncio

if os.name == 'nt':
    from hotplug.windows_notifier import WindowsNotifier as Notifier
else:
    from hotplug.linux_notifier import LinuxNotifier as Notifier

__instance = None


def get_notifier():
    global __instance
    if __instance is not None:
        return __instance

    __instance = Notifier()
    asyncio.create_task(__instance.start())
    return __instance


def __getattr__(name):
    global __instance
    if __instance is None:
        __instance = get_notifier()

    if hasattr(__instance, name):
        return getattr(__instance, name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")



