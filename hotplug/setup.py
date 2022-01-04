import os
from setuptools import setup, find_packages

requires = ['pyusb', 'pyee']
if os.name == 'nt':
    requires.append('pywin32')

setup(
    name="Hotplug",
    version="1.0.0",
    description="pyusb + hotplugging + async events",
    author_email="support@elevated.app",
    url="https://github.com/elevationsoftware/hotplug",
    keywords=["usb", "hotplug", "unplug"],
    packages=find_packages(),
    package_data={},
    install_requires=requires
)
