import sdl2
import sdl2.ext
from PIL import Image

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
        (r1 >= 0 and r2 >= 0 and r3 >= 0)
        or
        (r1 <= 0 and r2 <= 0 and r3 <= 0)
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

    u = w_a * uv_a[0] + w_b * uv_b[0] + w_c * uv_c[0]
    v = w_a * uv_a[1] + w_b * uv_b[1] + w_c * uv_c[1]

    return (u, v)

ANCHO, ALTO = 800, 600

# Coordenadas de los tres vértices
a = (150, 100)
b = (650, 180)
c = (350, 500)

# UV asignadas a los vértices: (u, v)
uv_a = (0.0, 0.0)
uv_b = (1.0, 0.0)
uv_c = (0.5, 1.0)

# Carga la imagen que se usará como textura
textura = Image.open("textura.png").convert("RGB")
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
min_x = max(0, min(a[0], b[0], c[0]))
max_x = min(ANCHO - 1, max(a[0], b[0], c[0]))
min_y = max(0, min(a[1], b[1], c[1]))
max_y = min(ALTO - 1, max(a[1], b[1], c[1]))

eventos = sdl2.SDL_Event()
ejecutando = True

while ejecutando:
    while sdl2.SDL_PollEvent(eventos):
        if eventos.type == sdl2.SDL_QUIT:
            ejecutando = False

    # Fondo oscuro
    sdl2.SDL_SetRenderDrawColor(renderizador, 25, 25, 30, 255)
    sdl2.SDL_RenderClear(renderizador)

    # Color del triángulo: naranja
    sdl2.SDL_SetRenderDrawColor(renderizador, 255, 100, 30, 255)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            # Usar el centro del píxel suele dar un resultado más uniforme.
            punto = (x + 0.5, y + 0.5)


            if dentro_triangulo(punto, a, b, c):
                uv = uv_en_punto(punto, a, b, c, uv_a, uv_b, uv_c)

                if uv is not None:
                    u, v = uv

                    # Pillow cuenta las filas desde arriba.
                    tx = max(0, min(tex_w - 1, int(u * (tex_w - 1))))
                    ty = max(0, min(tex_h - 1, int(v * (tex_h - 1))))

                    rojo, verde, azul = textura.getpixel((tx, ty))
                    sdl2.SDL_SetRenderDrawColor(
                        renderizador, rojo, verde, azul, 255
                    )
                    sdl2.SDL_RenderDrawPoint(renderizador, x, y)

    sdl2.SDL_RenderPresent(renderizador)

sdl2.SDL_DestroyRenderer(renderizador)
sdl2.SDL_DestroyWindow(ventana)
sdl2.ext.quit()




