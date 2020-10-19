import json
from aiohttp import web


async def get_markets(request:web.Request):
    """
    ---
        description: Gets a list of objects that have markets associated with them
        tags:
            - Information
        parameters:
            - in: query
              name: organization
              type: string
              description: Organization to bound to, default is all
              required: false
              default: None
            - in: query
              name: withinfo
              type: int
              default: 1
              description: 1 -> Gives information, 0 -> Gives only names
              required: false
            - in: query
              name: output
              default: csv
              type: string
              description: Determines wether to give csv or JSON output
              required: false
        produces:
            - text/plain
        responses:
            "200":
                description: Successfully fetched market information, even if nothing returns
            "400":
                description: Client side EWrror
    """
    params = request.query
    output = params.get('output', 'csv')
    org = params.get('organization')
    withinfo = int(params.get('withinfo', 1))
    if org and org != "None":
        markets = [v.tojson() for _, v in request.app['atsdb'].items() if v.market > 0 and org.lower() in v.empire.lower()]
    else:
        markets = [v.tojson() for _, v in request.app['atsdb'].items() if v.market > 0]
    if not withinfo:
        return web.Response(body="\n".join(v['name'] for v in markets), content_type="text/plain")
    if output == "json":
        return web.json_response(json.dumps(markets))
    else:
        rstring = "{0:<25s}\t{1:15s}\t{2:10s}\t{3:10s}\n".format(
            "Name of Object",
            "Empire",
            "Type",
            "Market"
        )  
        for mark in markets:
            rstring += "{name:<25s}\t{empire:15s}\t{type:10s}\t{market:6d}\n".format(**mark)
        return web.Response(body=rstring, content_type="text/plain")


async def get_objs_by_org(request:web.Request):
    """
    ---
        description: Gets a list of objects that have markets associated with them
        tags:
            - Information
        parameters:
            - in: query
              name: organization
              type: string
              description: Organization to bound to, default is all
              required: false
              default: None
            - in: query
              name: withinfo
              type: int
              default: 1
              description: 1 -> Gives information, 0 -> Gives only names
              required: false
            - in: query
              name: type
              default: all
              type: string
              description: Can be all, planets, stations
              required: false
            - in: query
              name: output
              default: csv
              type: string
              description: Determines wether to give csv or JSON output
              required: false
        produces:
            - text/plain
        responses:
            "200":
                description: Successfully fetched market information, even if nothing returns
            "400":
                description: Client side EWrror
    """
    params = request.query
    output = params.get('output', 'csv')
    otype = params.get('type', 'all')
    org = params.get('organization')
    withinfo = int(params.get('withinfo', 1))
    if org and org != "None":
        markets = [v.tojson() for _, v in request.app['atsdb'].items() if org.lower() in v.empire.lower()]
    else:
        markets = [v.tojson() for _, v in request.app['atsdb'].items()]
    if otype != "all":
        markets = [x for x in markets if otype.lower() in x['type'].lower()]
    if not withinfo:
        return web.Response(body="\n".join(v['name'] for v in markets), content_type="text/plain")
    if output == "json":
        return web.json_response(markets)
    else:
        rstring = "{0:<25s}\t{1:15s}\t{2:10s}\t{3:10s}\n".format(
            "Name of Object",
            "Empire",
            "Type",
            "Market"
        )  
        for mark in markets:
            rstring += "{name:<25s}\t{empire:15s}\t{type:10s}\t{market:6d}\n".format(**mark)
        return web.Response(body=rstring, content_type="text/plain")
