# Bitácora de Datos — Demanda de Transporte Público en Bus (Santiago)
Proyecto CIT3620 · Data Science UDP · Última actualización: 21 de octubre 2026

> Este documento consolida las fuentes, decisiones técnicas y limitaciones conocidas,
> y registra el avance reproducible de Etapa II junto con los siguientes pasos.

---

## 1. Inventario de datos — qué tenemos realmente

| Fuente | Períodos disponibles | Estado |
|---|---|---|
| **Subidas por Paradero y Estación** (agregado semanal) | 2024-11, 2025-04, 2025-11, 2026-04 | ✅ Consolidadas en `Etapa_02/resultados/panel_demanda_bus.csv` |
| Subidas por Paradero — **abril 2024** | — | ❌ **Confirmado ausente.** El link del portal DTPM para "Abril 2024" descarga el mismo archivo que "Abril 2025 v2" (`Subida_Paradero_Estacion_2025_04_v2.xlsb`). Verificado vía `FICHA_DATOS`: ambos dicen "Vigencia: Abril 2025 (21–25)". El corte de abril 2024 no está disponible. **Hay 4 cortes únicos, no 5.** |
| **Tabla de Etapas** (individual) | ZIP disponibles para 2024-04, 2024-11, 2025-04, 2025-11 y 2026-04 | ✅ Paquetes y estructuras organizados en `Datos/Fuentes/`; los períodos 2024–2025 aún no se han procesado para comparación. |
| Tabla de Etapas — exploración de abril 2026 | **Lunes 13 abril 2026** y algunos días del corte | ✅ Verificado: 5.027.059 etapas el lunes 13, 35 columnas leídas, 0 nulos en columnas clave; conteos de 11 y 12 de abril también verificados. |
| **Tabla de Viajes** | ZIP disponibles para 2024-04, 2024-11, 2025-04, 2025-11 y 2026-04 | ✅ Paquetes y estructuras organizados en `Datos/Fuentes/`; los períodos 2024–2025 aún no se han procesado para comparación. |
| Tabla de Viajes — exploración de abril 2026 | **Lunes 13 abril 2026** (día hábil) | ✅ Verificado previamente: muestra de 200k filas y distribución por número de etapas y propósito confirmada. |
| GTFS estático (Red Movilidad) | — | ❌ No recibido. Se necesita para variables de oferta (frecuencia de servicio), **no** para comuna (eso ya viene en los datos) |
| Índice de Evasión / Indicadores de Operación (DTPM) | — | ❌ No descargado. Opcional / *nice to have* |

---

## 2. Decisiones técnicas ya tomadas (y por qué)

| Decisión | Justificación |
|---|---|
| Filtrar `Modo` / `tipo_transporte == BUS` | El alcance del proyecto es la red de buses; los archivos DTPM traen Bus+Metro+Tren(+ZP) mezclados |
| Usar `Subida_Paradero_Estacion_2025_04_v2.xlsb` (no la versión sin `_v2`) | La v2 agrega la columna SIMIT y corrige el casing de `Modo` (`BUS` vs `Bus`), igual que los cortes más recientes |
| Normalizar `Comuna`: strip + upper + fix de encoding | Los archivos `.xlsb` (2024-11, 2025-04) traían nombres de comuna corruptos (mala doble-decodificación Latin-1/CP-1252). Fix: probar `latin1`, si falla probar `cp1252` |
| Unificar `"-"` y `"SIN_COMUNA"` en una sola categoría | Ambos representan paraderos sin comuna asignable (GPS perdido, aguas arriba/abajo sin match) |
| `Media_hora` normalizada a hora decimal | openpyxl entrega `datetime.time`, pyxlsb entrega fracción de día (float) — hay que soportar ambos formatos |
| Tratar `"-"` como nulo explícito en Etapas/Viajes | El separador de nulos en estas tablas es el string `"-"`, no un campo vacío ni NaN — un `isna()` estándar no lo detecta |

---

## 3. Limitaciones conocidas y su tratamiento

| Limitación | Evidencia | Qué falta decidir |
|---|---|---|
| Sin evasión tarifaria | Declarado por el DTPM en `FICHA_DATOS` de todos los archivos | Mencionarlo como límite del alcance, no requiere acción |
| Solo semanas representativas, no serie continua | Cada corte = 1 semana muestral, 2-3 veces al año | Modelar como panel de períodos (train en 2024-2025, test en abril 2026), no como serie diaria continua |
| `commune_bajada` con **29,4% de nulos en BUS** (no 35,7%) | Verificado directamente sobre 1.929.443 etapas BUS del Lunes 13 abr 2026: 567.542 valores `"-"` o NaN = 29,4% | **Pendiente:** ¿se excluye "bajadas" del alcance de Etapa II, o se imputa/documenta el sesgo? |
| `fExpansionServicioPeriodoTS` con outliers extremos (máx. real: **122,0**, no 176,4; 40 registros > 50; 9 registros > 100) | Verificado sobre los 5.027.059 registros completos del Lunes 13 | **Pendiente:** decidir umbral de winsorización (sugerido: cap en percentil 99 = 2,42) |
| Cobertura real: **39 comunas** (no 34 ni ~40) | Verificado: lista completa de `comuna_subida` únicas en BUS (13-abr-2026) | Ajustado en el informe: "comunas de la RM servidas por Red Movilidad" |

---

## 4. Pendientes de datos y documentación

- [x] Confirmar si el corte de abril 2024 existe → **Confirmado:** el link DTPM de abr-2024 descarga el mismo archivo que abr-2025 v2 (verificado vía `FICHA_DATOS`). Hay cuatro cortes únicos.
- [ ] Verificar las cifras de la exploración de Tabla de Etapas con su notebook de origen antes de reutilizarlas en una presentación.
- [ ] Confirmar con DTPM si una combinación comuna/día/franja ausente en las tablas de Subidas representa cero demanda o falta de cobertura.
- [ ] Aclarar la comparabilidad de medios de pago entre cortes; la ficha de abr-2026 menciona bip! u otro medio de pago.

---

## 5. Estado técnico del avance de Etapa II

- [x] Construir el panel histórico de Subidas, normalizando modos, comunas, franjas y formatos.
- [x] Mantener un panel observado disperso y un panel de modelamiento con 36 comunas comunes; marcar las combinaciones completadas provisionalmente con cero.
- [x] Usar validación temporal, reservar abr-2026 como prueba final y comparar último corte, media histórica y un primer HistGradientBoosting.
- [ ] Reforzar la evaluación: la validación interna de nov-2025 favoreció a la media histórica y los cortes disponibles son pocos.
- [ ] Mantener Etapas/Viajes como análisis complementario, sin mezclarlos con el target histórico de Subidas; evaluar los cortes nuevos solo en un análisis separado y después de revisar los factores de expansión.
- [x] Consolidar en `Datos/Fuentes/` las fuentes utilizadas y los datos complementarios futuros; quitar copias duplicadas verificadas por SHA-256.
- [x] Organizar los entregables y documentar la reproducción en `README.md`.

---

## 6. Archivos de referencia generados

- `Etapa_02/resultados/panel_demanda_bus.csv` — panel observado agregado (comuna × tipo_día × media_hora × período), solo Bus, 4 períodos, 20.051 filas
- `Etapa_02/codigo/build_panel.py` — script de consolidación (incluye el fix de encoding y el filtro de Bus)
