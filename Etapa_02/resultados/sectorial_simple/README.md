# Etapa II: pronóstico sectorial sencillo

Esta es la versión principal para la entrega del 28 de octubre de 2026. Usa exclusivamente las tablas de **Subidas por Paradero y Estación**, ya armonizadas en `panel_demanda_bus_modelo.csv`. Las fuentes Etapas, Viajes y geográficas quedan para una fase posterior.

## Alcance

- Oriente: Las Condes, Vitacura, Lo Barnechea, Providencia, La Reina y Ñuñoa.
- Sur: La Cisterna, El Bosque, San Bernardo, La Pintana, San Ramón, San Miguel, La Granja, San Joaquín, Pedro Aguirre Cerda y Lo Espejo.
- Unidad del pronóstico: sector × tipo de día × franja de 30 minutos. Cuatro cortes: nov-2024, abr-2025 v2, nov-2025 y abr-2026.
- Volumen objetivo: suma de `Subidas_Promedio` de las comunas del sector. No es demanda corregida por evasión, personas únicas ni total mensual.
- La agrupación territorial es analítica, no oficial. Los totales no están ajustados por población, paraderos u oferta.

## Pronóstico y ausencias

La **media histórica** promedia únicamente los valores anteriores completos de la misma combinación sector/día/franja. No promedia entre horarios. La referencia **último observado** repite el antecedente completo más reciente, que puede ser anterior al corte inmediatamente previo si este está incompleto.

Las 427 celdas comunales añadidas provisionalmente con cero en los sectores se detectan mediante `relleno_cero`. Si falta una comuna, el agregado sectorial de esa franja queda incompleto y no se usa como antecedente ni objetivo de evaluación. Esto evita entrenar la nueva referencia simple con esos ceros sintéticos. Una franja sin antecedente completo se marca sin historial.

Hay 1.152 filas sectoriales posibles. En abril de 2026 se evalúan **135/144** de oriente: ocho están incompletas y una adicional carece de historial completo. En sur se evalúan **117/144**, con 27 incompletas. Los dos métodos se comparan sobre las mismas filas de cada sector y corte.

## Etiquetas observadas y pronosticadas

Se usa x = suma sectorial / número fijo de comunas (6 o 10). Los terciles positivos de 768 franjas históricas completas de los tres primeros cortes fijan los umbrales finales: q1 = 392,15555555555557 y q2 = 962,5177777777778.

| Etiqueta | Regla |
|---|---|
| Nulo | x = 0 con cobertura completa |
| Bajo | 0 < x ≤ q1 |
| Medio | q1 < x ≤ q2 |
| Alto | x > q2 |

Los umbrales se aplican tanto al valor observado como al pronosticado. No se entrena un clasificador. Son comunes a los sectores y tipos de día, exploratorios y sin interpretación de saturación. **No hay casos sectoriales nulos confirmados**, por lo que no se declara desempeño en esa clase. Una ausencia no se etiqueta como nulo.

Cada evaluación interna recalcula los umbrales únicamente con los cortes anteriores al evaluado. Los umbrales finales no utilizan abril de 2026. Un autocontrol verifica que cambiar objetivos futuros no altera pronósticos ni umbrales.

## Evaluación

El MAE corresponde al volumen **agregado del sector por día y franja**. No se compara con los MAE comunales de los avances anteriores. El WAPE es 100 × suma de errores absolutos / suma observada. La coincidencia de etiquetas es la proporción de clases pronosticadas que coinciden con la clase observada; no equivale a precisión del volumen.

| Sector, abr-2026 | Método | MAE | WAPE | Coincidencia |
|---|---|---:|---:|---:|
| Oriente | Media histórica | 618,23 | 7,78 % | 83,70 % |
| Oriente | Último observado | 781,48 | 9,84 % | 83,70 % |
| Sur | Media histórica | 509,51 | 9,13 % | 88,03 % |
| Sur | Último observado | 509,30 | 9,12 % | 88,89 % |

La media mejora en oriente. En sur ambos métodos dan resultados prácticamente iguales y no se afirma superioridad de la media. En noviembre de 2025 la media tiene menor WAPE en ambos sectores. En abril de 2025 ambos métodos coinciden porque solo hay un corte anterior.

Las matrices de abril revelan errores ocultos por la coincidencia global: en oriente, 16 de 31 franjas medias se pronostican altas. La media detecta 61 de 66 franjas altas de oriente y 12 de 14 del sur.

Abril de 2026 ya se había revisado en el avance anterior. Este nuevo enfoque se evalúa **retrospectivamente** y no constituye una nueva prueba ciega. Solo existen cuatro publicaciones; no se construye una serie diaria continua ni se declara un modelo final.

## Reproducción y archivos

El notebook principal es `Etapa_02/notebooks/etapa_ii_sectorial_simple.ipynb`. No requiere ejecutar los modelos anteriores. Desde la raíz:

```bash
uv run --with pandas --with matplotlib python Etapa_02/codigo/pronostico_sectorial_simple.py
```

El script reutiliza la delimitación y la función de etiquetas de `analisis_sectores.py`, sin ejecutar su análisis anterior. No requiere scikit-learn. `perfil_sectorial.csv` contiene cobertura y perfiles. `predicciones.csv` conserva antecedentes, umbrales y etiquetas. `metricas.csv` y `metricas_por_horario.csv` contienen los errores. `confusion_etiquetas_abril_2026.csv` guarda las matrices completas. `resumen_presentacion.json` alimenta las diapositivas. Los PNG muestran observado y pronosticado en días laborales.

La presentación para enviar es `output/presentaciones/etapa_ii_oriente_sur_entrega.pptx`, con su PDF homónimo. Los notebooks y resultados anteriores se conservan como antecedentes del proyecto.
