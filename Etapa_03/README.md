# Etapa III — Evaluación, selección e interpretación

El [plan de trabajo](plan_de_trabajo.md) organiza la entrega en tres hitos. Se implementó la base técnica del **Hito 1**: auditoría del panel incluido, reproducción de las referencias de etapa 2 y controles de validación temporal. La selección y la evaluación ampliada siguen pendientes.

## Estado y datos para el equipo

El [plan actualizado](plan_de_trabajo.md#estado-del-avance-para-revisión-del-equipo) distingue tareas realizadas (`[x]`) y pendientes (`[ ]`). La base activa sigue teniendo cuatro cortes; los datos nuevos están seleccionados, pero todavía no integrados ni usados para elegir un método.

El paquete local `Datos/Datos_equipo_etapa_03.zip` permite compartir las fuentes actuales, los paneles y los candidatos de ampliación sin subir los binarios a Git. Véanse [el contenido y las instrucciones de extracción](compartir_datos.md) y [el inventario de Etapas](../Datos/Fuentes/Etapas/README.md).

## Objetivo compartido

Pronosticar la **suma de subidas registradas** de oriente y sur por tipo de día y franja de 30 minutos. Comparar media histórica y último observado, usando solo antecedentes completos publicados antes del corte evaluado. Las etiquetas se calculan con terciles positivos históricos del promedio por comuna; no se entrena un clasificador ni se interpreta esa normalización como ajuste por población.

Esto reemplaza el objetivo inicial de estimar pasajeros reales corregidos por evasión. Cuatro publicaciones no son una serie diaria continua. Abril de 2026 ya fue observado: la evaluación es retrospectiva y no una prueba ciega ni evidencia suficiente para decisiones de flota o frecuencia.

## Ejecutar el Hito 1

Desde la raíz del repositorio, con `uv` y Python 3.14 (entorno utilizado):

```bash
MPLBACKEND=Agg uv run --python 3.14 --with-requirements Etapa_03/requirements.txt \
  python Etapa_03/codigo/base_reproducible.py

MPLBACKEND=Agg uv run --python 3.14 --with-requirements Etapa_03/requirements.txt \
  python -m unittest discover -s Etapa_03/codigo -p 'test_*.py' -v
```

Alternativa: instalar `Etapa_03/requirements.txt` en un entorno virtual y ejecutar los mismos comandos Python. `matplotlib` es necesario por los imports del código reutilizado; esta fase no genera gráficos.

No se requieren los libros originales ni ejecutar scripts de análisis anteriores. Se importan únicamente funciones y constantes de etapa 2, cuyos análisis están protegidos por `main`. No se modifican archivos de esa etapa. La ejecución reescribe exclusivamente las salidas del Hito 1 después de superar los controles.

## Datos y auditoría

Entradas de `Etapa_02/resultados/`:

- `panel_demanda_bus_modelo.csv`: rejilla de 36 comunas × cuatro cortes × tres tipos de día × 48 franjas, con `relleno_cero`.
- `panel_demanda_bus.csv`: combinaciones observadas, utilizado para contrastar valores y marcas de ausencia.
- `panel_quality_report.json`: antecedente de construcción; se registra su SHA-256, pero no se repite su auditoría de los libros originales.

Se verificaron claves únicas, rejilla exacta, valores finitos y no negativos y marcas binarias. Cada cero añadido debe corresponder a una clave ausente del panel observado; cada celda presente debe conservar su valor. En los dos sectores hay **9.216 celdas comunales**, **427 ceros añadidos** y **83 ceros comunales observados**. No hay agregados sectoriales nulos confirmados: el desempeño de esa categoría es **no evaluable**.

La delimitación se conserva: seis comunas de oriente y diez del sur, detalladas en [la metodología anterior](../Etapa_02/resultados/sectorial_simple/README.md). La procedencia usa las tablas de Subidas de noviembre de 2024, abril de 2025 **v2**, noviembre de 2025 y abril de 2026. Se mantienen el filtro BUS, normalización de nombres y horarios, exclusión de `SIN_COMUNA` y selección de comunas comunes del panel anterior. Véanse [las fuentes](../Datos/Fuentes/README.md) y [el constructor del panel](../Etapa_02/codigo/build_panel.py).

**Límite:** esta auditoría contrasta los paneles incluidos entre sí. No relee los libros originales ni confirma la semántica de omisión del DTPM.

## Resultados reproducidos

Se reprodujeron las 1.728 filas de predicciones, las 12 filas de métricas y la matriz de abril de 2026 de la media histórica. Coinciden con los CSV de etapa 2 con `rtol=1e-9` y `atol=1e-8`; los conteos son exactos.

| Abril de 2026 | Método | MAE | WAPE | Coincidencia de etiquetas |
|---|---|---:|---:|---:|
| Oriente | Media histórica | 618,23 | 7,78 % | 83,70 % |
| Oriente | Último observado | 781,48 | 9,84 % | 83,70 % |
| Sur | Media histórica | 509,51 | 9,13 % | 88,03 % |
| Sur | Último observado | 509,30 | 9,12 % | 88,89 % |

Ambos métodos usan exactamente las mismas claves evaluables. Abril de 2025 empata porque solo dispone de un corte anterior; no es evidencia de equivalencia con más historial. No se selecciona todavía un método.

### Cobertura de la evaluación

| Corte | Sector | Evaluadas / 144 | % evaluado | Incompletas | Sin historial completo |
|---|---|---:|---:|---:|---:|
| 2025-04 | Oriente | 131 | 90,97 % | 10 | 3 |
| 2025-04 | Sur | 119 | 82,64 % | 23 | 2 |
| 2025-11 | Oriente | 134 | 93,06 % | 7 | 3 |
| 2025-11 | Sur | 119 | 82,64 % | 24 | 1 |
| 2026-04 | Oriente | 135 | 93,75 % | 8 | 1 |
| 2026-04 | Sur | 117 | 81,25 % | 27 | 0 |

Las exclusiones son disjuntas: primero se cuentan objetivos incompletos; «sin historial» cuenta únicamente objetivos completos sin antecedente completo. Sus porcentajes suman 100 % junto con el evaluado. `predicciones.csv` conserva `n_antecedentes` también para objetivos incompletos, permitiendo revisar solapamientos. La cobertura se publica además por tipo de día, sin duplicar conteos por método.

## Archivos generados

En [`resultados/hito_1/`](resultados/hito_1/):

| Archivo | Contenido |
|---|---|
| `auditoria_panel.json` | Conteos, delimitación, versiones de ejecución y SHA-256 de las entradas. |
| `perfil_sectorial.csv` | Las 1.152 franjas sectoriales de los cuatro cortes, con cobertura y ausencias. |
| `predicciones.csv` | Ambos métodos, observados, etiquetas, antecedentes y umbrales por corte. |
| `metricas.csv` | MAE, WAPE, coincidencia y detección de altos por sector/corte/método. |
| `cobertura.csv` | Conteos y porcentajes por sector/corte. |
| `cobertura_por_tipo_dia.csv` | El mismo desglose por tipo de día. |
| `confusion_etiquetas_abril_2026.csv` | Matriz reproducida de la media histórica. |

Para el frente C, `perfil_sectorial.csv` deja **vacíos** el volumen y promedio por comuna de las franjas incompletas: deben graficarse como interrupciones. Las participaciones diarias quedan vacías para todo sector/tipo de día/corte con alguna franja incompleta o total cero. No son idénticas a las del perfil anterior; esta diferencia es deliberada y no cambia los pronósticos ni las métricas.

Las etiquetas del perfil usan los umbrales anteriores a abril de 2026, solo para comparación descriptiva. Para evaluar cada corte, usar las etiquetas y los umbrales de `predicciones.csv`, recalculados con su historial correspondiente.

## Verificaciones realizadas y pendientes

- Reproducción de predicciones, métricas y matriz; matriz contrastada con conteos, detección de altos y coincidencia.
- Alteración de valores y cobertura del corte objetivo y posteriores para cada evaluación: no cambia pronósticos ni umbrales.
- Cinco pruebas: límites de etiquetas, historial incompleto/ausente, WAPE con denominador cero, cobertura sin doble conteo y perfiles con ausencias. Un WAPE sin volumen observado queda vacío y se interpreta como **no evaluable**.

Pendiente del Hito 2: error firmado medio (predicción menos observado), métricas por tipo de día, subestimación de franjas altas, matrices ampliadas y selección por WAPE conjunto de noviembre de 2025 y abril de 2026. Pendiente del Hito 3: notebook completo, gráficos y presentación integrados, revisión contra la rúbrica y ensayo. Los responsables y la validación del relato por el equipo siguen por asignar; no se da por cerrada la entrega completa del Hito 1.

## Hito 2 y 3: comparación de modelos, robustez y entrega

Reproducir desde la raíz del repositorio:

```bash
python -m venv .venv
.venv/Scripts/pip install -r Etapa_03/requirements.txt pytest jupyter
.venv/Scripts/python -m pytest Etapa_03/codigo
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace Etapa_03/notebooks/etapa_iii_final.ipynb
```

| Script | Salida | Contenido |
|---|---|---|
| `codigo/comparacion_modelos.py` | `resultados/hito_2/` | 4 métodos (media histórica, último observado, Ridge y Gradient Boosting) con validación de origen móvil (pruebas en 2025-11 y 2026-04) |
| `codigo/validacion_robustez.py` | `resultados/hito_2b/` | Bootstrap IC 95 %, RMSE, ajuste de hiperparámetros sin fuga, importancia por permutación, residuos y sensibilidad de umbrales |
| `codigo/ampliacion_2023.py` | `resultados/hito_2c/` | Historial ampliado con las Subidas laborales de 2023 (abr, ago, nov). Compara historial original y ampliado sobre las mismas franjas laborales, con bootstrap |
| `codigo/figuras_hito_3.py` | `resultados/figuras/` | Figuras de la presentación |

**Modelo seleccionado, por segmento:**
- **Laboral:** Gradient Boosting con historial 2023–2026. WAPE 3,2 %, significativamente mejor que la media histórica (−1,6 pp, IC 95 % [−2,1; −1,2]).
- **Sábado y domingo:** media histórica, porque no hay datos de 2023 para esos días. En la evaluación de 2024–2026 empata estadísticamente con Ridge (WAPE conjunto 6,95 %) y es la más simple.

`ampliacion_2023.py` lee los ZIP de `Datos/Fuentes/Subidas/` (ignorados por git; ver `compartir_datos.md`) y requiere `pyxlsb`.

Presentación: `presentacion/deck/` (fuente de las láminas) y `presentacion/preguntas_y_respuestas.md`.
