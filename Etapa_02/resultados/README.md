# Panel y resultados preliminares — Etapa II

## Definición del target

El panel modela `Subidas_Promedio` de los libros **Subidas por Paradero y Estación**. Son subidas observadas/procesadas por el DTPM, no una estimación de todos los pasajeros, y las fichas señalan que no consideran evasión. No se usa `fExpansionServicioPeriodoTS` para el entrenamiento porque solo hay Tabla de Etapas detallada para abril de 2026, no cuatro cortes históricos equivalentes.

## Archivos

- `panel_demanda_bus.csv`: agregación observada por corte, comuna, tipo de día y franja. Mantiene comunas reportadas en cada fuente, incluida `SIN_COMUNA`; no agrega combinaciones ausentes.
- `panel_demanda_bus_modelo.csv`: rejilla completa de las **36 comunas presentes en los cuatro cortes** × 3 tipos de día × 48 franjas × 4 cortes (20.736 filas). Excluye `SIN_COMUNA` y comunas que no aparecen en todos los cortes. `relleno_cero=1` marca combinaciones sin fila en la fuente que se han tratado provisionalmente como cero.
- `panel_quality_report.json`: filas procesadas, cobertura por fuente, comunas y ceros agregados.
- `metricas_modelo_inicial.csv`: resultados de los baselines y del primer HistGradientBoosting bajo evaluación temporal.
- `figuras/`: gráficos generados por el análisis.

Para interpretar columnas, métricas, gráficos y salidas impresas, consulta el [diccionario de salidas](DICCIONARIO_SALIDAS.md).

## Reproducibilidad

Desde la raíz del repositorio:

```bash
uv run --with openpyxl --with pyxlsb python Etapa_02/codigo/build_panel.py
uv run --with pandas --with scikit-learn --with matplotlib python Etapa_02/codigo/etapa_ii_analysis.py
```

Para convertir los dos archivos históricos `.xlsb`, `build_panel.py` requiere LibreOffice (`libreoffice` o `soffice`). Los archivos originales no se modifican. El notebook anotado está en `Etapa_02/notebooks/etapa_ii_avance.ipynb` y el código percent-format equivalente en `Etapa_02/codigo/etapa_ii_analysis.py`.

## Advertencias que deben acompañar los resultados

1. La ficha de abril de 2026 menciona transacciones bip! **u otro medio de pago**; las fichas anteriores mencionan bip!. Puede haber un cambio de medición entre cortes.
2. La cobertura comunal aumentó: las fuentes tienen 36 comunas en nov-2024, 36 más `SIN_COMUNA` en abr/nov-2025, y 39 más `SIN_COMUNA` en abr-2026. Para la prueba temporal se usa la intersección de 36 comunas.
3. En nov-2024 hay filas de paradero con cero subidas explícitas; en los otros tres archivos no aparecen filas con valor cero. Se completan con cero solo las combinaciones comuna/día/franja ausentes dentro de las 36 comunas comunes. Es una hipótesis de trabajo que debe validarse con la semántica de exportación del DTPM; por eso se conserva la marca `relleno_cero`.
4. Los ratios laboral/domingo de la tabla de Subidas no son ≥3 en todos los cortes (aprox. 2,27; 3,28; 2,87; 3,23). No afirmar que la razón supera 3 en todos los períodos. La Tabla de Etapas de abril de 2026 es una fuente distinta y su patrón debe reportarse aparte.
5. La validación de abril de 2026 es temporal, pero solo existen tres cortes previos. En la validación interna de nov-2025, el primer modelo ML no superó la media histórica; su resultado en abr-2026 es preliminar, no evidencia suficiente para declararlo modelo final.
