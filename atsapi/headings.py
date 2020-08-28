from aiohttp import web
from atspythonutils.atsheadings import findobjectsalongline


async def findborder(request:web.Request) -> web.Response:
    """
    ---
    description: Find border by name or partial name, or list all borders
    tags:
        - Borders
    parameters:
        - in: query
          name: border
          description: Name or partial name of a border, default all borders returned
        - in: query
          name: output
          description: CSV or JSON, default CSV
    produces:
        - text/plain
    responses:
        "200":
            description: Successfully scanned borders, even if non are returned
        "400":
            description: Could not find border by name
    """
    name = request.query.get("border", None)
    output = request.query.get("output", "csv")
    atsborders = request.app['atsborders']
    if name in atsborders:
        border = atsborders.get(name)
        candidates = {name: border._asdict()}
    elif not name:
        candidates = {bname: border._asdict() for bname, border in atsborders.items()}
    else: 
        candidates = {bname: border._asdict() for bname, border in atsborders.items() if name.lower() in bname.lower()}
    if output == "json":
        return web.json_response(candidates)
    ostr = ""
    for bname, border in candidates.items():
        ostr += "{0} Coords: X: {x} Y: {y} Z: {z}\n".format(bname, **border)
    return web.Response(body=ostr)


        

async def objectsonline(request:web.Request) -> web.Response:
    """
    ---
    description: Takes several paraemeters (coordinates and a heading) and determines possible objects along that line
    tags:
        - ObjectsOnLine
    parameters:
        - in: query
          name: x
          description: X Corrdinate
        - in: query
          name: y
          description: Y Coordinate
        - in: query
          name: z
          description: Z Corrdinate
        - in: query
          name: yaw
          description: Yaw angle
        - in: query
          name: pitch 
          description: Pitch Angle
        - in: query
          name: frame
          description: Name of the empire for the frame the coordinates are in
          required: false
        - in: query
          name: output
          description: Switched output from plaintext
        - in: query
          name: radius
          description: Length of the virutal line used to determine matches default 1000
          required: false
    produces:
        - text/plain
    responses:
        "200": 
            description: "Successfully was able to caculate objects, even if none were returned"
        "400":
            description: "An error in the query was detected"
    """
    x = float(request.query.get('x'))
    y = float(request.query.get('y'))
    z = float(request.query.get('z'))
    yaw = float(request.query.get('yaw'))
    pitch = float(request.query.get('pitch'))
    frame_slug = request.query.get('frame', None)
    output = request.query.get('output', 'csv')
    d = float(request.query.get('radius', 1000))
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
    return_string = "Objects along line defined by Point {}, {}, {} and heading {}, {}:\n".format(
        x, y, z,
        yaw, pitch
    )
    if output == "json":
        output_list = []
        for d, obj in findobjectsalongline(x, y, z, yaw, pitch, request.app['atsdb'], request.app['atsborders'], frame):
            o = obj.tojson()
            o['distance'] = d
            output_list.append(o)
        return web.json_response(output_list)

        
    return_string += "\n\n"
    return_string += "{0:<25s}\t{1:15s}\t{2:10s}\t{3:10s}\n".format(
        "Name of Object",
        "Empire",
        "Type",
        "Distance (PC)"
    ) 
    return_string += "=" * 80 + "\n" 
    for d, obj in findobjectsalongline(x, y, z, yaw, pitch, request.app['atsdb'], request.app['atsborders'], frame):
        return_string += "{0:<25s}\t{1:15s}\t{2:10s}\t[{3:>.2f}]\n".format(
            obj.name,
            obj.empire,
            obj.type,
            d
        )  
    return web.Response(body=return_string)

