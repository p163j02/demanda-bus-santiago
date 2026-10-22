# Diccionario de salidas — Etapa II

Este documento explica qué representa cada archivo generado por `build_panel.py` y `etapa_ii_analysis.py`. Las salidas se guardan en `Etapa_02/resultados/`; los gráficos están en `figuras/`.

## Paneles CSV

### `panel_demanda_bus.csv` — panel observado

Una fila por combinación **corte × comuna reportada × tipo de día × franja de 30 minutos** que está presente en la fuente. Conserva las comunas reportadas, incluida `SIN_COMUNA`; no crea combinaciones ausentes.

| Columna | Significado |
|---|---|
| `periodo` | Corte de la fuente en formato `AAAA-MM` (por ejemplo, `2025-11`). |
| `comuna` | Nombre normalizado de la comuna; `SIN_COMUNA` indica que no se asignó una comuna. |
| `tipo_dia` | `LABORAL`, `SABADO` o `DOMINGO`. |
| `media_hora` | Inicio de la franja, de `00:00` a `23:30`, en intervalos de 30 minutos. |
| `subidas_promedio` | Suma agregada de `Subidas_Promedio` para buses de esa comuna, tipo de día y franja. Son subidas registradas/procesadas, no pasajeros corregidos por evasión. |

Tiene 20.051 filas en la versión actual.

### `panel_demanda_bus_modelo.csv` — panel balanceado para modelar

Contiene las mismas columnas y agrega `relleno_cero`:

- `relleno_cero = 0`: combinación presente en la tabla observada.
- `relleno_cero = 1`: combinación comuna/día/franja que no estaba en el corte y se completó provisionalmente con `subidas_promedio = 0`.

Incluye solo las **36 comunas comunes a los cuatro cortes**, excluye `SIN_COMUNA` y contiene 36 × 3 × 48 × 4 = **20.736 filas**. Los ceros añadidos son una hipótesis pendiente de validar: si una fila ausente significa falta de cobertura, no cero demanda, el panel y sus métricas deben revisarse.

## Calidad de fuentes

### `panel_quality_report.json`

El nivel superior tiene una sección por corte (`2024-11`, `2025-04`, `2025-11`, `2026-04`) y una sección `panel`.

| Campo por corte | Significado |
|---|---|
| `source` | Ruta relativa del libro Excel usado. |
| `sheet` | Hoja que se leyó. |
| `rows_total` | Filas examinadas en la hoja. |
| `rows_bus` / `rows_non_bus` | Filas reconocidas como BUS / de otros modos. |
| `rows_included` | Filas BUS que entraron a la agregación tras las validaciones. |
| `explicit_zero_rows` | Filas BUS con cero explícito en la fuente; no es lo mismo que los ceros que se completaron después. |
| `short_rows`, `missing_day`, `missing_time`, `invalid_time`, `non_half_hour_time`, `missing_or_invalid_target`, `negative_target` | Filas incompletas o descartadas por cada condición. En la corrida actual, estos conteos son cero. |
| `days`, `communes` | Valores de tipo de día y comunas encontradas en esa fuente. |

En `panel` se guardan las rutas y tamaños de los paneles, las 36 comunas comunes, el supuesto de completar ausencias a cero y el conteo de combinaciones observadas/completadas por período.

## Métricas de modelo

### `metricas_modelo_inicial.csv`

Cada fila compara un modelo en un corte de prueba concreto, sobre el mismo objetivo y las mismas celdas evaluadas.

| Columna | Significado |
|---|---|
| `corte_prueba` | Período futuro contra el cual se midió el pronóstico. |
| `entrenamiento` | Cortes anteriores disponibles para esa evaluación, en orden temporal. |
| `modelo` | `Último corte` repite para cada celda el valor del corte previo; `Media histórica` usa el promedio de sus cortes de entrenamiento; `HistGradientBoosting (lags por corte)` es el primer modelo de árboles. |
| `MAE` | Error absoluto medio. Se expresa en subidas por comuna × tipo de día × franja de 30 minutos; menor es mejor. |
| `RMSE` | Raíz del error cuadrático medio, en las mismas unidades; penaliza más los errores grandes; menor es mejor. |
| `WAPE_pct` | Suma de errores absolutos dividida por la suma de valores reales, ×100. Error porcentual agregado; menor es mejor. |
| `MAPE_positivos_pct` | Promedio del error porcentual absoluto calculado solo donde el valor real es positivo; evita dividir por cero. Puede ser sensible a valores reales pequeños. |

La prueba principal reservada es abril de 2026. La evaluación temporal interna de noviembre de 2025 es importante: el HistGradientBoosting quedó por debajo de la media histórica allí. Con solo cuatro cortes, los resultados siguen siendo preliminares. El modelo usa el último corte y la media de cortes anteriores como variables históricas; **no** usa rezagos de media hora como `t-1` o `t-48`.

## Figuras

| Archivo | Qué muestra | Cómo leerlo |
|---|---|---|
| `figuras/subidas_por_corte_y_dia.png` | Suma del panel por corte para días laborales, sábados y domingos. | Compara magnitudes y cambios por tipo de día; no atribuye por sí sola esos cambios a una causa. |
| `figuras/perfil_horario_laboral.png` | Suma por franja de 30 minutos en día laboral, una línea por corte. | Permite comparar forma horaria y horas punta entre cortes. |
| `figuras/top_comunas_2026_laboral.png` | Diez comunas con mayor suma laboral en el corte de abril de 2026. | Ordena las comunas del panel de 36 comunas comunes; no representa todas las comunas cubiertas en abril de 2026. |

Todas las sumas y gráficos describen `Subidas_Promedio` agregadas: no deben rotularse como total real de pasajeros ni mezclarse numéricamente con el factor de expansión de la Tabla de Etapas.

## Salidas impresas en el notebook

Además de los archivos anteriores, el notebook muestra en pantalla:

- **Control de cobertura:** filas observadas/completadas por corte; todas las filas del panel balanceado deben estar presentes.
- **Totales por tipo de día y corte:** suma de las 36 comunas para laboral, sábado y domingo.
- **Razón laboral/domingo:** cociente de esos dos totales por corte; es un resumen descriptivo sujeto a las limitaciones de comparabilidad entre cortes.
- **Top comunas:** las mismas diez comunas representadas en la figura correspondiente.
- **Tabla de métricas:** el contenido de `metricas_modelo_inicial.csv`, redondeado para lectura.

El notebook documenta el procedimiento y las advertencias en sus celdas Markdown; este diccionario complementa esa explicación para interpretar los archivos una vez exportados.
