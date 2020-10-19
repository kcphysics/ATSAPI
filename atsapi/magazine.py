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
    search_string = f".*?\|.*?\|{magid}\|.*?"
    magdb = request.app['magazinedb']
    with dbm.open(magdb, 'r') as db:
        results = [x for x in db.keys() if re.search(search_string, str(x))]
    res = []
    for x in results:
        title, magname, magid, page = x.decode('utf-8').strip("'").split("|")
        res.append({
            "title": title,
            "magname": magname,
            "magid": magid,
            "page": page,
            "key": base64.b16encode(x).decode('utf-8')
        })
    
    return {"results": res}

@aiohttp_jinja2.template("magazine_entry.jinja")
async def retrieve_magazine_entry(request:web.Request):
    magdb = request.app['magazinedb']
    magid = request.match_info.get('magid')
    key = request.match_info['key']
    keystr = base64.b16decode(key)
    with dbm.open(magdb, 'r') as db:
        entry = db.get(keystr)
    return {"entry": json.loads(entry.decode('utf-8'))}

@aiohttp_jinja2.template("magazines.jinja")
async def magazines(request:web.Request):
    magazine_counter = Counter()
    magazine_map = {}
    with dbm.open(request.app['magazinedb']) as db:
        key = db.firstkey()
        while key is not None:
            title, magname, magid, page = key.decode('utf-8').split("|")
            magazine_counter[magname] += 1
            magazine_map[magname] = magid
            key = db.nextkey(key)
    return {
        "magazines": magazine_map,
        "magazine_counts": magazine_counter
    }
    
    # return_string = f"<strong>PROVIDED MAGID: </strong>{magid}<br />"
    # return_string += f"<strong>PROVIDED PAGE: </strong>{page}<br />"
    # return_string += f"<strong>REGEX: </strong>{search_string}<br />"
    # if not page:
    #     return_string += "<strong>Results:</string><br/><ul>"
    #     for res in results:
    #         title, magname, magid, page = str(res).strip("'").split("|")
    #         return_string += f"<li>{magname}:<a href=/magazine/{magid}/{page}>{title}</a></li>"
    #     return_string += "</ul>"
    # elif page and len(results) == 1:
    #     with dbm.open(magdb, 'r') as db:
    #         entry = db[results[0]]
    #     return_string += "-" * 60
    #     return_string += json.dumps(json.loads(entry.decode("utf-8")), indent=2)
    #     return_string += "-" * 60

    # return web.Response(body=return_string, content_type="text/html")
