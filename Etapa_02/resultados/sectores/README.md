# Comparación de oriente y sur

Actualización de Etapa II según la indicación del profesor: evaluar dos sectores y etiquetar horarios altos, medios, bajos y nulos.

## Delimitación y unidades

La agrupación es analítica, no una zonificación oficial. Oriente incluye Las Condes, Vitacura, Lo Barnechea, Providencia, La Reina y Ñuñoa. Sur incluye La Cisterna, El Bosque, San Bernardo, La Pintana, San Ramón, San Miguel, La Granja, San Joaquín, Pedro Aguirre Cerda y Lo Espejo. Las 16 comunas aparecen en los cuatro cortes del panel común.

- Volumen: suma de `subidas_promedio` de las comunas de cada sector.
- Forma del perfil: participación de cada franja en la suma diaria del sector. Permite comparar zonas de distinta escala, pero no ajusta población, paraderos ni oferta.
- Intensidad para etiquetar: suma sectorial dividida por el número fijo de comunas (6 o 10). No dividir por las comunas observadas cuando faltan datos.
- La medida corresponde a subidas registradas promedio del DTPM. No es un total mensual, personas únicas, ocupación ni demanda corregida por evasión.

## Etiquetas

Los terciles de 768 franjas sectoriales positivas y completas de nov-2024, abr-2025 y nov-2025 fijan dos umbrales comunes: **392,15555555555557** y **962,5177777777778** subidas promedio agregadas por comuna en 30 minutos. Se usa interpolación lineal de pandas. Se mantienen iguales para ambos sectores y para laboral, sábado y domingo, sin recalcular con abril de 2026.

| Etiqueta | Regla sobre x = suma sectorial / número fijo de comunas |
|---|---|
| Nulo | x = 0 y todas las comunas observadas |
| Bajo | 0 < x ≤ 392,15555555555557 |
| Medio | 392,15555555555557 < x ≤ 962,5177777777778 |
| Alto | x > 962,5177777777778 |
| Sin dato completo | Falta al menos una comuna en la franja. Es un estado de calidad, no un nivel de demanda. |

No hay franjas sectoriales nulas confirmadas en esta delimitación y estos cuatro cortes. No se fuerza su existencia. La clasificación es descriptiva y exploratoria; los umbrales no son oficiales ni indican saturación. Las etiquetas se calculan sobre demanda observada, no se ha entrenado ni evaluado un clasificador.

## Pronóstico y evaluación

Se reutiliza el modelo inicial, entrenado con las **36 comunas**. Esta actualización desagrega sus predicciones en dos sectores; no entrena modelos separados ni cambia hiperparámetros. El MAE se calcula por celda comunal antes de agregar, evitando cancelar errores de comunas distintas. El WAPE divide la suma de errores absolutos por la suma observada.

Las tablas principales de la presentación usan **solo objetivos observados**: 856 celdas en oriente y 1.335 en sur para abril de 2026. Los antecedentes y el entrenamiento conservan el supuesto provisional de ceros del avance original. `metricas_por_sector.csv` también incluye la evaluación del panel provisional completo para comprobar sensibilidad. Las métricas por nivel heredan la etiqueta del sector/día/franja y evalúan las celdas comunales observadas. Las celdas observadas de franjas sectoriales incompletas aparecen en una fila separada de cobertura.

Abril de 2026 ya había sido revisado en la presentación original. El contraste nuevo es un análisis posterior del mismo test, no una validación ciega adicional. En noviembre de 2025 la media histórica supera al ML en ambos sectores y en abril de 2026 ocurre lo contrario.

## Resultados que sostienen la conclusión

- En abril de 2026 el máximo laboral del sur está en 07:00–07:30, y el de oriente en 18:00–18:30.
- Entre 06:00 y 09:00 el sur concentra 28,9 % de sus subidas laborales y oriente 21,7 %. Entre 16:00 y 20:00 oriente concentra 32,4 % y el sur 27,6 %. Los límites superiores son exclusivos. Los denominadores incluyen las sumas disponibles en franjas parciales.
- El máximo del sur se mantiene a las 07:00 en los cuatro cortes. Oriente tiene su máximo a las 18:00 en tres cortes y a las 08:00 en noviembre de 2025.
- La similitud de la forma convive con diferencias en concentración y nivel. La correlación laboral de abril es 0,87 sobre franjas completas en ambos sectores, un indicador descriptivo sin prueba de igualdad.
- Los datos orientan una revisión de oferta en la mañana del sur y la tarde de oriente. Se requieren capacidad, frecuencias y ocupación antes de recomendar cambios de servicio.

## Archivos y reproducción

`comunas_sectores.csv` define la agrupación. `perfil_y_etiquetas.csv` tiene las 1.152 combinaciones sector/corte/día/franja. `conteo_etiquetas_abril_2026.csv` comprueba las 48 franjas por sector y tipo de día. Las dos tablas de métricas muestran el error por sector y por nivel. `resumen_presentacion.json` alimenta las diapositivas editables y conserva valores sin redondear. Los PNG muestran volumen y forma del perfil laboral.

Desde la raíz, con las dependencias del análisis original:

```bash
python Etapa_02/codigo/etapa_ii_analysis.py
python Etapa_02/codigo/analisis_sectores.py
```

El notebook `Etapa_02/notebooks/etapa_ii_avance.ipynb` incluye el bloque nuevo después de la evaluación original. El segundo script requiere las predicciones exportadas por el primero. Incluye autocontroles de delimitación, cobertura, umbrales, fronteras de etiquetas y sumas diarias.
