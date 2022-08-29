import os
from setuptools import setup, find_packages

requires = ['libusb1']
if os.name == 'nt':
    requires.append('pywin32')

setup(
    name="Hotplug",
    version="2.0.0",
    description="pyusb + hotplugging + async events",
    author_email="support@elevated.app",
    url="https://github.com/elevationsoftware/hotplug",
    keywords=["usb", "hotplug", "unplug"],
    packages=find_packages(),
    package_data={},
    install_requires=requires
)
