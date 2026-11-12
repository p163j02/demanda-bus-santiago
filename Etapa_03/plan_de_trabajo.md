# Plan de trabajo — Etapa 3: evaluación, selección e interpretación

## Objetivo y alcance

Completar una solución reproducible para comparar y pronosticar las subidas registradas de buses en oriente y sur, por tipo de día y franja de 30 minutos, con etiquetas de intensidad horaria.

El primer avance consolidará la evaluación existente. La entrega final incluirá comparación de métodos, selección justificada, interpretación, presentación y notebook, conforme a la [rúbrica del proyecto](../Documentacion/Rubrica_Proyecto_2026-02.pdf).

Mantener las fuentes y los sectores de la etapa 2. Comparar **media histórica y último observado**; incorporar otro algoritmo no será requisito de este plan. No prometer una mejora mínima ni decisiones de frecuencia y flota.

Este alcance reformula los objetivos de la etapa 1: se pronostican subidas registradas sectoriales, no pasajeros reales corregidos por evasión. Debe explicarse esa diferencia en la entrega.

## Organización del equipo

Conservar los archivos de las etapas 1 y 2 como antecedentes. Guardar el código, notebook, resultados y presentación nuevos bajo `Etapa_03/`. Enlazar esta etapa desde el README principal al integrar la entrega.

Los integrantes asignarán sus nombres a los siguientes cuatro frentes. Si son cinco, separar presentación y coordinación. Actualizar responsables y estados en esta tabla durante el trabajo.

| Frente | Responsable | Estado | Trabajo y entregable | Dependencias |
|---|---|---|---|---|
| A. Datos y reproducibilidad | Por asignar | Pendiente | Verificar panel, cobertura, ceros y unidad de análisis. Documentar fuentes, exclusiones y ejecución. Preparar la entrada reproducible para evaluar. | Puede comenzar inmediatamente. |
| B. Evaluación y selección | Por asignar | Pendiente | Reproducir referencias, ampliar métricas y aplicar la regla de selección. Entregar predicciones y tablas comparativas. | Reutiliza el panel actual; cierra tras la revisión de A. |
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

### Hito 2 — Evaluación ampliada y decisión

B entrega tablas y selección por sector. C documenta dónde funcionan y fallan los métodos, incluyendo franjas altas y ausencia de casos nulos confirmados. Se congelan resultados antes de terminar las diapositivas.

### Hito 3 — Entrega integrada

- Notebook Python con Markdown: problema, cambios, datos, limpieza, métodos, validación, resultados, selección, interpretación y limitaciones.
- Presentación PPT/PDF: problema y objetivos revisados; cambios desde etapa 2; datos y cobertura; métodos; validación; resultados; selección; interpretación; conexión con el problema inicial.
- CSV de predicciones, cobertura, métricas y matrices; gráficos utilizados en la presentación.
- Instrucciones de instalación y ejecución, con dependencias necesarias.
- Ensayo en el que cada integrante explique la selección, las ausencias, las etiquetas y las limitaciones temporales.

Planificar el cierre para la primera fecha de la rúbrica, **16 de noviembre de 2026**, mientras no esté confirmada la asignación del equipo al día 19.

## Verificación y condiciones de cierre

- [ ] Reproducir las métricas actuales con tolerancia de redondeo antes de ampliar el análisis.
- [ ] Comprobar que modificar valores futuros no cambia pronósticos ni umbrales anteriores.
- [ ] Verificar límites de etiquetas, exclusión de agregados incompletos, falta de historial y ausencia de división por cero.
- [ ] Confirmar que métodos comparados usan las mismas filas y que matrices y métricas concuerdan con sus conteos.
- [ ] Ejecutar el notebook completo desde un entorno limpio y comprobar que las cifras de la presentación provienen de sus resultados.
- [ ] Confirmar que cada conclusión tiene respaldo reproducible y cada requisito de etapa 3 está cubierto.

Se excluyen nuevas fuentes, dashboard, clasificador separado y búsqueda de hiperparámetros. El riesgo principal sigue siendo la escasez de cortes temporales: la entrega defenderá una solución acotada y evaluada retrospectivamente, sin prometer generalización operativa.

Este documento es un plan: las tareas y verificaciones pendientes no se consideran realizadas por su inclusión aquí.
