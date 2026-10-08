bootstrap.py
| - serverx.py
|   | - vm engine * expone la api -api> rendere.json
|   | - rendere client * lee el rendere.json -> dibuja lo que hay dentro de ello

render.json:
{
 "CAP": [[0,0,[...],0]] ; [actibate, enumtype, [types], *cam]; types [enumtype, **] 2D 0 = text, 1 = texture 3D 0 = idmodeltype
 "MOD": {} ; modelos 3D
 "IMG": {} ; imagenes
 "CAM": [ [[0,0,0], [1.4,6,3]] ] ; [pos, tortex/cos-sin]
}
