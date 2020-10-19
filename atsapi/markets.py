import dbm
import json
import re
import aiohttp_jinja2
import base64
from collections import Counter
from aiohttp import web
from pprint import pprint

@aiohttp_jinja2.template('missions.jinja')
async def get_missions(request:web.Request):
    missiondb = request.app['missiondb']
    data = {}
    with dbm.open(missiondb, 'r') as db:
        key = db.firstkey()
        while key is not None:
            # enc_key = base64.b16encode(key).decode('utf-8')
            value = json.loads(db[key].decode('utf-8'))
            enc_key = value['mission_number'].replace("-", "").replace("#", "") 
            value['load'], value['commod'] = value['cargo'].split('x')
            data[enc_key] = value
            key = db.nextkey(key)
    return {"missions": data}
