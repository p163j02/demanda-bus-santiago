# Etapa II: cambios de enfoque y lectura de las curvas

## Qué cambió y por qué

El profesor solicitó comparar dos sectores y etiquetar los horarios como **alto, medio, bajo o nulo**. Por eso acotamos el análisis regional a **oriente y sur**, buscando diferencias y similitudes que podamos explicar y evaluar.

- **Datos:** usamos únicamente las tablas de Subidas. Etapas, Viajes y otras fuentes quedan para una fase posterior.
- **Unidad de análisis:** sector × tipo de día (laboral, sábado o domingo) × franja de 30 minutos. Oriente reúne seis comunas y sur diez; esta agrupación es analítica.
- **Pronóstico actual:** calculamos la media de los valores históricos completos de la misma combinación sector/día/franja. La comparamos con repetir el último valor completo observado.
- **Etiquetas:** dividimos la suma sectorial por su número de comunas y aplicamos umbrales históricos comunes para asignar el nivel. Esto no ajusta por población. No entrenamos un clasificador separado.
- **HistGradientBoosting:** permanece explicado como antecedente del modelo comunal anterior. No lo hemos reentrenado como modelo sectorial en esta entrega.

## Limpieza y aclaración sobre los ceros

Mantenemos el filtro de buses, la normalización de nombres y horarios y la selección de comunas comparables. Lo que cambia es el uso de las ausencias:

- Conservamos los **ceros publicados** en la fuente.
- Una fila ausente **no demuestra que hubo cero subidas**. El panel anterior conserva ceros añadidos, identificados con `relleno_cero`, para poder auditarlos.
- Si falta una comuna, excluimos ese agregado sectorial del historial utilizado para pronosticar y de los objetivos de evaluación. No usamos esos ceros añadidos como observaciones del modelo actual.
- **Nulo** requiere un cero observado con cobertura completa. En estos datos no hay casos sectoriales nulos confirmados; no se fuerza esa categoría ni se afirma desempeño en ella.

Esta aclaración aparece en la **diapositiva 5** de `etapa_ii_oriente_sur_entrega.pdf` y su PowerPoint.

## Qué significa el gráfico de dos puntas

Podríamos conseguir una curva más sencilla de analizar, aunque las dos puntas podrían seguir apareciendo porque son compatibles con actividad de mañana y tarde. Su forma, por sí sola, no es un error del conjunto de datos ni demuestra que el modelo sea inadecuado.

Interpretamos la recomendación del profesor como una invitación a separar patrones mezclados en el total regional. Las posibilidades son:

| Alternativa | Qué aporta | Estado actual |
|---|---|---|
| Separar por sector | Permite distinguir la concentración territorial de las subidas. En abril de 2026 laboral, sur alcanza su máximo a las 07:00 y oriente a las 18:00. | Aplicado. |
| Separar tipos de día | Permite comparar laborales, sábados y domingos, sin mezclar sus perfiles. | Aplicado; no implica que desaparezcan las dos puntas. |
| Agrupar por hora | Puede facilitar la lectura y reducir variaciones pequeñas, pero pierde detalle. | Propuesta futura; mantenemos intervalos de 30 minutos. |
| Mostrar observado frente a pronosticado | Permite ver cuánto anticipa el método y dónde falla, especialmente en las puntas. | Disponible en los gráficos de resultados del modelo sectorial. |

Como comparación visual adicional, podríamos mostrar el gráfico regional original junto a los perfiles sectoriales y sus pronósticos. Esta es una propuesta, no un cambio adicional realizado en la presentación. El avance sería explicar cómo se distribuyen las puntas territorialmente y qué tan bien podemos anticiparlas.

**Una curva más lisa, por sí sola, no demuestra una mejora: debemos respaldarla con interpretación y error de pronóstico.**

## Resultados y alcance

En abril de 2026, la media histórica obtiene un WAPE de **7,78 % en oriente** y **9,13 % en sur**. Mejora respecto al último observado en oriente; en sur ambos métodos prácticamente empatan. La coincidencia de etiquetas es **83,7 % y 88,0 %**, respectivamente: no equivale a precisión del volumen.

Estamos en una **fase preliminar o alfa**, con cuatro cortes de publicación y evaluación retrospectiva. Los resultados describen subidas registradas; todavía no justifican por sí solos cambios de frecuencia, para los que harían falta datos de oferta, capacidad y ocupación.
