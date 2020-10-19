#!/usr/bin/env python3
import json
import os
import dbm
import importlib_resources
import atspythonutils
import logging
import pathlib
import jinja2
import aiohttp_jinja2
from aiohttp import web
from aiohttp_swagger import setup_swagger
from argparse import ArgumentParser
from atspythonutils import loadObjects, loadBorders
from .ono import ono
from .bestroute import getRoute
from .headings import objectsonline, findborder, objectsonlinebyobject
from .cochranes import record_cochranes, retrieve_cochranes, getcochraneform
from .magazine import retrieve_magazine_entries, retrieve_magazine_entry, magazines
from .dbinfo import get_markets, get_objs_by_org
from .markets import get_missions


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
  #logging.basicConfig(level=logging.DEBUG)
  app['atsdb'] = loadObjects(databsae_file)
  app['atsborders'] = loadBorders(databsae_file)
  dbm.open(config.get('cochranedb'), 'c')
  app['cochranedb'] = config.get('cochranedb')
  app['magazinedb'] = config.get('magazinedb')
  app['missiondb'] = config.get('missiondb')
  app.add_routes([
    web.get("/nearbyobjects", ono, allow_head=False),
    web.get("/bestroute", getRoute, allow_head=False),
    web.get("/predictdest", objectsonline, allow_head=False),
    web.get("/predictdestbyobject", objectsonlinebyobject, allow_head=False),
    web.get("/borders", findborder, allow_head=False),
    web.post("/recordcochranes", record_cochranes),
    web.get("/retrievecochranes", retrieve_cochranes, allow_head=False),
    web.get("/cochranes", getcochraneform, allow_head=False, name="cochraneform"),
    web.post("/cochranes", getcochraneform),
    web.get("/magazine/{magid:\d+}", retrieve_magazine_entries, allow_head=False),
    web.get("/magazine/{magid:\d+}/{key}", retrieve_magazine_entry, allow_head=False),
    web.get("/magazine", magazines, allow_head=False),
    web.get("/markets", get_markets, allow_head=False),
    web.get("/objects", get_objs_by_org, allow_head=False),
    web.get("/missions", get_missions, allow_head=False)
  ])
  tpath = os.path.join(pathlib.Path(__file__).parent, "templates")
  print(tpath)
  aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(tpath))

  setup_swagger(app)
  return app

async def runapp():
  web.run_app(build_app())

if __name__ == "__main__":
  runapp()
