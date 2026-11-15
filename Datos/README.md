# Datos del proyecto

`Datos/` es la carpeta única de referencia para los **datos de origen** del proyecto. Las fuentes originales y los materiales necesarios para interpretarlas están organizados en [`Fuentes/`](Fuentes/README.md): Subidas, Etapas, Viajes, diccionarios y estructuras.

Los paneles, métricas y gráficos calculados no se duplican aquí: se guardan con la etapa que los produjo, por ejemplo en `Etapa_02/resultados/`. Así se mantiene clara la diferencia entre fuente original y resultado procesado.

La descarga temporal `Datos_descargados_hoy/` se consolidó en `Fuentes/`; las copias idénticas se eliminaron después de compararlas. Se revisaron posteriormente fuentes históricas de Subidas y se seleccionaron candidatos de Etapas de 2022–2023, todavía separados del modelo. El [inventario de Etapas](Fuentes/Etapas/README.md) detalla el alcance y la limpieza.

Para compartir las fuentes actuales y los candidatos seleccionados con el equipo, se generó el paquete que ahora está en `Datos/Datos_equipo_etapa_03.zip`, diferenciado del nombre original `Datos.zip`. El ZIP no se versiona; su contenido y las instrucciones de extracción se describen en [compartir datos de etapa 3](../Etapa_03/compartir_datos.md).
