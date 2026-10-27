import math
from dataclasses import dataclass

import pandas as pd

from parametros import Parametros


@dataclass
class Datos:
    nombres: list
    cedis: list
    tiendas: list
    dist: list
    demanda: list
    capacidad: float


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def cargar_datos(ruta_excel: str, params: Parametros) -> Datos:
    df = pd.read_excel(ruta_excel)

    requeridas = ["Nombre", "Tipo", "Latitud_WGS84", "Longitud_WGS84", params.col_demanda]
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en el Excel: {faltan}")

    nombres = df["Nombre"].astype(str).tolist()
    tipos = df["Tipo"].astype(str).str.lower().tolist()
    cedis = [i for i, t in enumerate(tipos) if "centro" in t]
    tiendas = [i for i, t in enumerate(tipos) if "tienda" in t]
    if not cedis or not tiendas:
        raise ValueError("El Excel debe contener al menos un CEDIS y una tienda en la columna 'Tipo'.")

    lat = df["Latitud_WGS84"].astype(float).tolist()
    lon = df["Longitud_WGS84"].astype(float).tolist()
    n = len(df)
    dist = [[haversine_km(lat[i], lon[i], lat[j], lon[j]) * params.factor_calle
             for j in range(n)] for i in range(n)]

    dem = pd.to_numeric(df[params.col_demanda], errors="coerce")
    dem = dem.fillna(dem.iloc[tiendas].mean())
    demanda = dem.tolist()

    total = sum(demanda[t] for t in tiendas)
    cap = params.capacidad_vehiculo or total / len(tiendas) * params.tiendas_por_ruta_objetivo
    capacidad = max(cap, max(demanda[t] for t in tiendas))

    return Datos(nombres, cedis, tiendas, dist, demanda, capacidad)
