import sdl2
import sdl2.ext
from PIL import Image

import time
import pathlib
from dataclasses import dataclass
import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.resolve()

def lado(inicio, fin, punto):
    return (
        (fin[0] - inicio[0]) * (punto[1] - inicio[1])
        - (fin[1] - inicio[1]) * (punto[0] - inicio[0])
    )


def dentro_triangulo(p, a, b, c):
    r1 = lado(a, b, p)
    r2 = lado(b, c, p)
    r3 = lado(c, a, p)

    return (
        (r1 >= 0 and r2 >= 0 and r3 >= 0) or
        (r1 <= 0 and r2 <= 0 and r3 <= 0)
    )

def proyectar(v, f):
    x, y, z = v
    if z <= 0:
        return None
    return (
        ANCHO / 2 + f * x / z,
        ALTO / 2 - f * y / z
    )

def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]

def uv_en_punto(p, a, b, c, uv_a, uv_b, uv_c):
    denom = cross((b[0] - a[0], b[1] - a[1]),
                  (c[0] - a[0], c[1] - a[1]))

    if denom == 0:
        return None  # triángulo degenerado

    w_b = cross((p[0] - a[0], p[1] - a[1]),
                (c[0] - a[0], c[1] - a[1])) / denom

    w_c = cross((b[0] - a[0], b[1] - a[1]),
                (p[0] - a[0], p[1] - a[1])) / denom

    w_a = 1.0 - w_b - w_c

    za, zb, zc = a[2], b[2], c[2]

    inv_z = w_a / za + w_b / zb + w_c / zc
    if inv_z == 0:
        return None

    u = (w_a * uv_a[0] / za +
         w_b * uv_b[0] / zb +
         w_c * uv_c[0] / zc) / inv_z

    v = (w_a * uv_a[1] / za +
         w_b * uv_b[1] / zb +
         w_c * uv_c[1] / zc) / inv_z

    z = 1.0 / inv_z
    return u,v,z

def getdata():
    file=open(PATH_DIR / "scene.json","r")
    r=file.split("\n")
    file.close()
    return r

# make a Vmem

sz = 200
ANCHO, ALTO = sz*4, sz*3

ZBF = [float("inf")] * ( ANCHO * ALTO )
f = 150
obj="""
mtllib triangulo.mtl
o Triangulo

v -0.5 -0.3 0.5
v  0.5 -0.3 0.5
v  0.0  0.5 4.0

vt 0.0 0.0
vt 1.0 0.0
vt 0.5 1.0

usemtl MaterialTriangulo
f 1/1 2/2 3/3
"""

mtl="""
newmtl MaterialTriangulo
Kd 1.0 1.0 1.0
map_Kd textura.png
"""

# Coordenadas de los tres vértices
a = (-0.5, -0.3, 0.5) # xy = ( a[0] / a[2], a[1] / a[2] )
b = ( 0.5, -0.3, 0.5)
c = ( 0.0,  0.5, 4.0)
pa = proyectar(a,f)
pb = proyectar(b,f)
pc = proyectar(c,f)
ra = (*pa, a[2])
rb = (*pb, b[2])
rc = (*pc, c[2])

# UV asignadas a los vértices: (u, v)
uv_a = (0.0, 0.0)
uv_b = (1.0, 0.0)
uv_c = (0.5, 1.0)

# Carga la imagen que se usará como textura
textura = Image.open( ROOT_DIR / "textura.png" ).convert("RGB")
tex_w, tex_h = textura.size

sdl2.ext.init()

ventana = sdl2.SDL_CreateWindow(
    b"Triangulo con PySDL2",
    sdl2.SDL_WINDOWPOS_CENTERED,
    sdl2.SDL_WINDOWPOS_CENTERED,
    ANCHO,
    ALTO,
    sdl2.SDL_WINDOW_SHOWN,
)

if not ventana:
    raise RuntimeError("No se pudo crear la ventana")

# Este ejemplo calcula los píxeles en la CPU; no usa un shader.
renderizador = sdl2.SDL_CreateRenderer(
    ventana,
    -1,
    sdl2.SDL_RENDERER_ACCELERATED
)

if not renderizador:
    raise RuntimeError("No se pudo crear el renderizador")

# Calcula la caja mínima que contiene el triángulo y limítala a la ventana.
min_x = max(0,         int(min(pa[0], pb[0], pc[0])))
max_x = min(ANCHO - 1, int(max(pa[0], pb[0], pc[0])))
min_y = max(0,         int(min(pa[1], pb[1], pc[1])))
max_y = min(ALTO - 1,  int(max(pa[1], pb[1], pc[1])))

eventos = sdl2.SDL_Event()

@dataclass
class Engine:
    loop: bool
    update: bool
    fps: float

engine=Engine(loop=True, update=True, fps=1/60)

while engine.loop:
    while sdl2.SDL_PollEvent(eventos):
        if eventos.type == sdl2.SDL_QUIT:
            engine.loop = False

    it=time.time()

    #now = getdata()

    if engine.update:
        ZBF = [float("inf")] * ( ANCHO * ALTO )
        # Fondo oscuro
        sdl2.SDL_SetRenderDrawColor(renderizador, 25, 25, 30, 255)
        sdl2.SDL_RenderClear(renderizador)

        # Color del triángulo: naranja
        sdl2.SDL_SetRenderDrawColor(renderizador, 255, 100, 30, 255)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                # Usar el centro del píxel suele dar un resultado más uniforme.
                punto = (x + 0.5, y + 0.5)


                if dentro_triangulo(punto, ra, rb, rc):
                    # preguntas:
                    # el calculo de z deveria de estar dentro de la funcion uv_en_punto?
                    indice = x + y * ANCHO
                    uvz = uv_en_punto(punto, ra, rb, rc, uv_a, uv_b, uv_c) 
                    if uvz is not None:
                        u,v,z=uvz
                        if z < ZBF[indice]:
                            ZBF[indice] = z
                            #divujar
                            # Pillow cuenta las filas desde arriba.
                            tx = max(0, min(tex_w - 1, int(u * (tex_w - 1))))
                            ty = max(0, min(tex_h - 1, int(v * (tex_h - 1))))

                            sdl2.SDL_SetRenderDrawColor(
                                renderizador, *textura.getpixel((tx, ty)), 255
                            )
                            sdl2.SDL_RenderDrawPoint(renderizador, x, y)
        engine.update=False

    sdl2.SDL_RenderPresent(renderizador)
    if (time.time()-it)<engine.fps:
        time.sleep(engine.fps-(time.time()-it))

sdl2.SDL_DestroyRenderer(renderizador)
sdl2.SDL_DestroyWindow(ventana)
sdl2.ext.quit()

