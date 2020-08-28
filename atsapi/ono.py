from aiohttp import web
from atspythonutils import get_nearby_objects

ats_database = '/home/kcphysics/tmush_code/atsdata.json'

async def ono(request:web.Request):
  """
  ---
  description: Takes a request and returns JSON or CSV formatted information about nearby objects
  tags:
    - ObjectsNearObjects
  parameters:
    - in: query
      name: target
      description: Target object to check nearby objects like a planet or station
    - in: query
      name: radius
      description: Radius around the target to check, default is 200
      required: false
    - in: query
      name: nresults
      description: Number of results to fetch, by default it is 20
      required: false
    - in: query
      name: output
      description: Controls output format, can be json or csv, default is csv
      required: false
  produces:
    - text/plain
  responses:
    "200":
      description: Successfully located target object in database and returned results
    "400":
      description: Could not find target object
  """
  params = request.query
  isjson = params.get("output", "csv")
  target = params.get("target", "")
  radius = int(params.get("radius", 200))
  nres = int(params.get("nresults", 20))
  # ats_objects, target_obj = loadObjects(request.app['atsdb'])
  target_obj = None
  for k, v in request.app['atsdb'].items():
    if target.lower() in k.lower():
      target_obj = v
  if not target_obj:
    raise web.HTTPBadRequest(body="Target of {} is not a known ATS Object".format(target))
  psinr = get_nearby_objects(request.app['atsdb'], target_obj, radius=radius, nres=nres)
  if isjson == "json":
    l = [x.tojson() for x in psinr]
    return web.json_response(l)
  csv_response = "{0:<25s}\t{1:15s}\t{2:10s}\t{3:10s}\n".format(
    "Name of Object",
    "Empire",
    "Type",
    "Distance (PC)"
  )  
  csv_response += "=" * 80 + "\n" 
  for _, x in psinr:
    csv_response += "{0:<25s}\t{1:15s}\t{2:10s}\t[{3:>.2f}]\n".format(
      x.name,
      x.empire,
      x.type,
      x.dist
    )  
  res = web.Response(body=csv_response)
  return res
