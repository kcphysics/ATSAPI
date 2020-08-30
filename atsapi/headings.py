from aiohttp import web
from atspythonutils.atsheadings import findobjectsalongline


async def findborder(request:web.Request) -> web.Response:
    """
    ---
    description: Find border by name or partial name, or list all borders
    tags:
        - Information
    parameters:
        - in: query
          name: border
          type: string
          description: Name or partial name of a border, default all borders returned
          required: false
        - in: query
          name: output
          type: string
          default: csv
          description: CSV or JSON, default CSV
          required: false
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
        - Destination Prediction
    parameters:
        - in: query
          name: x
          type: number
          description: X Corrdinate
        - in: query
          name: y
          type: number
          description: Y Coordinate
        - in: query
          name: z
          type: number
          description: Z Corrdinate
        - in: query
          name: yaw
          type: number
          description: Yaw angle
        - in: query
          name: pitch 
          type: number
          description: Pitch Angle
        - in: query
          name: speed
          description: Speed the object was travelling at
          type: number
          default: 16
        - in: query
          name: frame
          type: string
          description: Name of the empire for the frame the coordinates are in
          required: false
        - in: query
          name: output
          type: string
          default: csv
          description: Switched output from plaintext
        - in: query
          name: radius
          type: number
          description: Length of the virutal line used to determine matches default 1000
          required: false
          default: 1000
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
    speed = float(request.query.get('speed', 16))
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
        for d, t, obj in findobjectsalongline(x, y, z, yaw, pitch, request.app['atsdb'], request.app['atsborders'], speed=speed, frame=frame):
            o = obj.tojson()
            o['distance'] = d
            o['time'] = t
            output_list.append(o)
        return web.json_response(output_list)

        
    return_string += "\n\n"
    return_string += "{0:<25s}\t{1:15s}\t{2:10s}\t{3:20s}\t{4:10s}\n".format(
        "Name of Object",
        "Empire",
        "Type",
        "Time (Duration)", 
        "Distance (PC)"
    ) 
    return_string += "=" * 100 + "\n" 
    for d, t, obj in findobjectsalongline(x, y, z, yaw, pitch, request.app['atsdb'], request.app['atsborders'], speed=speed, frame=frame):
        return_string += "{0:<25s}\t{1:15s}\t{2:10s}\t{3:20s}\t[{4:>.2f}]\n".format(
            obj.name,
            obj.empire,
            obj.type,
            t,
            d
        )  
    return web.Response(body=return_string)

