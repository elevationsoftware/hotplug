from setuptools import setup, find_packages

setup(
    name="Hotplug",
    version="1.0.0",
    description="pyusb + hotplugging + async events",
    author_email="support@elevated.app",
    url="https://github.com/elevationsoftware/hotplug",
    keywords=["usb", "hotplug", "unplug"],
    packages=find_packages(),
    package_data={}
)
