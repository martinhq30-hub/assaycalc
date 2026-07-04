# mining-assay-toolkit

Herramientas en Python para el procesamiento y validación de datos de assay geológico (sondajes de exploración minera).

## Instalación

```bash
pip install mining-assay-toolkit
```

## Uso rápido

```python
from mining_assay_toolkit import leer_csv_assay, validar_assay, componer_assay, guardar_csv

# 1. Leer datos de assay desde un CSV
df = leer_csv_assay("assay_original.csv")

# 2. Validar integridad de los datos
validar_assay(df)

# 3. Generar compósitos de 2 metros ponderados por ley de Cu
df_compositos = componer_assay(df, longitud_composito=2.0)

# 4. Guardar el resultado
guardar_csv(df_compositos, "assay_compuesto.csv")
```

## Formato de entrada esperado

El CSV debe contener, como mínimo, estas columnas:

| Columna    | Descripción                          |
|------------|---------------------------------------|
| `hole_id`  | Identificador del sondaje             |
| `from`     | Profundidad inicial del intervalo (m) |
| `to`       | Profundidad final del intervalo (m)   |
| `Cu_pct`   | Ley de cobre (%) en el intervalo      |

## Validaciones incluidas

`validar_assay()` verifica automáticamente:

- Que no existan `hole_id` vacíos
- Que todos los intervalos tengan `from < to`
- Que no existan leyes de `Cu_pct` negativas
- Que no existan intervalos solapados dentro de un mismo sondaje

Si alguna validación falla, se lanza un `ValueError` con el detalle del problema.

## Compositado

`componer_assay()` divide cada sondaje en intervalos de longitud fija (por ejemplo, cada 2 metros) y calcula la ley promedio ponderada por la longitud de cada intervalo original que cae dentro del compósito.

## Licencia

MIT — ver [LICENSE](LICENSE) para más detalles.