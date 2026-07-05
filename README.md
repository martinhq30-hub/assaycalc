# assaycalc

Herramientas en Python para el procesamiento y validación de datos de assay geológico (sondajes de exploración minera).

## Instalación

```bash
pip install assaycalc
```

## Uso rápido

```python
from assaycalc import leer_csv_assay, validar_assay, componer_assay, guardar_csv

COLUMNAS_LEY = ["Cu_pct"]  # Agrega aquí cualquier otra ley: "Au_gpt", "Ag_gpt", etc.

# 1. Leer datos de assay desde un CSV
df = leer_csv_assay("assay_original.csv", columnas_ley=COLUMNAS_LEY)

# 2. Validar integridad de los datos
validar_assay(df, columnas_ley=COLUMNAS_LEY)

# 3. Generar compósitos de 2 metros ponderados por cada ley indicada
df_compositos = componer_assay(df, longitud_composito=2.0, columnas_ley=COLUMNAS_LEY)

# 4. Guardar el resultado (usa separador=";" si vas a abrirlo directo en Excel en español)
guardar_csv(df_compositos, "assay_compuesto.csv")
```

## Formato de entrada esperado

El CSV debe contener, como mínimo, estas columnas:

| Columna    | Descripción                            |
|------------|------------------------------------------|
| `hole_id`  | Identificador del sondaje               |
| `from`     | Profundidad inicial del intervalo (m)   |
| `to`       | Profundidad final del intervalo (m)     |

Además, debe incluir **una o más columnas de ley** (por ejemplo `Cu_pct`, `Au_gpt`, `Ag_gpt`), indicadas explícitamente mediante el parámetro `columnas_ley` en cada función.

## Validaciones incluidas

`validar_assay()` verifica automáticamente:

- Que no existan `hole_id` vacíos
- Que todos los intervalos tengan `from < to`
- Que no existan leyes negativas en ninguna de las columnas indicadas en `columnas_ley`
- Que no existan intervalos solapados dentro de un mismo sondaje

Si alguna validación falla, se lanza un `ValueError` con el detalle del problema.

## Compositado

`componer_assay()` divide cada sondaje en intervalos de longitud fija (por ejemplo, cada 2 metros) y calcula, para cada ley indicada en `columnas_ley`, el promedio ponderado por la longitud de cada intervalo original que cae dentro del compósito.

## Trabajando con Collar (ubicación de sondajes)

Además de Assay, `assaycalc` permite leer y validar la tabla Collar, que contiene la ubicación de cada sondaje.

```python
from assaycalc import leer_csv_collar, validar_collar, validar_integridad_referencial

# 1. Leer datos de collar desde un CSV
df_collar = leer_csv_collar("collar.csv")

# 2. Validar integridad de collar (hole_id sin vacíos ni duplicados)
validar_collar(df_collar)

# 3. Verificar que todo hole_id de assay tenga su collar correspondiente
validar_integridad_referencial(df_collar, df)
```

### Formato de entrada esperado (Collar)

| Columna    | Descripción                          |
|------------|----------------------------------------|
| `hole_id`  | Identificador del sondaje (único)      |
| `x`        | Coordenada X del collar                |
| `y`        | Coordenada Y del collar                |
| `z`        | Coordenada Z (elevación) del collar    |

### Validaciones incluidas (Collar)

`validar_collar()` verifica que no existan `hole_id` vacíos ni duplicados (cada sondaje debe tener una única fila de collar).

`validar_integridad_referencial()` verifica que todo `hole_id` presente en Assay exista también en Collar, evitando sondajes "huérfanos" sin ubicación conocida.

## Exportar resultados

`guardar_csv()` acepta parámetros opcionales `separador` y `codificacion`. Por defecto usa coma (`,`) como separador, el estándar universal de CSV. Si vas a abrir el archivo con doble clic en Excel configurado en español, usa `separador=";"` para evitar que todo aparezca en una sola columna.

## Licencia

MIT — ver [LICENSE](https://github.com/martinhq30-hub/assaycalc/blob/main/LICENSE) para más detalles.