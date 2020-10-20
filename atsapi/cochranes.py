import time
import dbm
import json
import re
import aiohttp_jinja2
from aiohttp import web
from atspythonutils.atsheadings import converttogrc
from atspythonutils.atsobjs import Point


async def rcochranes(db, x:float, y:float, z:float, cochranes:float, vessel:str="Not Provided"):
    """ Records the cochranes to the DBM database specified by dbm_file"""
    key = "reading|{} {} {}".format(x, y, z)
    # value = "{} {} {}".format(cochranes, vessel, time.time())
    value = {
        "cochranes": cochranes,
        "vessel": vessel,
        "timestamp": time.time()
    }
    await db.hmset_dict(key, value)
    # with dbm.open(dbm_file, 'w') as db:
    #     db[key] = json.dumps(value)
    return key, value

galcoord = re.compile("^\s*Galactic X Y Z:\s+(?P<X>[-]?\d+.\d+)\s+(?P<Y>[-]?\d+.\d+)\s+(?P<Z>[-]?\d+.\d+).*$")
#galcoord = re.compile("\s*Galactic X Y Z:\s*(?P<X>-?\d{1,6}\.\d{1,4})\s+(?P<Y>-?\d{1,6}\.\d{1,4})\s+(?P<Z>-?\d{1,6}\.\d{1,4})")
sname = re.compile("\s*Name:\s*(.*)\s+Class:.*")
creading = re.compile(".*Cochranes: (\d{1,6}\.\d{1,4})")

@aiohttp_jinja2.template("cochrane.jinja")
async def getcochraneform(request:web.Request) -> web.Response:
    """Gets the form for folks to use"""
    rdict = {
      "results": False
    }
    if request.method == "POST":
        x = None
        y = None
        z = None
        cochranes = None
        vessel = None
        data = await request.post()
        for line in data.get('helmstat', '').splitlines():
           coords = re.match(galcoord, line)
           if coords:
              x = float(coords.groups()[0])
              y = float(coords.groups()[1])
              z = float(coords.groups()[2])
           snames = re.match(sname, line)
           if snames:
              vessel = snames.groups()[0].strip()
           creadings = re.match(creading, line)
           if creadings:
              cochranes = float(creadings.groups()[0].strip())
        if not x or not y or not z or not cochranes:
            return {
                "results": True,
                "success": False
            }
        key, value = rcochranes(request.app['cochranedb'], x, y, z, cochranes=cochranes, vessel=vessel)
        rdict = {
          "results": True,
          "success": True,
          "key": key,
          "cochranes": cochranes,
          "vessel": vessel
        }
    return rdict

async def retrieve_cochranes(request:web.Request) -> web.Response:
    """
    ---
    description: Retrieves dictionaty of coordinates with cochrane/record information
    tags:
        - Cochrane Research
    parameters:
        - in: query
          name: output
          type: string
          default: csv
          description: CSV | JSON, controls output format
    produces:
        - text/plain
    responses:
        "200":
            description: Retrieved data
        "400":
            description: Client Error
    """
    output = request.query.get('output', 'csv')
    rval = {}
    cdb = request.app['cochranedb']
    cur = b'0'
    while cur:
        cur, keys = await cdb.scan(cur, match="reading|*")
        for key in keys:
            _, kstr = key.decode('utf-8').split("|")
            vals = await cdb.hgetall(key, encoding="utf-8")
            for ifield in ['cochranes', 'timestamp']:
                vals[ifield] = float(vals[ifield])
            rval[kstr] = vals
    if output.lower() == 'json':
        return web.json_response(rval)
    rstring = "{0:20s}\t{1:10s}\t{2:20s}\t{3:20s}\n".format("Galactic Coords", "Cochranes", "Timestamp", "Vessel")
    for k, v in rval.items():
        rstring += "{0:20s}\t{cochranes:10f}\t{timestamp:15.6f}\t{vessel:20s}\n".format(k, **v)
    return web.Response(body=rstring)

async def record_cochranes(request:web.Request) -> web.Response:
    """
    ---
    description: Will record a cochrane reading for a set of coordinates, assuming GRC frame unless otherwise specified
    tags:
        - Cochrane Research
    parameters:
        - in: query
          name: x
          required: true
          type: number
          description: X Corrdinate of the reading
        - in: query
          name: y
          required: true
          type: number
          description: Y Corrdinate of the reading
        - in: query
          name: z
          required: true
          type: number
          description: Z Corrdinate of the reading
        - in: query
          name: cochranes
          required: true
          type: number
          description: Cochrane reading
        - in: query
          name: frame
          required: false
          description: Frame of the reading, default is galactic
          type: string
        - in: query
          name: vessel
          required: false
          description: Name of the Vessel that took the reading
          type: string
    produces:
        - text/plain
    responses:
        "200":
            description: Recorded the Cochrane reading
        "400":
            description: Unable to record reading
    """
    frame = None
    x = float(request.query.get('x').strip("\\"))
    y = float(request.query.get('y').strip("\\"))
    z = float(request.query.get('z').strip("\\"))
    frame_slug = request.query.get('frame')
    cochranes = float(request.query.get('cochranes').strip("\\"))
    vessel = request.query.get('vessel', 'Anonymous')
    if frame_slug and frame_slug not in request.app['atsborders']:
        for k in request.app['atsborders'].keys():
            if frame_slug.lower() in k.lower():
                frame = k
    elif frame_slug in request.app['atsborders']:
        frame = frame_slug
    elif not frame_slug:
        frame = None
    else:
        return web.HTTPBadRequest(body="Frame {} is not a valid frame, these are the currently valid frames: {}".format(
            frame_slug, request.app['atsborders'].keys()
        ))
    p = Point(x, y, z)
    if frame:
        p = converttogrc(p, frame, request.app['atsborders'])
    key, value = await rcochranes(request.app['cochranedb'], cochranes=cochranes, vessel=vessel, **p._asdict())
    return web.Response(body="Added {}: {}".format(key, value))

