# Revisión de las descargas recientes del DTPM

## Resumen ejecutivo

La descarga temporal contenía **27 archivos, aproximadamente 19,43 GB**. Se consolidó en la carpeta canónica `Datos/Fuentes/`: se reubicaron 20 archivos únicos (ZIP complementarios, estructuras y referencias) sin cambiar sus bytes; se eliminaron siete copias duplicadas después de comparar sus hashes. La carpeta temporal `Datos_descargados_hoy/` ya no existe.

**Conclusión para el modelo actual:** están descargados los cuatro cortes de Subidas que usa Etapa II. Los cinco libros de Subidas encontrados en la descarga nueva corresponden byte por byte a los libros que ya estaban en `Datos/Fuentes/Subidas/` (verificación SHA-256). Por tanto, la descarga de hoy no revela un nuevo corte compatible de Subidas para agregar al modelo.

**Sí se agregaron otras fuentes útiles:** los ZIP de Etapas y Viajes de abril de 2024, noviembre de 2024, abril de 2025 y noviembre de 2025, además de los de abril de 2026. Antes de hoy, en `Datos/Fuentes/` solo estaba incorporado abril de 2026 para esas dos tablas. Estos períodos adicionales no se usaron para desarrollar el panel/modelo de Subidas.

## 1. Libros de Subidas: cotejo con los datos ya usados

| Libro canónico en `Datos/Fuentes/Subidas/` | Correspondencia con la descarga temporal | Uso en el panel actual |
|---|---|---|
| `Subida_Paradero_Estacion_2024.11.xlsb` | Copia descargada con el mismo SHA-256 | Sí: noviembre de 2024. |
| `Subida_Paradero_Estacion_2025_04_v2.xlsb` | Copia descargada como `..._v2(1).xlsb`, con el mismo SHA-256 | Sí: abril de 2025, versión v2. |
| `Subida_Paradero_Estacion_2025.04.xlsb` | Copia descargada con el mismo SHA-256 | No: variante no seleccionada; se prefiere v2. |
| `Subidas_Paradero_Estacion_2025.11.xlsx` | Copia descargada con el mismo SHA-256 | Sí: noviembre de 2025. |
| `Subidas_Paradero_Estacion_2026.04_v3(1).xlsx` | Copia descargada con el mismo SHA-256 | Sí: abril de 2026. |

El archivo v2 renombrado con `(1)` es una copia repetida con nombre cambiado por la descarga, no otra medición. Además, se comprobó nuevamente que el enlace publicado como Subidas de abril de 2024 entrega ese mismo libro v2 y que su ficha indica vigencia de abril de 2025. **No es una descarga omitida por el grupo: es un enlace/archivo mal publicado por DTPM, que al momento de esta revisión sigue sin proporcionar un libro válido de Subidas de abril de 2024.**

## 2. ZIP de Etapas y Viajes recién encontrados

Al revisar los nombres dentro de los ZIP, cada paquete de período contiene siete archivos diarios `.csv.gz`:

| Período dentro de los ZIP | Ruta canónica de Etapas | Ruta canónica de Viajes |
|---|---|---|
| Abril de 2024 (días 15–21) | `Datos/Fuentes/Etapas/2024-04/etapas202404_transparencia_15al21.zip` | `Datos/Fuentes/Viajes/2024-04/viajes202404_transparencia_15al21.zip` |
| Noviembre de 2024 (días 18–24) | `Datos/Fuentes/Etapas/2024-11/Tabla-de-Etapas- Nov24.zip` | `Datos/Fuentes/Viajes/2024-11/Tabla-de-Viajes-Nov-24.zip` |
| Abril de 2025 (días 21–27) | `Datos/Fuentes/Etapas/2025-04/Tabla-de-etapas-011025.zip` | `Datos/Fuentes/Viajes/2025-04/Tabla-de-viajes-011025.zip` |
| Noviembre de 2025 (días 8–14) | `Datos/Fuentes/Etapas/2025-11/Etapas_Nov_2025.zip` | `Datos/Fuentes/Viajes/2025-11/Tablas_viajes_NOV_2025.zip` |
| Abril de 2026 (días 11–17) | `Datos/Fuentes/Etapas/2026-04/Etapas-2026-04.zip` | `Datos/Fuentes/Viajes/2026-04/Viajes_2026-04.zip` |

Los ZIP de abril de 2026 ya estaban guardados antes y tienen SHA-256 idéntico al de la descarga; se conservó una sola copia canónica. Los ZIP de los otros cuatro cortes son los archivos nuevos reubicados. Los nombres internos del ZIP de abril de 2025 confirman fechas `2025-04-21` a `2025-04-27`.

Los ZIP de períodos anteriores son **datos nuevos para el proyecto** comparados con la carpeta original de fuentes. Pueden apoyar análisis complementarios con varias fechas, pero sus registros de viajes/etapas no se deben pegar directamente al panel de Subidas: representan unidades distintas. No se ha vuelto a ejecutar el análisis de Etapas/Viajes con esos nuevos cortes.

Como comprobación inicial, los archivos de estructura de los cinco cortes tienen los mismos campos y en el mismo orden: **35 campos en Etapas y 100 en Viajes**. Eso facilita plantear una comparación temporal, aunque no demuestra por sí solo que la cobertura y la medición sean idénticas entre años; aún habría que revisar los valores, factores de expansión, categorías y notas metodológicas de cada período.

## 3. Documentos y otros archivos descargados

El diccionario de campos, los `.txt` de estructura por año y `Zona777_ADATRAP.rar` (referencia geográfica) están organizados en `Datos/Fuentes/Referencias/`. Ayudan a interpretar las tablas; no son entradas del modelo de Subidas.

## 4. ¿Falta algo todavía en comparación con toda la página DTPM?

Sí, si “todo” significa **cada descarga histórica listada** en [Matrices de Viaje del DTPM](https://www.dtpm.cl/index.php/documentos/matrices-de-viaje). `Datos/Fuentes/` cubre períodos de 2024–2026, pero no contiene los paquetes más antiguos que la página todavía lista (por ejemplo, varios períodos de 2023 y años anteriores), ni los antiguos archivos agregados llamados “Tablas de Subidas y Bajadas”. Esos archivos históricos tienen formatos/definiciones que deben revisarse antes de considerarlos comparables y se dejaron fuera del alcance actual.

Esto no significa que falte un insumo compatible para reproducir el modelo vigente: **los cuatro cortes válidos de Subidas que usa el modelo ya estaban y siguen presentes**. La falta confirmada para esa serie es el corte real de abril de 2024; el enlace disponible apunta al archivo v2 de abril de 2025.

## Alcance de la verificación

- Se compararon mediante SHA-256 los cinco libros Excel de Subidas de la descarga temporal con sus copias canónicas, además de los dos ZIP de Etapas/Viajes de abril de 2026.
- Se inspeccionaron las listas de archivos internas de los ZIP para confirmar períodos y días incluidos.
- No se extrajeron ni reprocesaron todas las filas de los ZIP de casi 20 GB; esta revisión es de inventario, nombres/fechas internas y duplicados binarios, no una auditoría estadística completa de cada registro.
- Se reubicaron dentro de `Datos/Fuentes/` los 20 archivos únicos, sin modificar su contenido. Se eliminaron solamente las siete copias binarias duplicadas, tras confirmar los SHA-256. No se editó ningún libro o ZIP original conservado.
