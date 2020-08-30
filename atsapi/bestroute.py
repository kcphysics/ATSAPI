from aiohttp import web
from atspythonutils import get_best_route

async def getRoute(request:web.Request) -> web.Response:
  """
  ---
  description: Get Best route given a source and a destination
  tags:
    - Navigation
  parameters:
    - in: query
      name: source
      type: string
      description: Name of source object like a planet or station
    - in: query
      name: dest
      type: string
      description: Name of destination object like a planet or station
    - in: query
      name: speed
      type: number
      description: Warp speed, default 16
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
    bestroute = get_best_route(request.app['atsdb'], params.get('source'), params.get('dest'), float(params.get('speed', 16)))
  except ValueError as e:
    raise web.HTTPBadRequest(body=str(e))
  bestroute += "\n"
  return web.Response(body=bestroute)
