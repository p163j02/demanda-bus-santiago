# De dónde salen los datos y qué significa cada CSV

Una explicación paso a paso y sin asumir que ya conoces los archivos. Piensa en las fuentes como ingredientes distintos: **no todos miden lo mismo**, así que no se mezclan en una sola tabla.

## La historia en una línea

```text
Libros originales de Subidas (Excel)
        ↓ filtrar solo BUS, ordenar nombres y horas
panel_demanda_bus.csv
        ↓ conservar 36 comunas comunes y completar combinaciones ausentes con cero provisional
panel_demanda_bus_modelo.csv
        ↓ analizar y evaluar predicciones
metricas_modelo_inicial.csv + gráficos
```

Las tablas de **Etapas** y **Viajes** son ingredientes complementarios, pero **no pasan por esa receta ni alimentan el modelo de Etapa II**: describen unidades distintas y se conservan aparte.

## 1. ¿De dónde vienen los datos principales?

La fuente principal del modelo son los libros originales de **Subidas por Paradero y Estación**, guardados sin modificar en `Datos/Fuentes/Subidas/`. El código selecciona cuatro cortes:

| Corte usado | Archivo original |
|---|---|
| Noviembre de 2024 | `Subida_Paradero_Estacion_2024.11.xlsb` |
| Abril de 2025 | `Subida_Paradero_Estacion_2025_04_v2.xlsb` |
| Noviembre de 2025 | `Subidas_Paradero_Estacion_2025.11.xlsx` |
| Abril de 2026 | `Subidas_Paradero_Estacion_2026.04_v3(1).xlsx` |

También está `Subida_Paradero_Estacion_2025.04.xlsb`, otra versión de abril de 2025 que **no utiliza el proceso actual**; se eligió la versión `_v2`. No hay un corte válido de abril de 2024: los cortes disponibles son esos cuatro.

### ¿Qué significa “Subidas” aquí?

Son datos publicados como `Subidas_Promedio`, organizados originalmente por paradero/estación y otras características del servicio. Para este análisis se toma ese valor, se filtran las filas cuyo modo es `BUS` y se suman las subidas dentro de cada grupo de:

- corte;
- comuna;
- tipo de día (`LABORAL`, `SABADO` o `DOMINGO`);
- franja de 30 minutos.

En simple: agrupamos las observaciones de bus para responder “¿cuántas subidas promedio registra esta comuna en este tipo de día y franja, en este corte?”. No es el total de pasajeros corregido por evasión. El proyecto usa la medida `Subidas_Promedio` tal como viene en la fuente.

**Importante:** cada corte representa una semana/muestra publicada; no tenemos una medición diaria continua desde 2024 hasta 2026. Por eso estos cuatro cortes sirven para una comparación temporal preliminar, no para afirmar que tenemos una serie diaria larga.

## 2. ¿Qué son Etapas y Viajes? ¿Por qué no se mezclan?

### Tabla de Etapas

La extracción explorada está en `Datos/Fuentes/Etapas/2026-04/Etapas-2026-04/Tabla de Etapas/`: hay archivos diarios del 11 al 17 de abril de 2026, principalmente como `*.etapas.csv.gz`, y una versión descomprimida grande de `2026-04-11.etapas.csv`. Además, hay ZIP por corte en `Datos/Fuentes/Etapas/` para abril y noviembre de 2024, abril y noviembre de 2025 y abril de 2026.

Una **etapa** es un tramo de un viaje: por ejemplo, una parte del recorrido hecha en bus o metro, con datos de subida y, a veces, de bajada. El archivo trae variables como modo de transporte, horas, comuna/paradero de subida y bajada y factores de expansión. Sus CSV usan `|` como separador; `.gz` solo significa que el archivo está comprimido.

Puede servir para análisis complementarios de esos cortes, pero no reemplaza directamente el histórico de Subidas: cada fila representa una etapa, no una subida agregada. Los nuevos ZIP de 2024 y 2025 aún no se han procesado para un análisis comparativo. El factor de expansión de Etapas no se incorpora al target del modelo de Subidas.

### Tabla de Viajes

La extracción explorada está en `Datos/Fuentes/Viajes/2026-04/Viajes_2026-04/Tabla de Viajes/`, con un archivo `*.viajes.csv.gz` por día del 11 al 17 de abril de 2026. También hay ZIP por período para abril y noviembre de 2024, abril y noviembre de 2025 y abril de 2026.

Un **viaje** representa el recorrido completo de una persona, que puede contener varias etapas. Sus columnas incluyen duración/distancia, cantidad de etapas, modos y propósito del viaje, entre otras. También usa `|` como separador y está comprimida en formato `.gz`.

En una frase: **Viaje = recorrido completo; Etapa = un tramo del recorrido; Subidas = medida de subidas que usamos como objetivo histórico.** No se deben sumar o concatenar estas tablas como si cada fila significara lo mismo.

Los archivos `.zip` de Etapas y Viajes son contenedores de las descargas originales; no son otra medición. Los paquetes por corte permiten plantear comparaciones temporales complementarias, pero aún no se han reprocesado ni validado metodológicamente.

## 3. ¿Qué es cada archivo generado?

Todos los resultados de Etapa II están en `Etapa_02/resultados/`.

### `panel_demanda_bus.csv` — lo observado y agrupado

Es la primera tabla que crea `build_panel.py` a partir de los cuatro libros de Subidas.

- Una fila representa un corte + comuna + tipo de día + franja de 30 minutos.
- Solo contiene combinaciones que aparecían en la fuente; **no inventa filas faltantes**.
- Conserva las comunas reportadas en cada corte, incluida `SIN_COMUNA`.
- Tiene 20.051 filas en la versión actual.

Columnas:

| Columna | En palabras simples |
|---|---|
| `periodo` | El corte, como `2025-11`. |
| `comuna` | Comuna normalizada; `SIN_COMUNA` significa que no se pudo asignar una comuna. |
| `tipo_dia` | Laboral, sábado o domingo. |
| `media_hora` | Inicio de una franja de 30 minutos, por ejemplo `08:00`. |
| `subidas_promedio` | Suma de la medida `Subidas_Promedio` para ese grupo. |

### `panel_demanda_bus_modelo.csv` — la tabla preparada para modelar

Parte de los mismos datos, pero el modelo necesita una cuadrícula regular: que estén todas las combinaciones esperadas en todos los cortes. Por eso:

- se limita a las **36 comunas presentes en los cuatro cortes**;
- excluye `SIN_COMUNA`;
- incluye los 3 tipos de día, 48 franjas de media hora y 4 cortes;
- contiene 36 × 3 × 48 × 4 = **20.736 filas**.

Tiene las cinco columnas del panel observado y una adicional:

- `relleno_cero = 0`: había una fila para esa combinación en la fuente;
- `relleno_cero = 1`: no había fila y el proceso la completó con `subidas_promedio = 0`.

Ese cero es **provisional**. Es como ver que no llegó un formulario: no sabemos todavía si significa “cero subidas” o “faltó información/cobertura”. Hay 1.087 combinaciones completadas a cero en total; hay que interpretar las métricas teniendo presente esa advertencia.

### `metricas_modelo_inicial.csv` — qué tan lejos quedaron las predicciones

La crea el análisis del notebook. Cada fila compara un modelo con los valores observados en un corte futuro.

| Columna | Significado sencillo |
|---|---|
| `corte_prueba` | Corte futuro contra el que se probó. |
| `entrenamiento` | Cortes anteriores utilizados para aprender o calcular la referencia. |
| `modelo` | Predicción del último corte, media histórica o HistGradientBoosting. |
| `MAE` | Error absoluto promedio, en unidades de subidas promedio; menor es mejor. |
| `RMSE` | Error que penaliza más los errores grandes; menor es mejor. |
| `WAPE_pct` | Error absoluto total dividido por el total observado, expresado en porcentaje; menor es mejor. |
| `MAPE_positivos_pct` | Error porcentual promedio solo donde el valor observado es positivo; se excluyen ceros para evitar dividir por cero. |

Ejemplo de lectura: si el MAE es 70, en promedio la predicción se desvía unas 70 unidades de `Subidas_Promedio` por fila evaluada. No significa que se equivoque 70 pasajeros reales: el target es la medida de la fuente y está agregada por comuna/día/franja. Los valores se consideran preliminares porque solo hay cuatro cortes y los ceros añadidos siguen pendientes de validación.

### `panel_quality_report.json` — revisión de cómo se armó la tabla

No es un CSV, sino un informe legible por máquina. Para cada corte registra qué libro y hoja se leyeron, cuántas filas entraron, cuántas eran de bus, qué comunas y tipos de día aparecieron y cuántas combinaciones se completaron con cero. Sirve para auditar el proceso, no es un resultado de demanda ni una tabla para entrenar el modelo.

### Gráficos en `figuras/`

- `subidas_por_corte_y_dia.png`: compara la suma de subidas por corte y tipo de día.
- `perfil_horario_laboral.png`: compara el perfil de las 48 franjas de día laboral entre cortes.
- `top_comunas_2026_laboral.png`: muestra las diez comunas con mayor suma laboral en abril de 2026, dentro de las 36 comunas comunes.

Son visualizaciones descriptivas: muestran patrones, pero por sí solas no explican sus causas.

## 4. El recorrido completo, con una analogía

Imagina que tienes cuatro planillas de distintas fechas con los registros de subidas de muchos lugares y modos:

1. **Elegimos cuatro planillas de Subidas** y descartamos Metro/otros modos para quedarnos con buses.
2. **Arreglamos formatos**: nombres de comunas, días y horas para que se puedan comparar.
3. **Agrupamos** las subidas por comuna, tipo de día y franja de media hora. Eso produce `panel_demanda_bus.csv`.
4. **Preparamos una cuadrícula pareja** con las 36 comunas comunes y marcamos las celdas sin fila. Para probar el modelo se les pone cero provisional y se añade `relleno_cero`; eso produce `panel_demanda_bus_modelo.csv`.
5. **Probamos predicciones** y comparamos sus errores. Eso produce `metricas_modelo_inicial.csv`.
6. **Revisamos la calidad y mostramos patrones** con el JSON y los gráficos.

Etapas y Viajes contienen registros de tramos y recorridos completos. Ahora hay paquetes para cinco cortes entre abril de 2024 y abril de 2026; pueden responder preguntas complementarias, pero no son la misma “receta” ni se combinan con los cuatro cortes de Subidas.

## 5. ¿Qué archivos necesito para ejecutar el notebook?

Para ejecutar solo el análisis de Etapa II en Colab, basta con el notebook `Etapa_02/notebooks/etapa_ii_avance.ipynb` y `panel_demanda_bus_modelo.csv`. Los Excel originales, Etapas y Viajes **no hacen falta** si el panel ya está generado.

Para reconstruir los paneles desde el origen, se necesitan el script `Etapa_02/codigo/build_panel.py` y los cuatro Excel de Subidas usados que aparecen en la tabla inicial. Los archivos originales se conservan intactos.

## 6. Entonces, ¿faltan datos de origen?

**Sí, hay huecos respecto de una historia completa y también combinaciones ausentes dentro de los archivos; pero son dos cosas distintas.**

1. **El enlace de Subidas de abril de 2024 en el portal sigue entregando un archivo repetido.** Descarga el mismo libro v2 de abril de 2025; la ficha confirma que la vigencia es abril de 2025. No es una descarga que se nos haya pasado: el enlace publicado por DTPM no proporciona un libro válido de Subidas de abril de 2024. Por eso usamos los cuatro cortes válidos disponibles (nov-2024, abr-2025, nov-2025 y abr-2026) y no inventamos un quinto corte.
2. **No tenemos una serie continua.** Los cuatro cortes de Subidas son semanas/muestras separadas; no hay un archivo de cada día o cada mes desde 2024. Los ZIP de Etapas y Viajes para cinco cortes de 2024–2026 ya están organizados en `Datos/Fuentes/Etapas/` y `Datos/Fuentes/Viajes/`. Son fuentes complementarias y no sustituyen automáticamente los cortes de Subidas que faltan.
3. **Hay combinaciones sin fila en los libros de Subidas.** En la rejilla de modelamiento se completaron 1.087 combinaciones comuna/día/franja con cero provisional (247 en nov-2024, 291 en abr-2025, 268 en nov-2025 y 281 en abr-2026). No se sabe todavía si cada ausencia quiere decir demanda cero o que esa combinación no se cubrió/exportó. Por eso `relleno_cero` identifica esas filas y no deben presentarse como ceros observados.
4. **La cobertura de comunas cambia.** Nov-2024 contiene 36 comunas; abr y nov-2025, 36 más `SIN_COMUNA`; abr-2026, 39 más `SIN_COMUNA`. El modelo usa solo la intersección de 36 comunas para comparar la misma geografía en todos los cortes. Otras comunas reportadas en 2026 (como Buin, Colina y Pirque) quedan fuera del panel de modelamiento, no porque no existan en el original, sino porque no están en los cuatro cortes.
5. **No se ha descargado todo el archivo histórico del portal.** La carpeta canónica `Datos/Fuentes/` contiene las fuentes de 2024–2026 que se consideran útiles para este proyecto, pero la página DTPM lista también paquetes anteriores a 2024 y archivos agregados de “Subidas y Bajadas” que no se conservaron. Podrían servir para otros análisis; antes de considerarlos hay que comprobar su definición, granularidad y formato. El [informe de cotejo y consolidación](revision_descargas_dtpm_hoy.md) detalla el inventario.
6. **Hay una diferencia potencial de medición:** la ficha de abril de 2026 menciona “bip! u otro medio de pago”, mientras las fichas anteriores mencionan bip!. Esto no prueba que los datos sean incompatibles, pero sí que la comparación debe tratarse como preliminar hasta aclararlo con DTPM.

En resumen: **sí faltan períodos y hay combinaciones ausentes, pero no se puede concluir que falten viajes** solo mirando una fila ausente. El reporte actual no encontró errores de parseo en campos obligatorios para las filas procesadas; eso no demuestra que la cobertura de origen sea completa. El pendiente principal es preguntar al DTPM qué significa que no venga una combinación comuna/día/franja.

## Dónde consultar más detalle

- [Índice del proyecto](../README.md)
- [Fuentes originales y su organización](../Datos/Fuentes/README.md)
- [Diccionario de columnas y salidas](../Etapa_02/resultados/DICCIONARIO_SALIDAS.md)
- [Bitácora con decisiones y limitaciones](bitacora_datos_proyecto.md)
- [Cotejo de la descarga reciente con las fuentes anteriores](revision_descargas_dtpm_hoy.md)
