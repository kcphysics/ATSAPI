#!/usr/bin/env python3
import json
import os
import dbm
import importlib_resources
import atspythonutils
from aiohttp import web
from aiohttp_swagger import setup_swagger
from argparse import ArgumentParser
from atspythonutils import loadObjects, loadBorders
from .ono import ono
from .bestroute import getRoute
from .headings import objectsonline, findborder, objectsonlinebyobject
from .cochranes import record_cochranes


async def build_app():
  parser = ArgumentParser(prog="ATS API Server")
  parser.add_argument("config", help="The location of the configuration file")
  args = parser.parse_args()
  app = web.Application()
  databsae_file = importlib_resources.files(atspythonutils).joinpath('data/atsdata.json')
  if args.config and os.path.isfile(args.config):
    with open(args.config, 'r') as f:
      config = json.loads(f.read())
    databsae_file = config.get('atsdb', None)
  print("ATS Nav Database file is: {}".format(databsae_file))
  app['atsdb'] = loadObjects(databsae_file)
  app['atsborders'] = loadBorders(databsae_file)
  dbm.open(config.get('cochranedb'), 'c')
  app['cochranedb'] = config.get('cochranedb')
  app.add_routes([
    web.get("/nearbyobjects", ono, allow_head=False),
    web.get("/bestroute", getRoute, allow_head=False),
    web.get("/predictdest", objectsonline, allow_head=False),
    web.get("/predictdestbyobject", objectsonlinebyobject, allow_head=False),
    web.get("/borders", findborder, allow_head=False),
    web.post("/recordcochranes", record_cochranes)
  ])

  setup_swagger(app)
  return app

async def runapp():
  web.run_app(build_app())

if __name__ == "__main__":
  runapp()
