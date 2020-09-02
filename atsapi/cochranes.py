import time
import dbm
import json
from aiohttp import web
from atspythonutils.atsheadings import converttogrc
from atspythonutils.atsobjs import Point


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
    try:
        with dbm.open(request.app['cochranedb'], 'r') as db:
            k = db.firstkey()
            while k is not None:
                rval[k.decode("utf8")] = json.loads(db[k])
                k = db.nextkey(k)
    except dbm.error as e:
        return web.HTTPServerError(body=str(e))
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
    key = "{x} {y} {z}".format(**p._asdict())
    # value = "{} {} {}".format(cochranes, vessel, time.time())
    value = {
        "cochranes": cochranes,
        "vessel": vessel,
        "timestamp": time.time()
    }
    try:
        with dbm.open(request.app['cochranedb'], 'w') as db:
            db[key] = json.dumps(value)
    except dbm.error as e:
        return web.HTTPError(body=str(e))
    return web.Response(body="Added {}: {}".format(key, value))
    