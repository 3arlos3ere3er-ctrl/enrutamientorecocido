# Enrutamiento de tiendas

Proyecto de optimización de rutas de distribución mediante recocido simulado.

## Requisitos

- Python 3.9 o posterior
- Un archivo de entrada llamado `datos_distribucion_tiendas.xlsx` en la carpeta del proyecto

El archivo de datos no está incluido en este repositorio. Debe contener las columnas `Nombre`, `Tipo`, `Latitud_WGS84`, `Longitud_WGS84` y `Capacidad_Venta`; en `Tipo` se deben identificar al menos un centro y una tienda.

## Instalación

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Coloca `datos_distribucion_tiendas.xlsx` junto a `main.py` y ejecuta:

```bash
python main.py
```

El programa genera `resultados_rutas.xlsx` y `convergencia.png`. Estos archivos y los Excel locales se excluyen del control de versiones.
