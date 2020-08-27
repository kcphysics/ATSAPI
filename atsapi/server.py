#!/usr/bin/env python3
import importlib_resources
import atspythonutils
from aiohttp import web
from aiohttp_swagger import setup_swagger
from .ono import ono
from .bestroute import getRoute
from atspythonutils import loadObjects


async def build_app():
  app = web.Application()
  databsae_file = importlib_resources.files(atspythonutils).joinpath('data/atsdata.json')
  print(databsae_file)
  app['atsdb'] = loadObjects(databsae_file)
  app.add_routes([
    web.get("/ono", ono, allow_head=False),
    web.get("/route", getRoute, allow_head=False)
  ])

  setup_swagger(app)
  return app

async def runapp():
  web.run_app(app)

if __name__ == "__main__":
  runapp()