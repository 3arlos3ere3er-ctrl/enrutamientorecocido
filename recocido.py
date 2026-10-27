import math
import random
import statistics
from rutas import ModeloRutas

class RecocidoSimulado:
    def __init__(self, modelo: ModeloRutas, max_iter=30000,
                 razon_temp_final=1e-3, prob_aceptacion_inicial=0.5, semilla=None):
        self.m = modelo
        self.max_iter = max_iter
        self.razon_temp_final = razon_temp_final
        self.p0 = prob_aceptacion_inicial
        self.rng = random.Random(semilla)

    def _dos_opt(self, sol):
        cand = [k for k, r in enumerate(sol) if len(r) >= 2]
        if not cand:
            return None
        k = self.rng.choice(cand)
        r = sol[k]
        i, j = sorted(self.rng.sample(range(len(r)), 2))
        return {k: r[:i] + r[i:j + 1][::-1] + r[j + 1:]}

    def _reubicar(self, sol):
        no_vacias = [k for k, r in enumerate(sol) if r]
        a = self.rng.choice(no_vacias)
        i = self.rng.randrange(len(sol[a]))
        if self.m.p.zonificacion_fija:
            destinos = [k for k, c in enumerate(self.m.slot_cedis) if c == self.m.slot_cedis[a]]
        else:
            destinos = range(len(sol))
        b = self.rng.choice(destinos)
        if a == b:
            r = list(sol[a])
            s = r.pop(i)
            r.insert(self.rng.randrange(len(r) + 1), s)
            return {a: r}
        ra = sol[a][:i] + sol[a][i + 1:]
        rb = list(sol[b])
        rb.insert(self.rng.randrange(len(rb) + 1), sol[a][i])
        return {a: ra, b: rb}

    def _intercambiar(self, sol):
        no_vacias = [k for k, r in enumerate(sol) if r]
        if len(no_vacias) < 2:
            return None
        a = self.rng.choice(no_vacias)
        if self.m.p.zonificacion_fija:
            candidatos = [k for k in no_vacias if k != a and self.m.slot_cedis[k] == self.m.slot_cedis[a]]
        else:
            candidatos = [k for k in no_vacias if k != a]
        if not candidatos:
            return None
        b = self.rng.choice(candidatos)
        ra, rb = list(sol[a]), list(sol[b])
        i, j = self.rng.randrange(len(ra)), self.rng.randrange(len(rb))
        ra[i], rb[j] = rb[j], ra[i]
        return {a: ra, b: rb}

    def _vecino(self, sol):
        x = self.rng.random()
        mov = self._dos_opt(sol) if x < 0.34 else self._intercambiar(sol) if x > 0.75 else None
        return mov or self._reubicar(sol)

    def _calibrar_T0(self, sol, costos, muestras=300):
        peores = []
        for _ in range(muestras):
            mov = self._vecino(sol)
            delta = (sum(self.m.costo_ruta(self.m.slot_cedis[k], r) for k, r in mov.items())
                     - sum(costos[k] for k in mov))
            if delta > 0:
                peores.append(delta)
        promedio = statistics.mean(peores) if peores else 1.0
        return -promedio / math.log(self.p0)

    def ejecutar(self, sol_inicial):
        m = self.m
        sol = [list(r) for r in sol_inicial]
        costos = [m.costo_ruta(m.slot_cedis[k], r) for k, r in enumerate(sol)]
        actual = sum(costos)
        mejor, mejor_costo = [list(r) for r in sol], actual

        T = T0 = self._calibrar_T0(sol, costos)
        alfa = self.razon_temp_final ** (1.0 / self.max_iter)
        historial = []

        for it in range(self.max_iter):
            mov = self._vecino(sol)
            nuevos = {k: m.costo_ruta(m.slot_cedis[k], r) for k, r in mov.items()}
            delta = sum(nuevos.values()) - sum(costos[k] for k in mov)

            if delta < 0 or self.rng.random() < math.exp(-delta / max(T, 1e-12)):
                for k, r in mov.items():
                    sol[k], costos[k] = r, nuevos[k]
                actual += delta
                if actual < mejor_costo - 1e-9:
                    mejor, mejor_costo = [list(r) for r in sol], actual

            T *= alfa
            if it % 100 == 0:
                historial.append(mejor_costo)

        return mejor, mejor_costo, historial, T0