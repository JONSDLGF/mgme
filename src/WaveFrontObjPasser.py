# By Jon M. GPLv3 (C)2026

from pathlib import Path

def parse_obj(path):
    '''
    this fn is a paser
    name `parse_obj`
    arguments `path`
    output `tuple`
    '''
    vertices = []
    uvs = []
    normals = []
    faces = []
    material_libraries = []

    with Path(path).open(encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            # Ignora comentarios y líneas vacías
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            parts = line.split()
            kind, values = parts[0], parts[1:]

            if kind == "v":
                vertices.append(tuple(map(float, values[:3])))

            elif kind == "vt":
                uvs.append(tuple(map(float, values[:2])))

            elif kind == "vn":
                normals.append(tuple(map(float, values[:3])))

            elif kind == "f":
                face = []

                for token in values:
                    # Cada vértice de cara puede ser v, v/vt o v/vt/vn
                    indices = token.split("/")
                    vi = obj_index(indices[0], len(vertices))
                    ti = obj_index(indices[1], len(uvs)) if len(indices) > 1 and indices[1] else None
                    ni = obj_index(indices[2], len(normals)) if len(indices) > 2 and indices[2] else None
                    face.append((vi, ti, ni))

                faces.append(face)

            elif kind == "mtllib":
                material_libraries.extend(values)

    return vertices, uvs, normals, faces, material_libraries


def obj_index(text, current_count):
    """Convierte un índice OBJ a índice Python (base 0)."""
    index = int(text)

    if index == 0:
        raise ValueError("Los índices OBJ no pueden ser 0")

    result = index - 1 if index > 0 else current_count + index

    if not 0 <= result < current_count:
        raise ValueError(f"Índice OBJ fuera de rango: {index}")

    return result

if __name__=='__main__':
    src = Path(__file__).resolve().parent
    name = "test"
    obj_path = src / "modls" / name / f"{name}.obj"

    vs, uv, ns, faces, mtllibs = parse_obj(obj_path)

    print(f"Vértices: {len(vs)}")
    print(f"UVs: {len(uv)}")
    print(f"Normales: {len(ns)}")
    print(f"Caras: {len(faces)}")
    print(f"Bibliotecas de materiales: {mtllibs}")
