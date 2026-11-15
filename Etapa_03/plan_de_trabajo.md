# Plan de trabajo — Etapa 3: evaluación, selección e interpretación

## Objetivo y alcance

Completar una solución reproducible para comparar y pronosticar las subidas registradas de buses en oriente y sur, por tipo de día y franja de 30 minutos, con etiquetas de intensidad horaria.

El primer avance consolidará la evaluación existente. La entrega final incluirá comparación de métodos, selección justificada, interpretación, presentación y notebook, conforme a la [rúbrica del proyecto](../Documentacion/Rubrica_Proyecto_2026-02.pdf).

Mantener las fuentes y los sectores de la etapa 2. Comparar **media histórica y último observado**; incorporar otro algoritmo no será requisito de este plan. No prometer una mejora mínima ni decisiones de frecuencia y flota.

Este alcance reformula los objetivos de la etapa 1: se pronostican subidas registradas sectoriales, no pasajeros reales corregidos por evasión. Debe explicarse esa diferencia en la entrega.

## Estado del avance para revisión del equipo

`[x]` indica trabajo realizado; `[ ]` indica trabajo pendiente. Una tarea técnica terminada no equivale a la aprobación del equipo ni a una selección definitiva.

- [x] Mantener las etapas 1 y 2 y guardar el avance nuevo en `Etapa_03/`.
- [x] Implementar la base reproducible del Hito 1: auditoría, predicciones, métricas, perfiles y cobertura.
- [x] Reproducir 1.728 predicciones, 12 filas de métricas y la matriz de abril de 2026 de etapa 2.
- [x] Ejecutar controles temporales y cinco pruebas automatizadas.
- [x] Revisar los seis libros de Subidas/Bajadas de 2023 y documentar los resultados en [revisión de 2023](revision_datos_2023.md).
- [x] Explorar los agregados históricos de Subidas de 2012–2019; mantenerlos fuera del panel actual.
- [x] Inspeccionar encabezados y muestras de las bases nuevas de Etapas y organizar nueve ZIP candidatos en `Datos/Fuentes/Etapas/Utiles/`.
- [x] Limpiar archivos de Etapas de 2020–2021 fuera del alcance actual y duplicados verificados de 2026; registrar motivos y hashes en [el inventario](../Datos/Fuentes/Etapas/README.md).
- [x] Generar y verificar `Datos/Datos_equipo_etapa_03.zip` para el equipo: fuentes actuales, paneles/resultados y candidatos separados en el manifiesto. Véase [cómo compartir y extraer el paquete](compartir_datos.md).
- [ ] Asignar responsables y aprobar el objetivo, el relato y el cierre compartido del Hito 1.
- [ ] Validar e integrar, si corresponde, los candidatos de ampliación; aún no aportan cortes al modelo.
- [ ] Completar la evaluación ampliada y la selección provisional del Hito 2.
- [ ] Integrar notebook, figuras, presentación y revisión contra la rúbrica del Hito 3.

**Base utilizada hoy:** Subidas de noviembre de 2024, abril de 2025 v2, noviembre de 2025 y abril de 2026. Se mantienen Oriente y Sur, tres tipos de día y 48 franjas. No se ha incorporado ningún corte nuevo ni elegido un método definitivo.

## Ampliación de datos — trabajo paralelo condicionado

La revisión de fuentes adicionales no debe detener el Hito 2 con la base actual. Descargar u organizar una fuente no confirma comparabilidad, cobertura ni mejora del pronóstico.

- [x] Conservar Subidas de abril, agosto y noviembre de 2023 como candidatos laborales; identificar diferencias de modo, nombres, períodos y ausencias.
- [x] Conservar Etapas de agosto de 2022; abril, agosto y noviembre de 2023; abril y noviembre de 2024; abril y noviembre de 2025; y abril de 2026.
- [x] Detectar que los CSV de 2022–2023 tienen 32 columnas, incluido `netapa`, mientras sus estructuras describen 31.
- [ ] Auditar completamente Etapas de noviembre de 2023: fechas, tipos de día, modos y zonas pagas, comunas/paraderos, ausencias y factores de expansión.
- [ ] Cotejar la reconstrucción laboral con las Subidas publicadas de noviembre de 2023; no contar filas ni aplicar factores automáticamente.
- [ ] Si el cotejo funciona, revisar los otros cortes de 2023 y agosto de 2022. Confirmar especialmente la cobertura de agosto de 2023, cuyo ZIP es mucho menor.
- [ ] Evaluar la reconstrucción de abril de 2024 como posible corte adicional; el enlace de Subidas sigue entregando abril de 2025 v2.
- [ ] Acordar si la ampliación será análisis de sensibilidad o parte de la evaluación principal; comparar historiales sobre las mismas filas objetivo.
- [ ] Construir paneles candidatos separados, conservar la distinción ausencia/cero y repetir controles antes de integrarlos.

Los archivos de 2020–2021 eliminados estaban fuera de este alcance, no se declararon inválidos. Los históricos más antiguos quedan como antecedentes exploratorios. Véase [la selección de Etapas](../Datos/Fuentes/Etapas/README.md).

## Organización del equipo

Conservar los archivos de las etapas 1 y 2 como antecedentes. Guardar el código, notebook, resultados y presentación nuevos bajo `Etapa_03/`. Enlazar esta etapa desde el README principal al integrar la entrega.

Los integrantes asignarán sus nombres a los siguientes cuatro frentes. Si son cinco, separar presentación y coordinación. Actualizar responsables y estados en esta tabla durante el trabajo.

| Frente | Responsable | Estado | Trabajo y entregable | Dependencias |
|---|---|---|---|---|
| A. Datos y reproducibilidad | Por asignar | Base técnica del Hito 1 implementada; revisión de equipo pendiente | Verificar panel, cobertura, ceros y unidad de análisis. Documentar fuentes, exclusiones y ejecución. Preparar la entrada reproducible para evaluar. | Puede comenzar inmediatamente. |
| B. Evaluación y selección | Por asignar | Referencias reproducidas; ampliación y selección pendientes | Reproducir referencias, ampliar métricas y aplicar la regla de selección. Entregar predicciones y tablas comparativas. | Reutiliza el panel actual; cierra tras la revisión de A. |
| C. Interpretación y gráficos | Por asignar | Pendiente | Analizar perfiles, errores y etiquetas. Preparar figuras y conclusiones con sus límites. | Puede estudiar perfiles ahora; conclusiones finales dependen de B. |
| D. Narrativa y entrega | Por asignar | Pendiente | Redactar objetivos revisados, cambios desde etapa 2 y estructura de presentación. Integrar notebook, conclusiones y ensayo. | Puede comenzar inmediatamente; cierra con A, B y C. |

### Antecedentes para comenzar

- [Resumen de cambios y curvas](../Etapa_02/presentacion/resumen_cambios_y_curvas.md).
- [Metodología y resultados sectoriales actuales](../Etapa_02/resultados/sectorial_simple/README.md).
- [Script de pronóstico sectorial](../Etapa_02/codigo/pronostico_sectorial_simple.py).
- [Notebook sectorial de etapa 2](../Etapa_02/notebooks/etapa_ii_sectorial_simple.ipynb).

## Trabajo técnico y criterios de decisión

### Datos y evaluación

- Reutilizar el panel comunal y la lógica sectorial actual, sin importar scripts antiguos que ejecuten análisis al cargarse.
- Mantener `relleno_cero` como señal de ausencia. Excluir agregados incompletos del historial y de los objetivos evaluados; no convertirlos en categoría nulo.
- Evaluar abril de 2025, noviembre de 2025 y abril de 2026 usando solo publicaciones anteriores. Explicar que la primera comparación empata porque dispone de un único antecedente.
- Comparar ambos métodos sobre las mismas filas en cada sector y corte. Mostrar cantidad y porcentaje de franjas evaluadas, incompletas y sin historial.
- Calcular umbrales de etiquetas solo con antecedentes completos del corte evaluado. No usar una división aleatoria de filas.
- Reconocer que abril de 2026 ya fue observado y que toda esta evaluación es retrospectiva.

### Métricas y selección

- Mantener MAE y WAPE para volumen, coincidencia de etiquetas y matriz de confusión para categorías.
- Añadir resultados por tipo de día y error firmado medio para identificar sobreestimación o subestimación. Definir el error firmado como predicción menos observado.
- Informar cuántas franjas altas se detectan y cuántas se subestiman. Cuando una categoría no tenga casos, indicar «no evaluable».
- Seleccionar un método por sector mediante el **WAPE conjunto de noviembre de 2025 y abril de 2026**, calculado como `100 × suma de errores absolutos / suma de observaciones` de ambos cortes, no promediando porcentajes.
- Si la diferencia es inferior a **0,5 puntos porcentuales de WAPE**, declarar empate práctico y elegir último observado por simplicidad. Este umbral será una convención del proyecto, no evidencia de significancia estadística. En los demás casos, elegir el menor WAPE conjunto.
- Mostrar siempre ambos cortes por separado para que el resultado conjunto no oculte cambios de desempeño. La selección será provisional, no una validación independiente del método elegido.

### Interpretación y visualización

- Comparar perfiles de oriente y sur por tipo de día, conservando franjas de 30 minutos.
- Mostrar observado frente a pronosticado y localizar errores por horario; representar los datos faltantes como interrupciones, no como ceros.
- Revisar mañana de 06:00 a 09:00 y tarde de 16:00 a 20:00, con límite superior excluido, manteniendo las ventanas del análisis anterior.
- Separar gráficos de volumen sectorial y promedio por comuna. Explicar que este último no ajusta por población ni oferta.
- No calcular participaciones diarias como si hubiera cobertura total cuando existan franjas incompletas.
- Interpretar las dos puntas como patrones observados. No atribuir destinos, motivos de viaje o saturación sin evidencia adicional.

## Entregables y secuencia

### Hito 1 — Base compartida y resultados reproducidos

A y B verifican cobertura y reproducen las métricas de etapa 2. C y D avanzan en perfiles, objetivos y relato de cambios. Al cerrar este hito, el equipo comparte una sola definición del objetivo y de la validación.

#### Avance aplicado del Hito 1

La [base reproducible](README.md) audita los paneles incluidos, reproduce las predicciones, métricas y matriz de etapa 2 y publica cobertura por sector, corte y tipo de día. Incluye controles temporales para los tres cortes evaluados y cinco pruebas de casos límite. Los perfiles nuevos conservan las interrupciones por ausencia y omiten participaciones diarias si la cobertura no es total.

No se han releído los libros originales ni revisado la entrega contra la rúbrica. Los responsables, la discusión de perfiles y la aprobación del objetivo y relato por el equipo siguen pendientes; este avance no cierra por sí solo el hito compartido.

### Hito 2 — Evaluación ampliada y decisión

B entrega tablas y selección por sector. C documenta dónde funcionan y fallan los métodos, incluyendo franjas altas y ausencia de casos nulos confirmados. Se congelan resultados antes de terminar las diapositivas.

- [ ] Añadir error firmado medio, definido como predicción menos observado.
- [ ] Calcular métricas por tipo de día; la cobertura por tipo de día ya existe, pero no sustituye estas métricas.
- [ ] Informar detección y subestimación de franjas altas, con «no evaluable» donde no haya casos.
- [ ] Generar matrices ampliadas para ambos métodos y los cortes evaluados.
- [ ] Seleccionar provisionalmente por sector mediante WAPE conjunto de noviembre de 2025 y abril de 2026; aplicar la regla de empate práctico de 0,5 puntos.
- [ ] Mostrar ambos cortes por separado, interpretar errores y congelar las salidas finales.

### Hito 3 — Entrega integrada

- [ ] Notebook Python con Markdown: problema, cambios, datos, limpieza, métodos, validación, resultados, selección, interpretación y limitaciones.
- [ ] Presentación PPT/PDF: problema y objetivos revisados; cambios desde etapa 2; datos y cobertura; métodos; validación; resultados; selección; interpretación; conexión con el problema inicial.
- [ ] CSV finales de predicciones, cobertura, métricas y matrices; gráficos utilizados en la presentación. Las referencias del Hito 1 ya están generadas.
- [ ] Instrucciones completas de instalación y ejecución de la entrega final. Las del Hito 1 y sus dependencias ya existen.
- [ ] Ensayo en el que cada integrante explique la selección, las ausencias, las etiquetas y las limitaciones temporales.

Planificar el cierre para la primera fecha de la rúbrica, **16 de noviembre de 2026**, mientras no esté confirmada la asignación del equipo al día 19.

## Verificación y condiciones de cierre

- [x] Reproducir las métricas actuales con tolerancia de redondeo antes de ampliar el análisis.
- [x] Comprobar que modificar valores futuros no cambia pronósticos ni umbrales anteriores.
- [x] Verificar límites de etiquetas, exclusión de agregados incompletos, falta de historial y ausencia de división por cero.
- [x] Confirmar para el Hito 1 que ambos métodos usan las mismas filas y que matrices y métricas concuerdan con sus conteos.
- [ ] Repetir la comparación de filas y conteos sobre las salidas ampliadas del Hito 2.
- [ ] Ejecutar el notebook completo desde un entorno limpio y comprobar que las cifras de la presentación provienen de sus resultados.
- [ ] Confirmar que cada conclusión tiene respaldo reproducible y cada requisito de etapa 3 está cubierto.

Se excluyen dashboard, clasificador separado y búsqueda de hiperparámetros. Las nuevas fuentes solo se integrarán tras la validación y el acuerdo de alcance descritos arriba; no son un requisito para avanzar el Hito 2. El riesgo principal sigue siendo la escasez de cortes temporales: la entrega defenderá una solución acotada y evaluada retrospectivamente, sin prometer generalización operativa.

Este documento es un plan: las tareas y verificaciones pendientes no se consideran realizadas por su inclusión aquí.
