import statistics
import pandas as pd
from rutas import ModeloRutas

METRICAS = [("distancia_km", "Distancia total (km)"),
            ("costo_combustible", "Combustible (MXN)"),
            ("horas_acumuladas", "Tiempo acumulado (h)"),
            ("horas_ruta_mas_larga", "Ruta más larga (h)"),
            ("rutas_usadas", "Rutas usadas"),
            ("rutas_con_violaciones", "Rutas con violaciones")]


def tabla_rutas(modelo: ModeloRutas, sol) -> pd.DataFrame:
    nombres = modelo.d.nombres
    filas = []
    for k, ruta in enumerate(sol):
        if not ruta:
            continue
        c = modelo.slot_cedis[k]
        d = modelo.detalle_ruta(c, ruta)
        filas.append({
            "CEDIS": nombres[c],
            "Secuencia": " -> ".join([nombres[c]] + [nombres[s] for s in ruta] + [nombres[c]]),
            "Sucursales": len(ruta),
            "Carga": round(d["carga"], 2),
            "Capacidad": round(modelo.d.capacidad, 2),
            "Distancia_km": round(d["km"], 2),
            "Horas": round(d["horas"], 2),
            "Combustible_L": round(d["km"] / modelo.p.rendimiento_km_l, 2),
            "Costo_combustible_MXN": round(modelo.costo_combustible_ruta(d["km"]), 2),
        })
    return pd.DataFrame(filas)

def comparar(metricas_base: dict, metricas_sa: list) -> pd.DataFrame:
    filas = []
    for clave, nombre in METRICAS:
        valores = [r[clave] for r in metricas_sa]
        filas.append({"Métrica": nombre,
                      "Métrica Base": metricas_base[clave],
                      "Recocido Mejor": min(valores),
                      "Recocido Promedio": statistics.mean(valores),
                      "Recocido Desv Est": statistics.stdev(valores) if len(valores) > 1 else 0.0})
    return pd.DataFrame(filas)

def imprimir_comparacion(df: pd.DataFrame, metricas_base: dict, metricas_sa: list):
    mejor = min(r["costo_combustible"] for r in metricas_sa)
    prom = statistics.mean(r["costo_combustible"] for r in metricas_sa)
    base = metricas_base["costo_combustible"]
    print(f"\nAhorro de combustible vs métrica base: {(base - mejor) / base * 100:.1f} % (mejor corrida), "
          f"{(base - prom) / base * 100:.1f} % (promedio)")

def imprimir_rutas(df_rutas: pd.DataFrame):
    print("\nRUTAS DE LA MEJOR SOLUCIÓN:")
    for _, f in df_rutas.iterrows():
        print(f"  [{f['CEDIS']}] {f['Secuencia']}\n      "
              f"{f['Sucursales']} sucursales | {f['Distancia_km']} km | {f['Horas']} h | "
              f"carga {f['Carga']}/{f['Capacidad']} | ${f['Costo_combustible_MXN']:,.2f}")

def exportar_excel(archivo, comparacion, rutas_sa, rutas_base):
    with pd.ExcelWriter(archivo) as xw:
        metricas_excluidas = (
            "Tiempo acumulado (h)",
            "Ruta más larga (h)",
            "Rutas usadas",
            "Rutas con violaciones",
        )
        resumen_excel = comparacion[~comparacion["Métrica"].isin(metricas_excluidas)]
        resumen_excel.to_excel(xw, sheet_name="Resumen", index=False)
        rutas_sa.to_excel(xw, sheet_name="Rutas_mejor_solucion", index=False)
        rutas_base.to_excel(xw, sheet_name="Rutas_metrica_base", index=False)
        for hoja in xw.sheets.values():
            for fila in hoja.iter_rows():
                for celda in fila:
                    if isinstance(celda.value, float):
                        celda.number_format = "0.00"
    print(f"\nResultados guardados en {archivo}")


def graficar_convergencia(historiales, costo_baseline, archivo="convergencia.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib no está instalado: se omite la gráfica de convergencia)")
        return
    plt.figure(figsize=(8, 4.5))
    for h in historiales:
        plt.plot([i * 100 for i in range(len(h))], h, alpha=0.4)
    plt.axhline(costo_baseline, color="red", linestyle="--", label="Métrica base")
    plt.xlabel("Iteración")
    plt.ylabel("Mejor costo objetivo (MXN)")
    plt.title("Convergencia del recocido simulado (una curva por corrida)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(archivo, dpi=150)
    plt.close()
    print(f"Gráfica guardada en {archivo}")
