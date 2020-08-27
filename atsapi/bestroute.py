from aiohttp import web
from atspythonutils import get_best_route

async def getRoute(request:web.Request) -> web.Response:
  """
  ---
  description: Get Best route given a source and a destination
  tags:
    - bestroute
  parameters:
    - in: query
      name: source
      description: Name of source object like a planet or station
    - in: query
      name: dest
      description: Name of destination object like a planet or station
  produces:
    - text/plain
  responses:
    "200":
      description: "Route was found"
    "400":
      description: "Input parameters were missing"
  """
  params = request.query
  try:
    bestroute = get_best_route(request.app['atsdb'], params.get('source'), params.get('dest'))
  except ValueError as e:
    raise web.HTTPBadRequest(body=str(e))
  bestroute += "\n"
  return web.Response(body=bestroute)
