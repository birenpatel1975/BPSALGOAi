#!/usr/bin/env python
"""
Repository root wrapper to run the application located in `bpsalgoAi/run.py`.
This allows starting the app from the workspace root using `python run.py`.
"""
import runpy
import sys
import os

HERE = os.path.dirname(__file__)
PKG_PATH = os.path.join(HERE, 'bpsalgoAi')
if PKG_PATH not in sys.path:
    sys.path.insert(0, PKG_PATH)

runpy.run_module('run', run_name='__main__')
