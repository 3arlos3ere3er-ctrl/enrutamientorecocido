from dataclasses import dataclass
from typing import Optional


@dataclass
class Parametros:
    col_demanda: str = "Capacidad_Venta"
    capacidad_vehiculo: Optional[float] = None
    tiendas_por_ruta_objetivo: int = 8
    vehiculos_por_cedis: int = 2
    zonificacion_fija: bool = True

    factor_calle: float = 1.3
    velocidad_kmh: float = 30.0
    min_descarga: float = 10.0
    jornada_max_h: float = 8.0
    max_horas_perecedero: float = 4.0

    rendimiento_km_l: float = 6.0
    precio_litro: float = 24.5
    costo_fijo_ruta: float = 0.0

    pen_capacidad: float = 5000.0
    pen_tiempo_h: float = 1000.0
