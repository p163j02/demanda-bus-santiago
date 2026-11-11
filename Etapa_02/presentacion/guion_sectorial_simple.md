# Guion de la entrega sectorial de Etapa II

Presentación principal: `output/presentaciones/etapa_ii_oriente_sur_entrega.pptx` y su PDF. Cada diapositiva incluye notas detalladas. Fuente actual: exclusivamente Subidas del DTPM. Etapas, Viajes y referencias geográficas se reservan para una fase posterior.

1. **Portada.** Pronóstico de subidas registradas y comparación de oriente con sur.
2. **Foco.** Acotar el problema a dos sectores, mantener medias horas y pronosticar niveles mediante una referencia sencilla.
3. **Sectores.** Seis comunas de oriente y diez del sur. Agrupación analítica explícita, sin ajuste por población u oferta.
4. **Objetivo.** Comparar perfiles, pronosticar cantidades y etiquetar su intensidad. Separar lo realizado de lo pendiente.
5. **Limpieza.** Filtrar BUS, normalizar nombres y horas, agrupar y seleccionar comunas comparables. Conservar ceros observados. El panel mantiene las ausencias marcadas con cero, pero el modelo actual excluye los agregados sectoriales incompletos. Cuatro cortes. Excluir agregados incompletos al construir antecedentes y evaluar. Abril: 135/144 franjas evaluables en oriente y 117/144 en sur.
6. **Etiquetas.** Suma sectorial dividida por número fijo de comunas. Terciles históricos comunes: 392,16 y 962,52. Nulo exige cero observado completo. Ausencia y falta de historial se distinguen.
7. **Volumen.** Abril laboral: máximo del sur a las 07:00 y de oriente a las 18:00.
8. **Forma.** Mañana 06:00–09:00: sur 28,9% frente a oriente 21,7%. Tarde 16:00–20:00: oriente 32,4% frente a sur 27,6%. Los intervalos superiores son exclusivos.
9. **Mapa horario.** Comparar las etiquetas observadas por zona y tipo de día. No forzar casos de nulo.
10. **Similitudes y diferencias.** Ambos tienen dos puntas, con distinta concentración relativa.
11. **Historia.** Sur mantiene el máximo a las 07:00 en los cuatro cortes. Oriente tiene una excepción a las 08:00 en noviembre 2025.
12. **Transición de modelos.** El avance comunal utilizaba HistGradientBoosting y referencias. La entrega sectorial actual usa media histórica y último observado. Las unidades y métricas son distintas.
13. **HistGradientBoosting como antecedente.** Árboles sucesivos corrigen la estimación del conjunto. Usaba comuna, calendario e historial. Reaplicarlo al nuevo objetivo exigiría reentrenamiento y evaluación comparable.
14. **Flujo actual.** Entrada: historial completo por sector/día/franja. Media histórica para la cantidad, umbrales para la etiqueta y evaluación separada de cantidades y clases. Contraste con último observado.
15. **Ejemplo.** Sur, laboral,07:00. Valores históricos 18.728,20.766 y 19.844. Media 19.779,33. Observado 21.232. Ambas etiquetas son altas, aunque el número no coincida.
16. **Cantidades.** La media mejora en oriente. En sur los métodos son prácticamente iguales. El MAE es por sector, no por comuna, y no se compara con el avance anterior.
17. **Etiquetas.** Coincidencia 83,7% en oriente y 88,0% en sur. Revisar grupos:16 de 31 franjas medias de oriente se pronostican altas. Nulo no tiene soporte para evaluar.
18. **Tiempo.** En noviembre 2025 la media mejora en ambos sectores. En abril 2026 su ventaja se mantiene solo en oriente. Evaluación retrospectiva, con pocos cortes.
19. **Límites.** Ausencias, pocos períodos y umbrales exploratorios. Otras fuentes y oferta se integrarán después.
20. **Conclusión.** Comparación reproducible y pronóstico interpretable. Orientar una revisión operativa, sin afirmar que ya se demostró un cambio necesario de frecuencia.

## Preguntas clave

**¿Se eliminó la forma de dos puntas?** Se conserva. Cada horario usa su propio historial, sin imponer una curva general a toda la región.

**¿Por qué un método sencillo?** Es una referencia interpretable y evaluable con los pocos cortes disponibles. No se presume que un modelo complejo sea mejor. La media no gana en todos los sectores y cortes.

**¿Se entrenó un clasificador?** No. Se pronostica una cantidad y se aplica una regla histórica para obtener el nivel.

**¿Qué significa 88% de coincidencia?** Coincidencia de etiquetas en 103 de 117 franjas del sur. No significa 88% de precisión del volumen de subidas.

**¿Por qué no hay nulos?** No existen agregados sectoriales completos con cero en estos datos. Una fila ausente no demuestra demanda nula.

**¿Se pueden recomendar frecuencias?** Los perfiles señalan horarios que conviene revisar. Una recomendación requiere oferta, capacidad y ocupación.

**¿Dónde quedó HistGradientBoosting?** Se explica como antecedente metodológico en las diapositivas 12 y 13. La media histórica de esta entrega es un método diferente. No se afirma que el modelo anterior esté reentrenado por sector.
