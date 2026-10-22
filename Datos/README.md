# Datos del proyecto

`Datos/` es la carpeta única de referencia para los **datos de origen** del proyecto. Las fuentes originales y los materiales necesarios para interpretarlas están organizados en [`Fuentes/`](Fuentes/README.md): Subidas, Etapas, Viajes, diccionarios y estructuras.

Los paneles, métricas y gráficos calculados no se duplican aquí: se guardan con la etapa que los produjo, por ejemplo en `Etapa_02/resultados/`. Así se mantiene clara la diferencia entre fuente original y resultado procesado.

La descarga temporal `Datos_descargados_hoy/` se consolidó en `Fuentes/`; las copias idénticas se eliminaron después de compararlas. No se descargaron ni conservaron en el proyecto los paquetes históricos anteriores a 2024 que no forman parte del alcance actual.
