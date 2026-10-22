# Exploración de Datos — Matrices de Viaje DTPM
## Abril 2026 (días 11 al 17)

> **Fuente:** Portal DTPM — [www.dtpm.cl/index.php/documentos/matrices-de-viaje](https://www.dtpm.cl/index.php/documentos/matrices-de-viaje)  
> **Período:** Sábado 11 → Viernes 17 de abril de 2026 (7 días consecutivos)  
> **Archivos analizados:** Tabla de Etapas · Tabla de Viajes · Subidas por Paradero y Estación

---

## 1. Inventario de Archivos

| Archivo | Formato | Tamaño comprimido | Separador |
|---|---|---|---|
| `2026-04-11.etapas.csv.gz` | CSV gzip | 173 MB | `\|` (pipe) |
| `2026-04-12.etapas.csv.gz` | CSV gzip | 98 MB | `\|` |
| `2026-04-13.etapas.csv.gz` | CSV gzip | 328 MB | `\|` |
| `2026-04-14.etapas.csv.gz` | CSV gzip | 330 MB | `\|` |
| `2026-04-15.etapas.csv.gz` | CSV gzip | 333 MB | `\|` |
| `2026-04-16.etapas.csv.gz` | CSV gzip | 332 MB | `\|` |
| `2026-04-17.etapas.csv.gz` | CSV gzip | 325 MB | `\|` |
| `2026-04-11.viajes.csv.gz` | CSV gzip | 136 MB | `\|` |
| `2026-04-12.viajes.csv.gz` | CSV gzip | 71 MB | `\|` |
| `2026-04-13.viajes.csv.gz` | CSV gzip | 274 MB | `\|` |
| `2026-04-14.viajes.csv.gz` | CSV gzip | 279 MB | `\|` |
| `2026-04-15.viajes.csv.gz` | CSV gzip | 281 MB | `\|` |
| `2026-04-16.viajes.csv.gz` | CSV gzip | 279 MB | `\|` |
| `2026-04-17.viajes.csv.gz` | CSV gzip | 266 MB | `\|` |
| `Subidas_Paradero_Estacion_2026.04_v3(1).xlsx` | Excel | 28 MB | — |

**Total datos sin comprimir estimado:** ~7–8 GB

---

## 2. Tabla de Etapas

### 2.1 Estructura
- **Número de columnas:** 35
- **Separador:** `|` (pipe)
- **Encoding:** UTF-8

### 2.2 Columnas principales

| Campo | Tipo | Descripción |
|---|---|---|
| `operador` | Int | Código del operador del servicio |
| `id_etapa` | Int | ID de la tarjeta/etapa |
| `tipo_dia` | Texto | `LABORAL` / `SABADO` / `DOMINGO` |
| `tipo_transporte` | Texto | `BUS` / `METRO` / `ZP` / `METROTREN` |
| `media_hora_subida` | Tiempo | Franja de 30 min de la subida (ej: `07:00:00`) |
| `media_hora_bajada` | Tiempo | Franja de 30 min de la bajada |
| `comuna_subida` | Texto | Comuna de origen de la etapa |
| `comuna_bajada` | Texto | Comuna de destino de la etapa |
| `servicio_subida` | Texto | Código del servicio abordado |
| `parada_subida` | Texto | Código del paradero de subida |
| `parada_bajada` | Texto | Código del paradero de bajada |
| `periodoSubida` | Texto | Período operacional (Punta Mañana, Fuera de Punta, Punta Tarde…) |
| `fExpansionServicioPeriodoTS` | Float | **Factor de expansión** → pasajeros reales estimados |
| `tiempo_subida` | DateTime | Timestamp exacto de la subida |
| `tiempo_bajada` | DateTime | Timestamp exacto de la bajada |
| `x_subida` / `y_subida` | Float | Coordenadas del paradero de subida |
| `x_bajada` / `y_bajada` | Float | Coordenadas del paradero de bajada |
| `dist_ruta_paraderos` | Float | Distancia recorrida por ruta (metros) |
| `contrato` | Int | Identificador del contrato de operación |

### 2.3 Volumen de registros por día

| Día | Tipo | Etapas totales |
|---|---|---|
| Sáb 11 | Fin de semana | 2.766.864 |
| **Dom 12** | **Fin de semana** | **1.585.544** |
| **Lun 13** | **Hábil** | **5.027.059** |
| Mar 14 | Hábil | ~5.1M (estimado) |
| Mié 15 | Hábil | ~5.2M (estimado) |
| Jue 16 | Hábil | ~5.1M (estimado) |
| Vie 17 | Hábil | ~5.0M (estimado) |

> **Ratio hábil / domingo: 3.2×** — señal de estacionalidad semanal muy clara para el modelo.

### 2.4 Distribución por modo de transporte (Lun 13 — muestra 300k)

| Modo | Registros | % |
|---|---|---|
| METRO | 139.859 | 46.6% |
| **BUS** | **121.215** | **40.4%** |
| ZP (Zona Paga) | 34.546 | 11.5% |
| METROTREN | 4.380 | 1.5% |

> Para el proyecto se filtra `tipo_transporte = BUS` → **1.929.443 etapas** en el día hábil completo (38.4% del total).

### 2.5 Calidad de datos

| Columna clave | Nulos |
|---|---|
| `media_hora_subida` | **0** |
| `comuna_subida` | **0** |
| `tipo_transporte` | **0** |
| `tipo_dia` | **0** |
| `fExpansionServicioPeriodoTS` | **0** |

> ✅ **Sin valores nulos en ninguna columna clave.** Los datos están muy limpios.

---

## 3. Tabla de Viajes

### 3.1 Estructura
- **Número de columnas:** 101
- **Separador:** `|` (pipe)

### 3.2 Columnas principales

| Campo | Descripción |
|---|---|
| `tipodia` | Tipo de día (0 = hábil, otros = fin de semana) |
| `factor_expansion` | Factor de expansión del viaje |
| `n_etapas` | Número de etapas del viaje (1 a 4) |
| `tviaje` | Tiempo total del viaje |
| `mediahora_inicio_viaje` | Franja de 30 min de inicio |
| `periodo_inicio_viaje` | Código del período operacional |
| `tipo_transporte_1..4` | Modo de cada etapa |
| `srv_1..4` | Servicio de cada etapa |
| `paradero_inicio_viaje` | Paradero de inicio |
| `paradero_fin_viaje` | Paradero de fin |
| `comuna_inicio_viaje` | Comuna de origen del viaje |
| `comuna_fin_viaje` | Comuna de destino del viaje |
| `proposito` | Propósito del viaje |
| `modos` | Código combinado de modos usados |
| `id_tarjeta` | ID anonimizado de la tarjeta |
| `id_viaje` | ID del viaje |

### 3.3 Distribución por número de etapas (Lun 13 — muestra 200k)

| Etapas por viaje | Cantidad | % |
|---|---|---|
| 1 | 145.958 | 73.0% |
| 2 | 48.512 | 24.3% |
| 3 | 5.419 | 2.7% |
| 4 | 111 | 0.1% |

### 3.4 Propósito del viaje

| Propósito | Cantidad | % |
|---|---|---|
| HOGAR | 78.328 | 39.2% |
| TRABAJO | 52.285 | 26.1% |
| OTROS | 40.718 | 20.4% |
| ESTUDIO | 27.519 | 13.8% |
| MENOS1MINUTO | 1.150 | 0.6% |

### 3.5 Calidad de datos (columnas clave)

| Columna | Nulos |
|---|---|
| `tipodia` | **0** |
| `n_etapas` | **0** |
| `mediahora_inicio_viaje` | **0** |
| `comuna_inicio_viaje` | **0** |
| `comuna_fin_viaje` | **0** |
| `proposito` | **0** |
| `factor_expansion` | **0** |

---

## 4. Tabla de Subidas por Paradero y Estación

### 4.1 Estructura (archivo .xlsx)

| Hoja | Contenido |
|---|---|
| `FICHA_DATOS` | Metadatos: fuente, vigencia, alcances y limitaciones |
| `SUBIDAS_2026_04` | Datos agregados de subidas |
| `RESUMEN` | Totales resumidos |

### 4.2 Columnas

| Campo | Descripción |
|---|---|
| `Tipo_dia` | `LABORAL` / `SABADO` / `DOMINGO` |
| `Modo` | `BUS` / `METRO` / `TREN` |
| `Paradero` | Código del paradero |
| `SIMIT` | Código SIMIT del paradero |
| `Comuna` | Nombre de la comuna |
| `Media_hora` | Franja horaria de 30 min |
| `Subidas_Promedio` | **Promedio de subidas** en esa franja/paradero (semana representativa) |

### 4.3 Nota metodológica (FICHA_DATOS)
> *"Resultado: Información procesada a partir de Transacciones Bip! y GPS de los buses. Vigencia: Abril 2026 (días hábiles entre el 11 y 17). Los datos no poseen evasión."*

---

## 5. Hallazgos de la Exploración Preliminar

### 5.1 Patrón bimodal de demanda en buses — Lun 13 abr 2026

| Franja | Subidas estimadas | Nota |
|---|---|---|
| 06:00 | 55.581 | |
| 06:30 | 85.054 | |
| **07:00** | **106.293** | 🔺 **Peak mañana** |
| **07:30** | **101.088** | |
| 08:00 | 94.060 | |
| 08:30 | 75.695 | |
| 09:00 | 62.634 | |
| 09:30 | 53.285 | |
| 10:00 | 50.012 | |
| … | … | Valle mediodía |
| 17:00 | 71.266 | |
| 17:30 | 77.905 | |
| **18:00** | **84.473** | 🔺 **Peak tarde** |
| 18:30 | 68.641 | |

### 5.2 Top 10 comunas por subidas en bus — Lun 13 abr 2026

| Ranking | Comuna | Subidas estimadas |
|---|---|---|
| 1 | Santiago | 180.663 |
| 2 | Maipú | 164.935 |
| 3 | Las Condes | 124.771 |
| 4 | Puente Alto | 107.973 |
| 5 | La Florida | 103.105 |
| 6 | Providencia | 93.758 |
| 7 | Ñuñoa | 81.451 |
| 8 | Pudahuel | 74.239 |
| 9 | Quilicura | 72.885 |
| 10 | Peñalolén | 66.608 |

---

## 6. Conclusiones para el Proyecto

| Aspecto | Evaluación |
|---|---|
| **Calidad de datos** | ✅ Excelente — 0 nulos en columnas clave |
| **Volumen** | ✅ Muy alto — >5M registros/día hábil |
| **Variable objetivo** | ✅ Clara y continua (`fExpansionServicioPeriodoTS` agregada) |
| **Estacionalidad semanal** | ✅ Fuerte y medible — ratio 3.2× |
| **Patrón bimodal** | ✅ Confirmado — peaks 07:00 y 18:00 |
| **Features disponibles** | ✅ `periodoSubida` etiquetado, coordenadas GPS, propósito de viaje |
| **Limitaciones** | ⚠️ Sin evasión · GPS puede fallar en túneles |
| **Viabilidad del modelo** | ✅ **Alta** — datos ideales para LightGBM/XGBoost con features de calendario |
