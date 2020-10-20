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
    cur = b'0'
    while cur:
        cur, keys = await missiondb.scan(cur, match="mission|*")
        for key in keys:
            val = await missiondb.hgetall(key, encoding='utf-8')
            val['load'], val['commod'] = val['cargo'].split('x')
            data [val.get('mission_number')] = val
    return {"missions": data}

@aiohttp_jinja2.template('markets.jinja')
async def get_markets(request:web.Request):
    missiondb = request.app['missiondb']
    data = {}
    cur = b'0'
    while cur:
        cur, keys = await missiondb.scan(cur, match="market|*")
        for key in keys:
            val = await missiondb.hgetall(key, encoding='utf-8')
            data [val.get('object')] = val
    return {"markets": data}

@aiohttp_jinja2.template('commods.jinja')
async def get_commodities(request:web.Request):
    econdb = request.app['missiondb']
    commod_map = {}
    cur = b'0'
    while cur:
        cur, keys = await econdb.scan(cur, match="commodity|*")
        for key in keys:
            _, commod_name, commod_number, _ = key.decode('utf-8').split("|")
            if commod_name not in commod_map:
                commod_map[commod_name] = {
                    "commod_number": commod_number,
                    "commods_count": 0
                }         
            commod_map[commod_name]['commods_count'] += 1
    return {"map": commod_map}


@aiohttp_jinja2.template('commodity.jinja')
async def get_commodity(request:web.Request):
    commod_number = request.match_info.get('commod_number')
    econdb = request.app['missiondb']
    cur = b'0'
    commods = []
    while cur:
        cur, keys = await econdb.scan(cur, match=f"commodity|*|{commod_number}|*")
        for key in keys:
            _, commod_name,_ ,_ = key.decode('utf-8').split('|')
            vals = await econdb.hgetall(key, encoding="utf-8")
            commods.append(vals)
    commod_high = max([int(x['price']) for x in commods])
    commod_low = min([int(x['price']) for x in commods])
    best_difference = commod_high - commod_low
    return {
        "commod_name": commod_name,
        "commod_number": commod_number,
        "commod_high": commod_high,
        "commod_low": commod_low,
        "best_difference": best_difference,
        "commods": commods
    }
