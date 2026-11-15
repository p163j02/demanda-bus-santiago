# Etapas seleccionadas para el proyecto

Los candidatos útiles están en **`Utiles/`**, separados por corte. Se conservaron nueve ZIP originales sin alterar sus bytes y cinco estructuras TXT. Esta selección no implica que las bases ya sean comparables o estén integradas al modelo.

## Inventario conservado

| Carpeta en `Utiles/` | ZIP original | Período anunciado por nombres internos | Uso previsto |
|---|---|---|---|
| `2022-08/` | `etapas_082022_8al14_transparencia.zip` | 8–14 agosto 2022 | Ampliación, después de validar 2023. |
| `2023-04/` | `etapas_042023_17al23_transparencia.zip` | 17–23 abril 2023 | Reconstrucción y cotejo con Subidas laborales. |
| `2023-08/` | `etapas_082023_7al13.zip` | 7–13 agosto 2023 | Candidato con cobertura pendiente; tamaño mucho menor que los otros ZIP de 2023. |
| `2023-11/` | `etapas_112023_6al12.zip` | 6–12 noviembre 2023 | Primera prueba de reconstrucción y cotejo con Subidas laborales. |
| `2024-04/` | `etapas202404_transparencia_15al21.zip` | 15–21 abril 2024 | Posible corte adicional: el enlace de Subidas no entrega el libro de este período. |
| `2024-11/` | `Tabla-de-Etapas- Nov24.zip` | 18–24 noviembre 2024 | Control de concordancia con la base actual. |
| `2025-04/` | `Tabla-de-etapas-011025.zip` | 21–27 abril 2025 | Control de concordancia con la base actual; no confundir el nombre externo con la fecha del corte. |
| `2025-11/` | `Etapas_Nov_2025.zip` | 8–14 noviembre 2025 | Control de concordancia con la base actual. |
| `2026-04/` | `Etapas-2026-04.zip` | 11–17 abril 2026 | Control de concordancia con la base actual. |

También se conservó `Utiles/2022-04/Estructura Tabla Etapas ABR22.txt`: **solo estructura, sin base descargada**. Las estructuras de agosto de 2022 y los tres cortes de 2023 acompañan sus ZIP. Las referencias de 2024–2026 permanecen en `../Referencias/Estructuras/`.

## Comprobaciones y pendientes

- Se inspeccionaron los miembros de todos los ZIP y se leyeron sus encabezados y hasta 40 filas por CSV. Los ZIP de 2024–2026 contienen siete miembros diarios; sus fechas también aparecen en las muestras. Los de 2022–2023 contienen un solo CSV por paquete: sus nombres no certifican que estén todos los días.
- Los CSV conservados de 2022–2023 tienen **32 columnas**, incluido `netapa`; sus TXT describen 31. Se debe leer por encabezado real, no asignar columnas por posición a partir de esas estructuras.
- Los CSV de 2024–2026 tienen **35 columnas**. Se observaron modos `BUS`, `METRO`, `METROTREN` y `ZP` en las muestras; no son un inventario exhaustivo de categorías.
- Antes de reconstruir Subidas faltan validar fechas completas, tipos de día, modo/zona paga, comunas, ausencias y factores de expansión. No contar filas automáticamente ni aplicar corrección por evasión.
- No se modificaron los paneles, los pronósticos ni las métricas de las etapas 2 y 3.

## Limpieza realizada

Se eliminaron definitivamente, por solicitud del usuario y por quedar **fuera del alcance actual 2022–2026**, los ZIP de marzo de 2020 (laboral y sábado/domingo), noviembre de 2020 y abril de 2021, junto con las cuatro estructuras de 2020–2021. Esto no afirma que esas fuentes sean inválidas; para un estudio específico de ese período habría que descargarlas nuevamente.

También se eliminaron siete GZIP extraídos de abril de 2026 y el CSV descomprimido del 11 de abril. Antes de eliminarlos se comprobaron los SHA-256 completos: cada GZIP coincide con su miembro dentro del ZIP conservado y el CSV coincide con el contenido descomprimido del GZIP del día 11.

**Espacio liberado:** 5.464 GB decimales (5.089 GiB), en 16 archivos. La limpieza se limitó a `Datos/Fuentes/Etapas/`; no se eliminaron fuentes de Subidas, Viajes ni archivos de otras carpetas.

El registro de rutas originales, destinos, tamaños, motivos y hashes de los archivos conservados/duplicados está en [`seleccion_archivos.json`](seleccion_archivos.json). La inspección temporal está en `/tmp/docs/seleccion_etapas/`; no sustituye una auditoría completa de las bases.
