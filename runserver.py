#!/usr/bin/env python3
from aiohttp import web
from atsapi import build_app

if __name__ == "__main__":
    web.run_app(build_app())