# Guion de presentación — Etapa II

**Proyecto:** Predicción de subidas de buses por comuna y franja horaria en Santiago  
**Duración sugerida:** 8–10 minutos + preguntas  
**Nota de alcance:** presentar el modelo como pronóstico de subidas registradas, no como estimación total de pasajeros evasores.

## 1. Problema y objetivo

- **Problema:** la demanda de buses cambia según comuna, hora y tipo de día; sin una estimación anticipada cuesta planificar frecuencias y flota.
- **Objetivo:** pronosticar subidas registradas por comuna y franja de 30 minutos para apoyar la planificación operativa.
- Aclarar que este avance usa la medida observada de las tablas históricas de Subidas; la estimación de pasajeros reales con factor de expansión queda fuera del target del primer modelo.
- **Visual:** mapa esquemático de Santiago + ejemplo de perfil horario.

## 2. Contexto y motivación

- Stakeholder de referencia: planificación del DTPM / Red Movilidad.
- Valor esperado: anticipar períodos y comunas de alta actividad, apoyar la planificación de frecuencias y evitar asignaciones basadas solo en promedios generales.
- No afirmar todavía impacto operacional medido: el proyecto pronostica demanda y no optimiza directamente rutas o frecuencias.

## 3. Datos disponibles y decisión sobre el target

- Cuatro cortes de las tablas “Subidas por Paradero y Estación”: nov-2024, abr-2025, nov-2025 y abr-2026.
- Se filtra BUS y se agrega `Subidas_Promedio` desde paradero a comuna × tipo de día × franja de 30 minutos.
- Se usa esta fuente para entrenar y evaluar porque es la única con cortes históricos suficientes.
- La ficha indica que no considera evasión; la ficha abr-2026 menciona bip! u otros medios de pago, potencial cambio respecto de cortes anteriores.
- **Visual:** diagrama “Excel por paradero → filtro BUS → normalización → agregación comunal → panel”.

## 4. Preparación y controles de calidad

- Normalización de formatos distintos entre libros: nombres de campos, `Bus/BUS`, tiempos Excel y nombres de comuna con problemas de codificación en nov-2024.
- Se conservan las cuatro fuentes originales sin modificarlas.
- Intersección temporal: 36 comunas presentes en los cuatro cortes; se excluye `SIN_COMUNA` del pronóstico y se evita comparar áreas no cubiertas en todos los períodos.
- Panel observado: 20.051 combinaciones. Panel de modelamiento: 20.736 filas (36 × 3 × 48 × 4).
- Se añadieron 1.087 combinaciones ausentes como cero, identificadas con `relleno_cero`; explicitar que es una hipótesis pendiente de validar con el DTPM.
- **Visual:** tabla por corte con comunas, filas observadas y celdas completadas.

## 5. Análisis descriptivo

- En las tablas de Subidas, los máximos laborales aparecen alrededor de 07:00–07:30; el perfil horario confirma actividad concentrada en períodos punta.
- Para las 36 comunas comunes, la razón laboral/domingo fue: 2,27 (nov-2024), 3,28 (abr-2025), 2,87 (nov-2025), 3,23 (abr-2026). No se debe afirmar que supera 3× en todos los cortes.
- En abr-2026, las mayores sumas laborales en las 36 comunas comunes fueron Santiago, Maipú y Las Condes; el orden es cualitativamente consistente con la exploración de Etapas, aunque los valores no son comparables por usar fuentes/medidas distintas.
- **Visuales:** `Etapa_02/resultados/figuras/perfil_horario_laboral.png`, `subidas_por_corte_y_dia.png`, `top_comunas_2026_laboral.png`.

## 6. Primer modelo y validación

- Baselines: repetir el último corte disponible y usar la media histórica de la misma comuna/día/franja.
- Modelo ML inicial: HistGradientBoosting con comuna, tipo de día, calendario y valores de cortes anteriores (retardos entre cortes).
- Validación temporal: prueba final en abr-2026; validaciones internas en cortes anteriores. No se mezclaron filas aleatoriamente.
- Como solo existen tres cortes antes del test, la validación tiene pocos puntos temporales y debe considerarse preliminar.

## 7. Resultados preliminares

| Prueba abr-2026 | MAE | RMSE | WAPE |
|---|---:|---:|---:|
| Último corte (nov-2025) | 101,13 | 213,38 | 11,41% |
| Media histórica | 89,27 | 180,97 | 10,07% |
| HistGradientBoosting | 70,82 | 164,90 | 7,99% |

- En la validación interna de nov-2025, HistGradientBoosting obtuvo MAE 147,12, peor que la media histórica (65,32). Por ello no se debe presentar como modelo final: el resultado favorable en abr-2026 requiere más validación y puede depender del corte/fuente.
- **Visual:** barras MAE por modelo, con una nota visible “resultado exploratorio; un único test final”.

## 8. Conclusiones, limitaciones y siguiente iteración

- Se logró construir un panel reproducible y establecer baselines y un primer modelo temporal.
- La media histórica fue más estable en la validación interna; el ML mejora en el último test, pero aún no demuestra generalización consistente.
- Próximos pasos: validar el significado de combinaciones ausentes, investigar la diferencia de medios de pago entre cortes, probar modelos basados en tendencia/rezagos y comparar con un modelo estacional sencillo.
- Reportar aparte cualquier estimación con factor de expansión de Etapas; no mezclarla con el target histórico de Subidas.

## Preguntas que conviene ensayar

1. ¿Por qué el modelo no predice pasajeros reales incluyendo evasión? Porque la medida histórica elegida no contiene una corrección comparable de evasión en los cuatro cortes.
2. ¿Por qué no se hizo un split aleatorio? Porque el objetivo es predecir un corte futuro; usar información temporal futura en entrenamiento sobreestimaría el desempeño.
3. ¿Qué significa `relleno_cero`? Una combinación comuna/día/franja no aparece en el libro; provisionalmente se trató como cero, pero se conserva la marca y se debe verificar esa semántica.
4. ¿Por qué el ML pierde en la validación interna y mejora en abr-2026? Los cortes son pocos y los patrones/fuentes varían; por eso el resultado es preliminar y no se declara un modelo final.
