from carga_datos import Datos

def zonificar(datos: Datos) -> dict:
    zonas = {c: [] for c in datos.cedis}
    for t in datos.tiendas:
        mas_cercano = min(datos.cedis, key=lambda c: datos.dist[c][t])
        zonas[mas_cercano].append(t)
    return zonas