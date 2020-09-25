#!/usr/bin/env python3
# Project: OMRON 2JCIE-BU01
# Module:
from setuptools import setup
import sys
if sys.version_info < (3, 6):
    raise NotImplementedError("Sorry, you need at least Python 3.6 to use OMRON 2JCIE-BU01.")

import omron_2jcie_bu01
MODNAME = "omron_2jcie_bu01"

setup(
    name                = "omron-2jcie-bu01",
    version             = omron_2jcie_bu01.__version__,
    description         = "API for OMRON 2JCIE-BU01 Environment Sensor",
    long_description    = omron_2jcie_bu01.__doc__,
    author              = omron_2jcie_bu01.__author__,
    author_email        = "nobrin@biokids.org",
    url                 = "https://github.com/nobrin/omron-2jcie-bu01",
    py_modules          = [MODNAME, f"{MODNAME}.ble", f"{MODNAME}.serial"],
    scripts             = [f"{MODNAME}/__init__.py", f"{MODNAME}/ble.py", f"{MODNAME}/serial.py"],
    install_requires    = ["pyserial"],
    extras_require      = {"ble": ["bleak"]},
    license             = "MIT",
    platforms           = "any",
    classifiers         = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Home Automation",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
