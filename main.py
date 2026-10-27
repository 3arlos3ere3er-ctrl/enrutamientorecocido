from analizador import (comparar, exportar_excel, graficar_convergencia,
                        imprimir_comparacion, tabla_rutas)
from carga_datos import cargar_datos
from parametros import Parametros
from recocido import RecocidoSimulado
from rutas import ModeloRutas

ARCHIVO_EXCEL = "datos_distribucion_tiendas.xlsx"
N_CORRIDAS = 10
MAX_ITER = 30000


def main(archivo_excel=ARCHIVO_EXCEL, n_corridas=N_CORRIDAS, max_iter=MAX_ITER):
    params = Parametros()

    print("Cargando datos desde Excel...")
    datos = cargar_datos(archivo_excel, params)
    modelo = ModeloRutas(datos, params)
    print(f"{len(datos.cedis)} CEDIS | {len(datos.tiendas)} sucursales | "f"capacidad por vehículo: {datos.capacidad:,.1f}")

    sol_base = modelo.solucion_baseline()
    metricas_base = modelo.evaluar(sol_base)

    metricas_sa, historiales = [], []
    mejor_sol, mejor_costo = None, float("inf")
    for corrida in range(n_corridas):
        sa = RecocidoSimulado(modelo, max_iter=max_iter, semilla=corrida)
        sol, costo, historial, T0 = sa.ejecutar(sol_base)
        metricas_sa.append(modelo.evaluar(sol))
        historiales.append(historial)
        if costo < mejor_costo:
            mejor_sol, mejor_costo = sol, costo
        print(f"  corrida {corrida + 1:>2}/{n_corridas}: costo objetivo = ${costo:,.2f} (T0 = {T0:,.2f})")

    comparacion = comparar(metricas_base, metricas_sa)
    imprimir_comparacion(comparacion, metricas_base, metricas_sa)

    rutas_sa = tabla_rutas(modelo, mejor_sol)

    exportar_excel("resultados_rutas.xlsx", comparacion, rutas_sa, tabla_rutas(modelo, sol_base))
    graficar_convergencia(historiales, metricas_base["costo_total"])

if __name__ == "__main__":
    main()