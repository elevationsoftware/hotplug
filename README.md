Hotplug
-------

`pyusb` monkeypatched with hotplugging.

... oh, plus asyncio eventing.

See: https://github.com/pyusb/pyusb/pull/160

```python
import asyncio
import hotplug


async def whats_new'(added, removed):
    print(f'added:{added}, removed:{removed}')


async def main():
    hotplug.on('change', whats_new)
    await asyncio.sleep(999)

if __name__ == '__main__':
    asyncio.run(main())
    ...

```

