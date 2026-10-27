from carga_datos import Datos
from parametros import Parametros
from zonifica import zonificar

class ModeloRutas:
    def __init__(self, datos: Datos, params: Parametros):
        self.d = datos
        self.p = params
        self.slot_cedis: list = []

    def detalle_ruta(self, cedis, ruta):
        if not ruta:
            return dict(km=0.0, horas=0.0, carga=0.0, exc_carga=0.0, exc_jornada=0.0, exc_perec=0.0)
        p, dist = self.p, self.d.dist
        km, t, carga, exc_perec, prev = 0.0, 0.0, 0.0, 0.0, cedis
        for s in ruta:
            tramo = dist[prev][s]
            km += tramo
            t += tramo / p.velocidad_kmh
            exc_perec += max(0.0, t - p.max_horas_perecedero)
            t += p.min_descarga / 60.0
            carga += self.d.demanda[s]
            prev = s
        tramo = dist[prev][cedis]
        km += tramo
        t += tramo / p.velocidad_kmh
        return dict(km=km, horas=t, carga=carga,
                    exc_carga=max(0.0, carga / self.d.capacidad - 1.0),
                    exc_jornada=max(0.0, t - p.jornada_max_h),
                    exc_perec=exc_perec)

    def es_factible(self, cedis, ruta):
        d = self.detalle_ruta(cedis, ruta)
        return d["exc_carga"] == 0 and d["exc_jornada"] == 0 and d["exc_perec"] == 0

    def costo_combustible_ruta(self, km):
        return km / self.p.rendimiento_km_l * self.p.precio_litro

    def costo_ruta(self, cedis, ruta):
        if not ruta:
            return 0.0
        d = self.detalle_ruta(cedis, ruta)
        p = self.p
        penal = (p.pen_capacidad * d["exc_carga"]
                 + p.pen_tiempo_h * (d["exc_jornada"] + d["exc_perec"]))
        return self.costo_combustible_ruta(d["km"]) + p.costo_fijo_ruta + penal

    def evaluar(self, sol):
        km = horas = litros = horas_max = 0.0
        usadas = violaciones = 0
        for k, ruta in enumerate(sol):
            if not ruta:
                continue
            d = self.detalle_ruta(self.slot_cedis[k], ruta)
            usadas += 1
            km += d["km"]
            horas += d["horas"]
            horas_max = max(horas_max, d["horas"])
            litros += d["km"] / self.p.rendimiento_km_l
            if not self.es_factible(self.slot_cedis[k], ruta):
                violaciones += 1
        return dict(distancia_km=km, litros=litros,
                    costo_combustible=litros * self.p.precio_litro,
                    costo_total=sum(self.costo_ruta(self.slot_cedis[k], r) for k, r in enumerate(sol)),
                    horas_acumuladas=horas, horas_ruta_mas_larga=horas_max,
                    rutas_usadas=usadas, rutas_con_violaciones=violaciones)

    def solucion_baseline(self):
        zonas = zonificar(self.d)
        rutas_por_cedis = {c: [] for c in self.d.cedis}

        for c, pendientes in zonas.items():
            pendientes = list(pendientes)
            while pendientes:
                ruta, actual = [], c
                while pendientes:
                    sig = min(pendientes, key=lambda t: self.d.dist[actual][t])
                    if ruta and not self.es_factible(c, ruta + [sig]):
                        break
                    ruta.append(sig)
                    pendientes.remove(sig)
                    actual = sig
                rutas_por_cedis[c].append(ruta)

        sol, self.slot_cedis = [], []
        for c in self.d.cedis:
            rutas = rutas_por_cedis[c]
            for k in range(max(self.p.vehiculos_por_cedis, len(rutas))):
                sol.append(list(rutas[k]) if k < len(rutas) else [])
                self.slot_cedis.append(c)
        return sol