import dbm
import json
import re
import base64
import aiohttp_jinja2
from collections import Counter
from aiohttp import web
from pprint import pprint

@aiohttp_jinja2.template("magazine_results.jinja")
async def retrieve_magazine_entries(request:web.Request):
    magid = request.match_info.get('magid')
    search_string = f"magazine|*|*|{magid}|*?"
    magdb = request.app['magazinedb']
    res = []
    cur = b'0'
    while cur:
        cur, keys = await magdb.scan(cur, match=search_string)
        for key in keys:
            val = await magdb.hgetall(key, encoding='utf-8')
            val["key"] = base64.b16encode(key).decode('utf-8')
            res.append(val)
    return {"results": res}

@aiohttp_jinja2.template("magazine_entry.jinja")
async def retrieve_magazine_entry(request:web.Request):
    magid = request.match_info.get('magid')
    key = request.match_info['key']
    magdb = request.app['magazinedb']
    keystr = base64.b16decode(key)
    entry = await magdb.hgetall(keystr, encoding="utf-8")
    return {"entry": entry}

@aiohttp_jinja2.template("magazines.jinja")
async def magazines(request:web.Request):
    magazine_counter = Counter()
    magazine_map = {}
    magdb = request.app['magazinedb']
    cur = b'0'
    while cur:
        cur, keys = await magdb.scan(cur, match="magazine|*")
        for key in keys:
            _, _, magname, magid, _ = key.decode('utf-8').split("|")
            magazine_counter[magname] += 1
            magazine_map[magname] = magid

    return {
        "magazines": magazine_map,
        "magazine_counts": magazine_counter
    }
    