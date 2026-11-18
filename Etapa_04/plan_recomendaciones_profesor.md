# Plan de Ejecución — Recomendaciones del Profesor para la Etapa 4 / Feria de Data Science

## Origen de las recomendaciones

Las siguientes indicaciones fueron entregadas por el profesor durante la presentación de la Etapa 3 (hoja "H3 Demanda de Pasajeros", filas 18-20):

| Fila | Recomendación original | Interpretación |
|------|------------------------|----------------|
| 18 | "Recomiendo que se haga de lunes a Vier, sabado y domingo." | Trabajar **solo con días lunes a viernes** (laborales). Descartar sábado y domingo del análisis. |
| 19 | "Identificar los feriados renunciables e irrenunciables, mediante una dummy" | Crear **dos variables dummy** que capturen el efecto de los feriados sobre la demanda. |
| 20 | "Hacer la demanda mensual." | Agregar la demanda a nivel **mensual** en lugar de (o además de) trabajar con franjas de 30 minutos por tipo de día. |

Referencia visual de la estructura de dummies propuesta por el profesor en la pizarra:

```
 Fecha      | va  | vn  | DUMMY_1 (Irrenunciable) | DUMMY_2 (Renunciable)
------------|-----|-----|-------------------------|----------------------
 Lun normal |  …  |  …  |           0             |          0
 Mar normal |  …  |  …  |           0             |          0
 ...        |     |     |                         |
 Feriado    |  …  |  …  |           1             |          0
 Irrenunc.  |     |     |                         |
 ...        |     |     |                         |
 Feriado    |  …  |  …  |           0             |          1
 Renunc.    |     |     |                         |
```

---

## Evaluación de cada recomendación

### R1. Filtrar solo días lunes a viernes (descartar sábado y domingo)

**Estado actual:** El panel usa la columna `tipo_dia` con tres categorías: `LABORAL`, `SABADO`, `DOMINGO`. Los datos de Subidas del DTPM ya vienen promediados por tipo de día para una semana de referencia dentro de cada corte.

**Impacto:**
- Reduce la complejidad del análisis y focaliza en la demanda más predecible y de mayor volumen (días hábiles).
- Elimina la variabilidad de fines de semana, que el modelo anterior detectó como fuente de mayor error (fila 16 del Excel: "Domingo genera mayor error").
- Pasar de ~9.216 celdas comunales a ~3.072 (un tercio del total).

**Viabilidad:** ✅ Alta. Es un filtro directo sobre `tipo_dia == "LABORAL"`. Si se trabaja con datos diarios de Etapas, es filtrar por `dayofweek < 5`.

**Decisión a tomar:**
- Si se usa el panel actual de Subidas: filtrar `tipo_dia == "LABORAL"`.
- Si se reconstruye desde las tablas de Etapas (datos diarios): filtrar las fechas que caigan de lunes a viernes, lo cual permite trabajar con la granularidad diaria necesaria para las dummies de feriados.

> [!IMPORTANT]
> Para que las dummies de feriados (R2) tengan sentido, se necesitan datos con fecha individual (diarios), no promedios por tipo de día. Esto implica reconstruir la serie desde las tablas de **Etapas**, no desde los promedios de **Subidas**.

---

### R2. Dummies de feriados irrenunciables y renunciables

**Concepto:** En Chile, los feriados se dividen en dos categorías legales:

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| **Irrenunciable** | El trabajador no puede trabajar; el comercio cierra obligatoriamente. Efecto similar a un domingo. | 1 de enero, 1 de mayo, 18-19 de septiembre, 25 de diciembre |
| **Renunciable** | El trabajador puede pactar trabajar; el comercio puede abrir. Efecto intermedio entre laboral y feriado irrenunciable. | Viernes Santo, 12 de octubre, 1 de noviembre, 8 de diciembre |

**Estructura propuesta (según la pizarra):**

```
DUMMY_1 (feriado_irrenunciable): 1 si el día es feriado irrenunciable, 0 en caso contrario.
DUMMY_2 (feriado_renunciable):   1 si el día es feriado renunciable, 0 en caso contrario.
```

Cuando ambas dummies son 0, es un día laboral normal. Las dummies son mutuamente excluyentes (un día no puede ser irrenunciable y renunciable a la vez).

**Feriados legales de Chile a considerar:**

| Fecha | Nombre | Tipo |
|-------|--------|------|
| 1 de enero | Año Nuevo | Irrenunciable |
| Viernes Santo | (variable) | Renunciable |
| Sábado Santo | (variable) | Renunciable |
| 1 de mayo | Día del Trabajo | Irrenunciable |
| 21 de mayo | Glorias Navales | Renunciable |
| 20 de junio | Día Nac. de los Pueblos Indígenas | Renunciable |
| 16 de julio | Virgen del Carmen | Renunciable |
| 15 de agosto | Asunción de la Virgen | Renunciable |
| 18 de septiembre | Fiestas Patrias | Irrenunciable |
| 19 de septiembre | Glorias del Ejército | Irrenunciable |
| 12 de octubre | Encuentro de Dos Mundos | Renunciable |
| 31 de octubre | Día de las Iglesias Evangélicas | Renunciable |
| 1 de noviembre | Día de Todos los Santos | Renunciable |
| 8 de diciembre | Inmaculada Concepción | Renunciable |
| 25 de diciembre | Navidad | Irrenunciable |

> [!NOTE]
> Algunos feriados tienen reglas especiales (ej. se mueven al lunes más cercano). Para los datos históricos, se debe verificar el calendario real de cada año. Se puede usar la librería `holidays` de Python con `holidays.Chile()` que ya incluye esta lógica.

**Viabilidad:** ✅ Alta, pero **requiere datos diarios** (con fecha), no promedios por tipo de día. Las tablas de Etapas tienen fecha individual y permiten esta identificación.

---

### R3. Hacer la demanda mensual

**Concepto:** Agregar la demanda a nivel mensual, en lugar de (o complementariamente a) las franjas de 30 minutos por tipo de día.

**Impacto:**
- Simplifica enormemente el análisis: de 48 franjas × 3 tipos de día = 144 combinaciones por comuna/corte, a **1 valor mensual** por comuna.
- Permite construir una serie temporal mensual más larga si se integran más cortes.
- Es más interpretable para la feria: "¿cuánta gente sube al bus en un mes en tal sector?".

**Viabilidad:** ✅ Alta. Se suma `subidas_promedio` ponderando por la cantidad de días de cada tipo en el mes, o directamente desde datos diarios de Etapas.

**Decisión a tomar:**
- ¿Reemplaza al análisis por franja, o se hace adicionalmente?
- ¿Se mantiene la desagregación por comuna o se trabaja solo a nivel sector?

---

## Plan de Ejecución

### Fase 0: Preparación de datos diarios

> [!WARNING]
> Las tres recomendaciones convergen en un cambio de granularidad: pasar de **promedios semanales por tipo de día** (panel de Subidas actual) a **datos diarios** (tablas de Etapas). Este es el paso más crítico y del que dependen las demás tareas.

- [ ] **0.1** Inventariar los CSV de Etapas disponibles en `Datos/Fuentes/Etapas/Utiles/` y confirmar qué períodos cubren con fechas individuales.
- [ ] **0.2** Definir el pipeline de lectura y limpieza de las tablas de Etapas:
  - Filtrar por modo BUS.
  - Mantener las comunas de Oriente y Sur ya definidas.
  - Preservar la fecha individual (`fecha`) como índice temporal.
- [ ] **0.3** Construir un panel diario con la estructura:

```
fecha | comuna | sector | subidas | media_hora (opcional) | feriado_irrenunciable | feriado_renunciable | dia_semana
```

- [ ] **0.4** Validar el panel diario contra los promedios del panel actual de Subidas como control de consistencia.

### Fase 1: Filtro lunes a viernes (R1)

- [ ] **1.1** Filtrar el panel diario para conservar solo `dia_semana` ∈ {0, 1, 2, 3, 4} (lunes a viernes en Python).
- [ ] **1.2** Documentar cuántos registros se descartan y verificar la distribución resultante.
- [ ] **1.3** Generar estadísticas descriptivas del panel filtrado vs. el original para confirmar el impacto.

### Fase 2: Variables dummy de feriados (R2)

- [ ] **2.1** Instalar o importar la librería `holidays`:
  ```bash
  pip install holidays
  ```
- [ ] **2.2** Generar el calendario de feriados chilenos para los años relevantes (2022-2026) usando `holidays.Chile()`.
- [ ] **2.3** Clasificar cada feriado como irrenunciable o renunciable según la ley chilena.
  - La librería `holidays` lista los feriados pero no siempre distingue el tipo. Puede requerirse un mapeo manual complementario.
- [ ] **2.4** Crear las dos columnas dummy en el panel diario:
  ```python
  df['feriado_irrenunciable'] = df['fecha'].apply(es_irrenunciable).astype(int)
  df['feriado_renunciable']   = df['fecha'].apply(es_renunciable).astype(int)
  ```
- [ ] **2.5** Verificar que las dummies sean mutuamente excluyentes y que los días con dummy = 1 que caen en fin de semana ya fueron excluidos en la Fase 1.
- [ ] **2.6** Análisis exploratorio: comparar la demanda promedio en días normales vs. feriados irrenunciables vs. feriados renunciables.

### Fase 3: Demanda mensual (R3)

- [ ] **3.1** Agregar el panel diario (ya filtrado lun-vie) a nivel mensual:
  ```python
  df_mensual = df.groupby(['año_mes', 'sector', 'comuna'])['subidas'].sum().reset_index()
  ```
- [ ] **3.2** Generar la serie temporal mensual por sector y/o comuna.
- [ ] **3.3** Visualizar tendencia y estacionalidad de la demanda mensual.
- [ ] **3.4** Evaluar si se puede construir un modelo de pronóstico mensual (ej. media móvil, suavizamiento exponencial, o regresión con las dummies como predictoras).

### Fase 4: Modelado con dummies (integración R1+R2+R3)

- [ ] **4.1** Especificar el modelo de regresión con las dummies:
  ```
  Subidas_diarias ~ β₀ + β₁·feriado_irrenunciable + β₂·feriado_renunciable + controles
  ```
- [ ] **4.2** Estimar el modelo y evaluar la significancia de los coeficientes de las dummies.
- [ ] **4.3** Interpretar: ¿cuántas subidas menos (o más) hay en un feriado irrenunciable vs. un día normal? ¿Y en uno renunciable?
- [ ] **4.4** Comparar el desempeño de este modelo con el modelo anterior (media histórica) usando WAPE o MAE.

### Fase 5: Preparación para la feria

- [ ] **5.1** Preparar visualizaciones claras del efecto de feriados sobre la demanda.
- [ ] **5.2** Integrar los resultados en el póster/presentación de la feria.
- [ ] **5.3** Documentar las mejoras respecto a la etapa anterior.
- [ ] **5.4** Preparar el notebook final reproducible con todo el pipeline.

---

## Dependencias y riesgos

| Riesgo | Mitigación |
|--------|------------|
| Las tablas de Etapas no cubren todos los períodos necesarios | Usar los períodos disponibles; documentar la cobertura real |
| La librería `holidays` no distingue irrenunciable/renunciable | Crear un diccionario manual con la clasificación legal |
| Pocos feriados caen en días lunes-viernes dentro de los datos | Documentar la limitación; el efecto puede no ser estadísticamente significativo con pocos datos |
| El cambio de granularidad (semanal → diario) introduce inconsistencias | Validar cruzadamente contra los promedios ya conocidos |

---

## Archivos esperados en `Etapa_04/`

```
Etapa_04/
├── codigo/
│   ├── construir_panel_diario.py      # Fase 0: lee Etapas y construye panel diario
│   ├── clasificar_feriados.py         # Fase 2: genera dummies de feriados
│   ├── agregar_mensual.py             # Fase 3: agrega a nivel mensual
│   └── modelo_con_dummies.py          # Fase 4: modelo con variables dummy
├── datos/
│   ├── panel_diario_lun_vie.csv       # Panel filtrado lunes a viernes
│   ├── feriados_chile.csv             # Catálogo de feriados con clasificación
│   └── demanda_mensual.csv            # Serie mensual agregada
├── resultados/
│   ├── analisis_efecto_feriados.csv   # Comparación demanda normal vs. feriados
│   └── modelo_dummies_metricas.csv    # Métricas del modelo con dummies
├── recomendaciones/
│   ├── recomendaciones.jpeg           # Captura del Excel del profesor
│   └── modelo_tablas.jpeg             # Captura de la pizarra (estructura dummies)
├── plan_recomendaciones_profesor.md   # Este archivo
└── README.md
```

---

## Prioridad sugerida de ejecución

1. **Fase 0** es bloqueante — sin datos diarios no se pueden hacer las dummies ni el filtro real por día de semana.
2. **Fase 1** es trivial una vez que se tiene la Fase 0.
3. **Fase 2** es el aporte más valioso para la feria: demuestra conocimiento de dominio (leyes laborales chilenas) y técnica (codificación dummy).
4. **Fase 3** es independiente y puede hacerse en paralelo con la Fase 2.
5. **Fases 4 y 5** integran todo para la presentación final.
