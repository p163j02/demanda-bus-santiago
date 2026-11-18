# Etapa III: guía de estudio, resultados y defensa

## Cómo estudiar esta guía

Para comprender primero la historia, lee las secciones 1, 2 y 12. Para aprender la materia, estudia las secciones 3 a 11. Las secciones finales explican las limitaciones, las preguntas de defensa y el cierre de la presentación.

Las explicaciones sencillas usan ejemplos inventados. Las tablas de resultados, en cambio, corresponden a experimentos ejecutados y verificados.

**Versión de referencia:** rama `origin/etapa-03-final`, hasta el commit `038dd06`, incluyendo la ampliación de 2023 de `f03ab66`. El PDF enviado por el compañero tiene 17 láminas. El `main` revisado todavía no incorpora esos dos commits: algunos archivos nuevos mencionados aquí pertenecen a la rama final y no están disponibles en ese `main`.

## 1. El proyecto explicado en un minuto

Queremos pronosticar la suma de subidas registradas de buses en dos sectores de Santiago, Oriente y Sur, según el tipo de día y la franja de treinta minutos.

En la etapa II construimos una base, estudiamos perfiles horarios y calculamos primeros pronósticos. En la etapa III auditamos esa base, reprodujimos los resultados, comparamos métodos, ajustamos parámetros, analizamos incertidumbre y probamos si incorporar antecedentes laborales de 2023 mejoraba el desempeño.

Con el historial original, la media histórica obtuvo el menor error de la comparación inicial. Después de ampliar el historial, Gradient Boosting obtuvo el menor WAPE total de las variantes evaluadas: **6,66 %**, frente a **6,95 %** de la media histórica. La mejora se concentra en laborales: **3,35 %**, frente a **4,79 %**.

La selección es provisional. La ventaja global es pequeña, su intervalo bootstrap incluye cero y noviembre de 2025 se reutilizó para ajustar parámetros y evaluar. Los domingos siguen siendo difíciles.

### Explicación sencilla

Imagina que quieres saber cuántos niños subirán al bus del colegio a las 7:00. Primero miras lo que ocurrió antes. Puedes copiar el último número, sacar un promedio o usar un programa que corrija ese promedio según la hora y el tipo de día.

En esta etapa probamos esas ideas con datos ya conocidos, pero ocultándolos al momento de construir cada pronóstico. También incorporamos información más antigua y comprobamos qué método la aprovecha mejor.

### Frase para decir en la presentación

> "El avance fue pasar de primeros pronósticos a una comparación reproducible de métodos, y comprobar cómo cambia el resultado al ampliar el historial."

## 2. Qué se hizo y en qué mejoró respecto de la etapa II

| Trabajo de etapa III | Qué significa | Mejora concreta |
|---|---|---|
| Auditoría del panel | Revisar claves, valores, cobertura y marcas de ausencia | Evita evaluar registros duplicados o confundir faltantes con ceros reales. |
| Reproducción de etapa II | Volver a calcular predicciones, métricas y matriz | Comprueba que la referencia anterior se conserva. |
| Comparación de cuatro métodos | Evaluar media, último observado, Ridge y Gradient Boosting | Permite justificar la elección con resultados. |
| Evaluación temporal | Usar antecedentes anteriores al corte objetivo | Evita que el pronóstico conozca directamente su respuesta. |
| Desglose del error | Revisar sectores, cortes, tipos de día y bloques horarios | Impide esconder un problema local detrás de un promedio total. |
| Bootstrap pareado | Remuestrear las mismas franjas para todos los métodos | Estima incertidumbre en las diferencias observadas. |
| Ajuste de hiperparámetros | Comparar configuraciones usando validación | Mejora Gradient Boosting en abril de 2026 respecto de la configuración inicial. |
| Importancia por permutación | Desordenar una variable y observar el deterioro | Ayuda a interpretar qué información utiliza el modelo ajustado. |
| Sensibilidad de etiquetas | Mover umbrales ±10 % y ±20 % | Muestra cuánto dependen las categorías de sus fronteras. |
| Incorporación laboral de 2023 | Adaptar tres publicaciones antiguas | Aumenta los antecedentes laborales sin inventar fines de semana. |
| Selección de un modelo común | Evaluar una misma receta para sectores y tipos de día | Gradient Boosting ampliado obtiene el menor WAPE total evaluado. |
| Entrega | Notebook, CSV, gráficos y presentación | Facilita revisar y explicar el procedimiento, aunque queda un fallo de ejecución limpia del notebook. |

El proyecto mejoró en calidad del análisis y en desempeño laboral. Eso no significa que todos los modelos mejoraran ni que cada tipo de día quedara resuelto.

## 3. Qué representan los datos

### 3.1. Objetivo y unidad de observación

El objetivo es la **suma sectorial de `Subidas_Promedio`**. Los datos describen perfiles promedio publicados, no una serie continua con una fila por fecha real.

Una observación sectorial tiene cuatro identificadores:

```text
periodo + sector + tipo_dia + media_hora
```

Por ejemplo:

```text
2026-04 | Sur | LABORAL | 07:00
```

Representa el volumen promedio registrado para la franja que comienza a las 7:00 en ese sector y tipo de día, según esa publicación. No representa necesariamente un martes específico ni todos los pasajeros de abril.

Los promedios pueden tener decimales. Un valor de 100,5 no significa que subió medio pasajero: es el resultado de promediar registros.

### 3.2. Qué se puede y qué no se puede interpretar

| Sí representa | No representa por sí solo |
|---|---|
| Subidas registradas en la fuente | Pasajeros reales corregidos por evasión |
| Volumen por sector, tipo de día y franja | Personas únicas: una persona puede realizar varias subidas |
| Un perfil temporal publicado | Una serie diaria completa |
| Intensidad de subidas | Ocupación dentro de cada bus |
| Una referencia para estudiar horarios | Una decisión validada de cantidad de buses o frecuencia |

Las fichas describen registros Bips! y procesamiento con información GPS; no incluyen corrección por evasión. Las bajadas no se suman al objetivo de subidas.

### 3.3. Sectores

**Oriente, seis comunas:** Las Condes, Vitacura, Lo Barnechea, Providencia, La Reina y Ñuñoa.

**Sur, diez comunas:** La Cisterna, El Bosque, San Bernardo, La Pintana, San Ramón, San Miguel, La Granja, San Joaquín, Pedro Aguirre Cerda y Lo Espejo.

La selección no cubre toda la Región Metropolitana. El panel general incluye 36 comunas, pero el análisis sectorial utiliza estas 16.

### 3.4. Cortes y tipos de día

Historial original:

- Noviembre de 2024: `2024-11`.
- Abril de 2025: `2025-04`.
- Noviembre de 2025: `2025-11`.
- Abril de 2026: `2026-04`.

Cada corte tiene tres tipos de día: `LABORAL`, `SABADO` y `DOMINGO`, y 48 franjas de treinta minutos, desde `00:00` hasta `23:30`.

Ampliación: abril, agosto y noviembre de 2023, **solo laborales**. Sábados y domingos siguen comenzando en noviembre de 2024.

### 3.5. Cómo leer los conteos

| Conteo | Cálculo o significado |
|---|---|
| 20.736 celdas del panel general | 36 comunas × 4 cortes × 3 tipos de día × 48 franjas |
| 9.216 celdas comunales de los sectores | 16 × 4 × 3 × 48 |
| 1.152 agregados sectoriales originales | 2 sectores × 4 cortes × 3 tipos de día × 48 |
| 427 celdas ausentes en los sectores | Combinaciones que se rellenaron con cero y quedaron marcadas como ausentes |
| 83 ceros comunales observados | Registros presentes cuyo valor publicado es cero |
| 576 franjas posibles de prueba conjunta | 2 sectores × 2 cortes evaluados × 3 tipos de día × 48 |
| 505 franjas evaluables comunes | Objetivos completos y con historial utilizable |
| 172 laborales, 168 sábados, 165 domingos | Descomposición de las 505 franjas |

**505 no es el número de días, buses ni personas.** Es el número de combinaciones sectoriales evaluadas por cada método.

Hay 71 franjas posibles excluidas de la prueba conjunta: 66 objetivos incompletos y cinco objetivos completos sin historial completo. No se cuentan dos veces.

## 4. Calidad de datos: ausencias, ceros y cobertura

### 4.1. Un cero real no equivale a un dato ausente

- Cero observado: existe el registro y su valor es cero.
- Ausencia: no existe esa combinación en el panel observado.
- `relleno_cero = 1`: se añadió una celda para completar la rejilla, pero su cero no debe interpretarse como actividad nula.
- `relleno_cero = 0`: el registro estaba presente, incluso si su valor era cero.

Al preparar los experimentos ampliados, el código vuelve a tratar los ceros añadidos como ausencias.

**Ejemplo sencillo:** si una lista dice que Ana tiene cero lápices, conocemos su cantidad. Si Ana no aparece en la lista, no sabemos cuántos tiene. Escribir cero en su casillero para completar la tabla no hace verdadera esa respuesta.

### 4.2. Cobertura sectorial

Un agregado sectorial se considera completo cuando hay un valor para cada comuna del sector en esa franja.

```text
comunas_ausentes = 0  →  cobertura_completa = True
```

Si falta una comuna, no se usa la suma parcial como objetivo completo. Si Oriente tiene seis comunas y falta una, sumar las otras cinco puede subestimar el volumen por falta de información, no por desempeño del modelo.

**Límite:** esta cobertura es comunal. Tener algún valor en todas las comunas no certifica que estén observados todos sus servicios o paraderos.

### 4.3. Controles de la auditoría

`base_reproducible.py` comprueba:

1. Claves únicas, sin duplicados.
2. Rejilla exacta de comunas, cortes, días y franjas.
3. Valores finitos y no negativos.
4. Marcas de ausencia binarias: cero o uno.
5. Correspondencia de esas marcas con las claves ausentes del panel observado.
6. Conservación de los valores publicados en las celdas presentes.
7. Correspondencia de predicciones y métricas con la etapa II.
8. Uso de antecedentes anteriores al objetivo.

**Valores finitos** excluye infinito y valores numéricos indefinidos. **Clave única** significa que una misma combinación no puede aparecer dos veces.

### 4.4. Participación diaria

```text
participacion_diaria_pct = 100 × volumen de la franja / volumen diario del perfil
```

Sirve para estudiar qué proporción del perfil corresponde a cada horario. En etapa III se deja vacía si falta alguna franja del día: no se presenta una participación aparentemente completa usando un total parcial.

Los gráficos también deben dejar interrupciones en los datos ausentes, en lugar de unirlos como si fueran ceros observados.

## 5. Cómo funciona el pronóstico

El flujo es:

```text
Panel comunal auditado
    → selección de 16 comunas
    → agregación sectorial con control de cobertura
    → antecedentes anteriores por sector, tipo de día y franja
    → variables históricas y de contexto
    → pronósticos de referencia y modelos ajustados
    → evaluación sobre las mismas claves
    → análisis de error e incertidumbre
```

### 5.1. Media histórica

Promedia los valores anteriores completos de la misma combinación de sector, tipo de día y franja.

```text
prediccion = suma de antecedentes completos / número de antecedentes completos
```

Ejemplo: valores anteriores 100, 120 y 110. El pronóstico es 110.

Es un **baseline** o método de referencia: una solución sencilla que un método más complejo debe justificar que supera.

Ventaja: combina antecedentes y es fácil de explicar. Limitación: da igual peso a publicaciones antiguas y recientes; puede quedar rezagada si cambian los niveles de subidas.

### 5.2. Último observado

Usa el antecedente completo más reciente de esa combinación.

Con 100, 120 y 110, predice 110. Si el último fuera 150, predice 150 aunque el promedio sea menor.

Ventaja: reacciona al nivel reciente. Limitación: depende mucho de un único antecedente y puede copiar una fluctuación.

Si solo existe un antecedente, la media y el último observado coinciden. Por eso empatan en el primer corte pronosticado; no demuestra equivalencia general.

### 5.3. Ridge

Es una regresión lineal regularizada. Combina variables mediante coeficientes y penaliza coeficientes demasiado grandes.

Una forma simplificada de su función de entrenamiento es:

```text
error cuadrático + alpha × suma de cuadrados de los coeficientes
```

- Un coeficiente controla cuánto cambia la respuesta al cambiar una variable, manteniendo las otras constantes.
- `alpha` controla la penalización.
- Una penalización mayor limita ajustes extremos, pero no garantiza mejor desempeño.

**Explicación sencilla:** Ridge arma una receta con varios ingredientes y evita echar cantidades exageradas de uno solo para acertar una prueba particular.

El experimento inicial usa `RidgeCV` con 20 valores de `alpha`, entre 0,001 y 100. Su selección interna predeterminada utiliza validación dejando una observación fuera, no una partición temporal interna. Se aplica únicamente a las filas anteriores al corte externo, pero esa selección interna no representa una nueva publicación futura independiente.

El ajuste temporal posterior compara cinco valores y selecciona `alpha = 10`; los experimentos nuevos utilizan ese valor fijo.

El código no incorpora un escalador adicional de variables. La transformación logarítmica comprime los volúmenes, pero no equivale a estandarizar todas las variables.

### 5.4. Gradient Boosting

La implementación es `HistGradientBoostingRegressor`. Construye árboles pequeños de manera secuencial. Cada árbol intenta corregir parte del error de la combinación anterior.

Un árbol divide observaciones mediante reglas, por ejemplo según tipo de día o valor histórico. Estas son ilustraciones: no son reglas extraídas del modelo final.

**Explicación sencilla:** haces un primer dibujo y varios compañeros van corrigiendo pequeños errores. El resultado acumula esas correcciones.

Puede aprender relaciones no lineales e interacciones. Una relación no lineal no tiene que aumentar siempre en la misma proporción; una interacción significa que el efecto de una variable depende de otra.

Por ejemplo, el efecto de la hora puede ser distinto en un laboral y en un domingo. Esa flexibilidad también puede sobreajustar si hay pocos antecedentes.

### 5.5. Qué aprenden realmente Ridge y Gradient Boosting

Los modelos no aprenden directamente el volumen bruto. Aprenden una corrección logarítmica de la media histórica:

```text
r = log(1 + observado) − log(1 + media_historica)
```

Después reconstruyen el pronóstico:

```text
prediccion = exp(log(1 + media_historica) + correccion_predicha) − 1
prediccion = máximo(prediccion, 0)
```

- Corrección cero: se conserva la media histórica.
- Corrección positiva: el pronóstico sube.
- Corrección negativa: el pronóstico baja.

`log1p(x)` calcula `log(1+x)`. Evita el problema de `log(0)` y comprime diferencias de escala. `expm1(x)` calcula `exp(x)-1`, la transformación inversa.

Esto se parece a una corrección multiplicativa sobre `1 + media`, no a sumar directamente una cantidad fija de subidas.

Los estimadores utilizados ajustan el error cuadrático de esa respuesta logarítmica. **WAPE se usa para evaluar y elegir configuraciones; no es la función que optimizan directamente durante el entrenamiento.**

No se calculó una corrección adicional del sesgo al volver del logaritmo. Entrenar en logaritmos no garantiza un pronóstico sin sesgo en la escala original.

### 5.6. Qué significa "modelo único"

La misma receta aprende con observaciones de ambos sectores y los tres tipos de día, usando variables que distinguen esos contextos.

No significa que todas las franjas reciban la misma predicción. Tampoco que un modelo entrenado con abril de 2026 se usara para pronosticar noviembre de 2025.

El código vuelve a ajustar el estimador para cada corte usando su pasado disponible. Lo seleccionado es una configuración común; el experimento no demuestra por sí solo que exista un modelo desplegado o un archivo serializado listo para producción.

## 6. Variables de entrada del modelo

| Variable | Definición | Interpretación sencilla |
|---|---|---|
| `media` | Promedio de antecedentes completos de la combinación | Lo habitual hasta ese momento |
| `ultimo` | Último antecedente completo | Lo que ocurrió en la publicación más reciente |
| `log_media` | `log1p(media)` | La media en una escala comprimida |
| `log_ultimo` | `log1p(ultimo)` | El último valor en esa escala |
| `hora_sin` | `sin(2π × minutos / 1440)` | Primera coordenada del reloj |
| `hora_cos` | `cos(2π × minutos / 1440)` | Segunda coordenada del reloj |
| `temporada_nov` | Uno si el corte termina en noviembre; cero si no | Indicador de noviembre, no una descripción completa de estación |
| `sector_sur` | Uno para Sur; cero para Oriente | Identifica el sector |
| `dia_LABORAL` | Uno si es laboral; cero si no | Identifica laborales |
| `dia_SABADO` | Uno si es sábado; cero si no | Identifica sábados |
| `dia_DOMINGO` | Uno si es domingo; cero si no | Identifica domingos |
| `n_hist` / `n_antecedentes` | Cantidad de antecedentes completos disponibles | Cuántos recuerdos utilizables hay |

Los nueve predictores son los dos logaritmos, las dos coordenadas horarias, el indicador de noviembre, el sector y los tres indicadores de día. El experimento exclusivamente laboral usa seis: omite los tres indicadores de día porque todos sus registros son laborales.

`media` se utiliza además para reconstruir el pronóstico. `n_hist` se registra para revisar cobertura, pero **no está incluido como predictor** en la lista de variables de los modelos nuevos.

### 6.1. Por qué representar la hora con seno y coseno

Una hora numérica puede hacer que 23:30 y 00:00 parezcan lejanas, aunque son consecutivas. Seno y coseno ubican la hora en un círculo de 24 horas.

```text
minutos = 60 × hora + minuto
ángulo = 2π × minutos / 1440
```

Ejemplos aproximados:

| Hora | `hora_sin` | `hora_cos` |
|---|---:|---:|
| 00:00 | 0 | 1 |
| 06:00 | 1 | 0 |
| 12:00 | 0 | −1 |
| 18:00 | −1 | 0 |

**Para un niño:** usamos un reloj redondo para que el programa entienda que, después de la noche, vuelve la madrugada.

### 6.2. Indicadores binarios

Los indicadores valen cero o uno. Un sábado tiene:

```text
dia_LABORAL = 0
dia_SABADO = 1
dia_DOMINGO = 0
```

Se llaman variables indicadoras o codificación *one-hot*. Evitan asignar un orden artificial como laboral=1, sábado=2 y domingo=3.

### 6.3. Qué no contienen estos modelos

No incorporan clima, feriados individuales, eventos masivos, población, oferta de buses, frecuencias, capacidad, ocupación, evasión ni número de paraderos. No pueden atribuir causalmente una diferencia a esas variables.

`temporada_nov` distingue noviembre frente a otros meses. Como agosto solo aparece en 2023, ese indicador no modela toda la estacionalidad anual.

## 7. Entrenamiento, validación y prueba

### 7.1. Las tres funciones

- **Entrenamiento:** datos que el modelo usa para aprender sus parámetros.
- **Validación:** datos para comparar configuraciones y elegir hiperparámetros.
- **Prueba:** datos reservados para evaluar la configuración elegida.

**Ejemplo sencillo:** estudias ejercicios, pruebas distintas formas de resolverlos y finalmente rindes un examen. Si eliges tu método mirando las respuestas del examen, ese examen deja de ser independiente.

### 7.2. Origen móvil

La comparación original usa:

| Corte evaluado | Filas objetivo utilizadas para entrenar ML |
|---|---|
| Noviembre de 2025 | Abril de 2025: 250 observaciones evaluables |
| Abril de 2026 | Abril y noviembre de 2025: 503 observaciones evaluables |

Noviembre de 2024 sirve como antecedente para construir variables de abril de 2025. No se utiliza como fila supervisada inicial porque carece de historia anterior en el panel original.

Al avanzar al siguiente corte, crece el conjunto de entrenamiento. Esto se llama evaluación de origen móvil o *rolling origin*.

Las franjas de una misma publicación están correlacionadas. Tener cientos de filas no equivale a tener cientos de fechas independientes.

### 7.3. Fuga temporal

Hay fuga cuando información que no estaría disponible al pronosticar se utiliza para construir el modelo o sus variables.

Ejemplo: incluir abril de 2026 al calcular la media usada para pronosticar abril de 2026.

Las comprobaciones ejecutadas muestran que alterar valores del objetivo y posteriores no modifica sus variables históricas. Los umbrales de etiquetas también se calculan con antecedentes anteriores.

**Eso no resuelve la reutilización de noviembre para elegir hiperparámetros:** son controles de variables históricas, no una certificación de independencia de toda la selección.

### 7.4. Evaluación retrospectiva

Abril de 2026 ya estaba disponible durante el desarrollo. Se simula cómo se habría pronosticado utilizando el pasado, pero el equipo ya podía observar ese resultado.

Por eso se debe decir "evaluación retrospectiva". Una prueba futura más fuerte exigiría congelar la receta antes de recibir una nueva publicación.

## 8. Hiperparámetros, regularización y sobreajuste

Los parámetros se aprenden, como los coeficientes de Ridge o las divisiones de árboles. Los hiperparámetros se eligen, como la penalización o profundidad máxima.

### 8.1. Configuración de Gradient Boosting

| Hiperparámetro | Inicial | Ajustado y usado en los experimentos nuevos | Significado |
|---|---:|---:|---|
| `max_depth` | 3 | 2 | Máxima profundidad de un árbol |
| `learning_rate` | 0,05 | 0,03 | Tamaño del aporte de cada corrección |
| `max_iter` | 200 | 100 | Máximo de iteraciones de boosting |
| `min_samples_leaf` | 10 | 10 | Mínimo de observaciones en una hoja |
| `random_state` | 0 | 0 | Semilla para reproducibilidad |

Una hoja es una región final de un árbol. Un mínimo de diez observaciones evita construir hojas basadas en muy pocos registros.

Una tasa de aprendizaje de 0,03 **no significa 3 % de acierto**. Cien iteraciones **no son cien cortes de datos**. La semilla cero **no significa ausencia de incertidumbre**.

### 8.2. Búsqueda temporal

`validacion_robustez.py`:

1. Entrena con abril de 2025.
2. Compara configuraciones en noviembre de 2025.
3. Selecciona la de menor WAPE de validación.
4. Reentrena con abril y noviembre de 2025.
5. Evalúa en abril de 2026.

Para Ridge compara `alpha` 0,01; 0,1; 1; 10; 100. Para Gradient Boosting compara 12 combinaciones: tres profundidades × dos tasas de aprendizaje × dos cantidades de iteraciones.

### 8.3. Sobreajuste

Ocurre cuando el modelo aprende particularidades de la muestra que no se mantienen en nuevas observaciones.

**Para un niño:** memorizar las respuestas de diez ejercicios puede ayudarte a repetirlos, pero no garantiza resolver el ejercicio once.

Regularización y árboles pequeños limitan esa flexibilidad. No eliminan por sí solos el problema de tener pocos cortes independientes.

## 9. Métricas: qué mide cada número

Usamos el error firmado:

```text
e = prediccion − observado
```

Positivo significa sobreestimación; negativo, subestimación.

### 9.1. WAPE

Error absoluto porcentual ponderado:

```text
WAPE = 100 × suma(|prediccion − observado|) / suma(observado)
```

Ejemplo: valores reales 100 y 200; pronósticos 110 y 180. El error absoluto total es 10+20=30 y el volumen real es 300. WAPE=10 %.

**Para un niño:** juntas cuánto te equivocaste, sin permitir que un error hacia arriba borre otro hacia abajo, y lo comparas con todo lo que realmente ocurrió.

Un WAPE de 6,66 % significa que la suma de errores absolutos equivale al 6,66 % del volumen observado del conjunto evaluado.

No significa que el 93,34 % de los pronósticos sea correcto, que cada franja tenga 6,66 % de error ni que ese sea el error garantizado del próximo corte.

#### WAPE total y subgrupos

El total se calcula sumando errores y volúmenes. No es el promedio simple de los WAPE por tipo de día.

Los grupos con mayor volumen pesan más. Por eso el 19,77 % de domingos puede coexistir con un total de 6,66 %.

Si el volumen observado total de un grupo es cero, WAPE no se puede calcular: se reporta como no evaluable, no como cero error.

WAPE está emparentado con MAPE, pero no divide el error de cada fila por su propio observado. Esto evita la división individual por cero. Una franja de cero observado puede aportar error al numerador si el total del grupo es positivo.

### 9.2. MAE

Error absoluto medio:

```text
MAE = suma(|e|) / n
```

Con errores absolutos 10 y 20, MAE=15. Se interpreta en la unidad original del objetivo.

El MAE de 472,01 de la media histórica corresponde a subidas promedio agregadas por franja sectorial. No significa 472 personas únicas por bus.

### 9.3. RMSE

Raíz del error cuadrático medio:

```text
RMSE = raíz(suma(e²) / n)
```

Elevar errores al cuadrado da mayor peso a equivocaciones grandes. Con errores 10 y 20, RMSE≈15,81.

MAE y RMSE responden preguntas distintas. Un método puede ganar en RMSE y perder ligeramente en WAPE. El criterio principal de estos experimentos fue WAPE.

### 9.4. Sesgo porcentual

```text
sesgo_pct = 100 × suma(e) / suma(observado)
```

- Positivo: exceso neto de pronóstico.
- Negativo: déficit neto.
- Cerca de cero: errores hacia arriba y abajo pueden compensarse.

Predecir 150 en una franja real de 100 y 50 en otra real de 100 produce sesgo cero, pero WAPE=50 %. **Sesgo cero no implica precisión.**

La media histórica inicial tiene sesgo −1,84 %. El Gradient Boosting ampliado del experimento final tiene aproximadamente −3,06 %, calculado en la verificación adicional. El sesgo final no figura como columna de `modelo_unico.csv`.

### 9.5. Coincidencia de etiquetas

```text
acierto_etiqueta_pct = 100 × etiquetas coincidentes / n
```

Mide si el observado y la predicción caen en la misma categoría de intensidad. No mide igualdad del volumen.

Dos números bastante diferentes pueden pertenecer a "Alto". Dos números casi iguales pueden quedar a lados distintos de un umbral.

### 9.6. Detección de altos

```text
recall_alto = 100 × altos_detectados / altos_reales
```

La media histórica inicial detecta 159 de 166 altos reales: 95,78 %. Eso es sensibilidad o *recall*, no precisión de la clase Alto.

La precisión de Alto requeriría dividir los altos correctamente detectados por **todos los pronosticados como Alto**. Esa cantidad no se obtiene solo con 159/166.

### 9.7. Subestimación de altos

```text
subestimacion_altos_pct =
    100 × suma(máximo(observado − prediccion, 0) en altos reales)
        / suma(observado en altos reales)
```

Mide el déficit de pronóstico en franjas realmente altas sin compensarlo con excesos. Una detección alta de categorías no garantiza ausencia de déficit de volumen.

### 9.8. Puntos porcentuales y mejora relativa

De 6,95 % a 6,66 %:

- Reducción absoluta: aproximadamente **0,29 puntos porcentuales**.
- Reducción relativa del WAPE: aproximadamente **4,19 %**.

De 4,79 % a 3,35 % en laborales:

- Reducción absoluta: aproximadamente **1,44 puntos porcentuales**.
- Reducción relativa: aproximadamente **29,98 %**.

No se debe llamar a 0,29 puntos una reducción de 29 %.

## 10. Etiquetas, terciles y matriz de confusión

### 10.1. Qué son los terciles

Se calculan dos umbrales, `q1` y `q2`, correspondientes a los percentiles 33,33 y 66,67 de valores históricos positivos y completos.

Se utiliza el promedio por comuna:

```text
promedio_por_comuna = subidas_sector / n_comunas
```

Esto divide por seis en Oriente y por diez en Sur. **No ajusta por población, tamaño territorial ni cantidad de paraderos.**

### 10.2. Reglas de clasificación

| Condición | Etiqueta |
|---|---|
| Falta una comuna | Sin dato completo |
| Valor completo igual a cero | Nulo |
| `0 < valor <= q1` | Bajo |
| `q1 < valor <= q2` | Medio |
| `valor > q2` | Alto |
| No existe historial para predecir | Sin historial, para el pronóstico |

No se entrena un clasificador independiente. Primero se pronostica una cantidad y después se le asigna una etiqueta.

Los umbrales se recalculan con historia anterior al corte:

| Corte | `q1` | `q2` |
|---|---:|---:|
| Noviembre de 2025 | 392,40 | 962,36 |
| Abril de 2026 | 392,16 | 962,52 |

Son subidas promedio por comuna, no totales sectoriales. Un valor exactamente igual a `q1` es Bajo; uno igual a `q2` es Medio.

### 10.3. Qué significa Alto

Significa alto respecto de la distribución histórica utilizada para calibrar los umbrales. No significa "bus lleno", "demanda insatisfecha" ni "hay que aumentar frecuencia".

No hay agregados sectoriales nulos confirmados en el panel original auditado. La categoría Nulo existe como regla, pero su desempeño no es evaluable con esa muestra.

### 10.4. Matriz de confusión

Cruza categorías observadas y pronosticadas. La diagonal contiene coincidencias; fuera de ella hay discrepancias.

- Real Alto, predicho Medio: subclasificación.
- Real Medio, predicho Alto: sobreclasificación.

Hay que leer los nombres de los ejes antes de interpretar filas y columnas. La matriz mostrada en el PDF corresponde a la media histórica, no al Gradient Boosting final.

### 10.5. Sensibilidad de umbrales

Se multiplican `q1` y `q2` por 0,8; 0,9; 1; 1,1; 1,2. Cambian las etiquetas, pero no los pronósticos numéricos ni WAPE.

En la media histórica inicial, el acierto va aproximadamente de 90,69 % a 93,07 %; la detección de altos, de 90,60 % a 95,78 %.

Esto muestra dependencia de la clasificación respecto de sus fronteras. No es una comprobación de estabilidad temporal del modelo final.

## 11. Incertidumbre e interpretación

### 11.1. Bootstrap pareado

El bootstrap crea muestras a partir de los resultados disponibles, seleccionando observaciones con reemplazo. Una franja puede aparecer varias veces y otra no aparecer.

El procedimiento realiza **2.000 remuestreos dentro de cada corte**. Utiliza exactamente las mismas franjas remuestreadas para todos los métodos: por eso es pareado.

En cada muestra recalcula WAPE y la diferencia respecto de la media histórica.

**Para un niño:** cambias varias veces la combinación de ejercicios, pero todos los métodos reciben la misma combinación en cada ronda. Así puedes observar si la ventaja cambia mucho.

Dos mil remuestreos no agregan dos mil publicaciones nuevas. Solo reorganizan la información ya disponible.

### 11.2. Intervalo del 95 %

El código utiliza los percentiles 2,5 y 97,5 de los valores remuestreados.

Para una diferencia definida como:

```text
diferencia = WAPE_modelo − WAPE_media
```

- Negativa: favorable al modelo.
- Positiva: favorable a la media.
- Intervalo que incluye cero: la comparación no distingue claramente una ventaja bajo este procedimiento.

Un intervalo no es una garantía del error futuro. Incluir cero tampoco demuestra equivalencia entre métodos.

La cobertura nominal de 95 % depende de que el procedimiento represente adecuadamente la variabilidad. Las franjas horarias están correlacionadas y solo hay dos cortes evaluados, por lo que esta inferencia debe interpretarse con cautela.

### 11.3. La diferencia puntual y la media bootstrap

`dif_vs_media` y `dif_vs_seleccionado` almacenan la **media de las diferencias remuestreadas**. No siempre coinciden exactamente con restar los WAPE puntuales.

En el modelo final:

- Diferencia puntual: aproximadamente −0,2913 puntos.
- Media bootstrap: aproximadamente −0,3025 puntos.

No hay contradicción: son resúmenes diferentes.

`prob_mejor_que_media`, en el análisis original, es la fracción de remuestreos donde la diferencia es negativa. No es automáticamente una probabilidad de superioridad futura ni un valor p formal.

### 11.4. Importancia por permutación

Se desordena una variable en la muestra de evaluación, manteniendo las otras. Si el error aumenta, el modelo utilizaba información de esa variable.

El código repite la permutación 20 veces y evalúa el error absoluto de la respuesta residual logarítmica. Por eso las importancias **no están expresadas en puntos de WAPE**.

`importancia` es el deterioro medio del indicador; `desv` es su desviación entre permutaciones. Un valor pequeño o negativo no demuestra que la variable carezca de utilidad general: puede haber ruido o redundancia.

En el Gradient Boosting ajustado original destacan `dia_DOMINGO` y `log_ultimo`. En Ridge original destaca `log_ultimo`.

Esto describe esos modelos ajustados y esa muestra. No identifica causas y no debe atribuirse sin recalcular al Gradient Boosting final ampliado.

### 11.5. Residuos por bloque

`residuos_modelo_final.csv` conserva el análisis de **media histórica**, pese a su nombre.

Los bloques son:

- Noche 00:00–06:00.
- Punta mañana 06:00–10:00.
- Valle 10:00–17:00.
- Punta tarde 17:00–21:00.
- Noche 21:00–24:00.

`error_medio` es el promedio del error firmado, en unidades de subidas agregadas. `sesgo_pct` es su suma respecto del volumen observado; no es el promedio simple de errores porcentuales individuales.

Por ejemplo, la media histórica subestima en el bloque de tarde del Sur: sesgo cercano a −4,09 % y WAPE de 8,53 %. Son resultados del modelo de referencia, no del modelo final.

## 12. Resultados verificados: cuatro experimentos diferentes

Conviene explicar los resultados en este orden. Mezclar una configuración inicial, una ajustada y otra ampliada puede hacer que las cifras parezcan contradictorias.

### 12.1. Experimento A: comparación inicial con historial original

Antes de comparar ML, el Hito 1 reprodujo 1.728 filas de predicción de las dos referencias para abril de 2025, noviembre de 2025 y abril de 2026, sus 12 filas de métricas por sector, corte y método, y la matriz de abril de 2026. Esas 1.728 filas incluyen pronósticos no evaluables y duplican cada combinación por los dos métodos; no deben confundirse con las 505 claves únicas de la comparación posterior.

Archivo: `Etapa_03/resultados/hito_2/metricas_conjuntas.csv`.

Misma evaluación: 505 franjas de noviembre de 2025 y abril de 2026.

| Método | WAPE | MAE | Sesgo | Coincidencia de etiquetas | Altos detectados / reales |
|---|---:|---:|---:|---:|---:|
| Media histórica | **6,9541 %** | 472,01 | −1,84 % | 90,69 % | 159 / 166 |
| Ridge inicial | 7,0519 % | 478,65 | −3,18 % | **92,87 %** | 151 / 166 |
| Gradient Boosting inicial | 7,8306 % | 531,51 | −0,67 % | 87,52 % | 151 / 166 |
| Último observado | 9,1755 % | 622,79 | −1,48 % | 84,95 % | 144 / 166 |

Conclusión: la media histórica tiene el menor WAPE. Ridge coincide más en etiquetas, pero ese no era el criterio principal de selección.

La diferencia bootstrap Ridge menos media es aproximadamente +0,09 puntos, con intervalo [−0,56; +0,73]. Incluye cero: no hay evidencia clara de superioridad de uno sobre otro bajo ese remuestreo.

RMSE de los mismos modelos:

| Método | RMSE |
|---|---:|
| Media histórica | 698,69 |
| Ridge inicial | 698,02 |
| Gradient Boosting inicial | 882,97 |
| Último observado | 990,52 |

Ridge tiene un RMSE ligeramente menor que la media, pero un WAPE ligeramente mayor. Las métricas no son intercambiables.

**Explicación sencilla:** en la primera competencia, sacar el promedio fue la mejor forma de estimar las cantidades. Un método más complicado no ganó solo por ser más complicado.

### 12.2. Experimento B: ajuste temporal y prueba en abril de 2026

Archivo: `Etapa_03/resultados/hito_2b/ajuste_hiperparametros_resumen.csv`.

Esta tabla evalúa **solo abril de 2026**, no los dos cortes juntos:

| Método | WAPE de abril de 2026 |
|---|---:|
| Gradient Boosting ajustado | **6,0114 %** |
| Media histórica | 8,2923 % |
| Ridge ajustado | 8,4515 % |

Conclusión: ajustar Gradient Boosting usando noviembre como validación mejoró el desempeño en abril de 2026 respecto de la referencia.

No se debe comparar el 6,01 % de un único corte con el 6,95 % conjunto como si fueran la misma muestra.

### 12.3. Experimento C: ampliación exclusivamente laboral

Archivo: `Etapa_03/resultados/hito_2c/resumen_sensibilidad.csv`.

Se entrenan métodos únicamente con laborales. Se comparan dos historiales sobre **las mismas 172 franjas laborales** de los dos cortes evaluados.

| Método | Historial original | Historial ampliado con 2023 |
|---|---:|---:|
| Gradient Boosting ajustado laboral | 4,8300 % | **3,1690 %** |
| Ridge laboral | 6,4273 % | 3,9719 % |
| Último observado | 4,1311 % | 4,1311 % |
| Media histórica | 4,7881 % | 9,6546 % |

La ampliación favorece a Gradient Boosting y Ridge. La media histórica empeora: no basta incorporar datos antiguos y promediarlos indiscriminadamente.

El último observado no cambia porque agregar cortes más antiguos no reemplaza el antecedente completo más reciente.

Para el último corte, el entrenamiento laboral crece de **173 a 429 filas utilizables**. No son 429 fechas distintas: varias filas provienen de cada publicación.

Gradient Boosting ampliado menos media histórica original:

- Diferencia puntual: aproximadamente −1,6191 puntos.
- Media de diferencias bootstrap: −1,6262 puntos.
- Intervalo del 95 %: **[−2,0521; −1,1974]**.

La mejora es consistente bajo ese remuestreo, con las limitaciones de dependencia temporal y selección ya descritas.

#### Cobertura comunal de los cortes incorporados

| Corte laboral | Oriente: franjas completas de 48 | Sur: franjas completas de 48 |
|---|---:|---:|
| Abril de 2023 | 46 | 40 |
| Agosto de 2023 | 45 | 40 |
| Noviembre de 2023 | 44 | 42 |

Esta completitud exige algún valor en cada comuna. No certifica observación de todos los servicios. Las faltas se concentran en la madrugada; no se deben presentar sumas parciales como totales diarios completos.

**Explicación sencilla:** dar al programa más recuerdos ayudó a algunos métodos. Al promedio simple lo perjudicó, porque los recuerdos antiguos tenían niveles distintos de los recientes. El experimento muestra ese comportamiento, pero no identifica por sí solo su causa.

### 12.4. Experimento D: modelo común para los tres tipos de día

Archivo: `Etapa_03/resultados/hito_2d/modelo_unico.csv`.

Aquí cada modelo aprende conjuntamente con sectores y tipos de día. Las variables indicadoras distinguen contextos. Los datos de 2023 siguen siendo solo laborales.

| Método | WAPE total | Laboral | Sábado | Domingo |
|---|---:|---:|---:|---:|
| Gradient Boosting ampliado | **6,6627 %** | **3,3527 %** | 5,3604 % | 19,7697 % |
| Media histórica original | 6,9541 % | 4,7881 % | **4,3319 %** | 18,4673 % |
| Ridge original, ajustado | 7,2908 % | 4,3148 % | 7,2426 % | **17,2124 %** |
| Ridge ampliado | 7,4716 % | 4,2260 % | 7,2254 % | 18,6132 % |
| Gradient Boosting original, ajustado | 7,6133 % | 4,2462 % | 6,3646 % | 20,8201 % |

Todos utilizan las mismas 505 claves evaluadas.

Conclusiones:

1. Gradient Boosting ampliado obtiene el menor WAPE total de estas variantes.
2. Su ventaja se concentra en laborales.
3. La media histórica supera al Gradient Boosting ampliado en sábados y domingos.
4. Entre todas las variantes de esta tabla, Ridge original obtiene el menor WAPE de domingos.
5. Ampliar el historial no mejora todos los modelos: Ridge ampliado tiene mayor error total que Ridge original ajustado.

#### Comparación por corte

| Método | Noviembre de 2025 | Abril de 2026 |
|---|---:|---:|
| Gradient Boosting ampliado | 7,5620 % | **5,7755 %** |
| Media histórica original | **5,5977 %** | 8,2923 % |

Gradient Boosting ampliado no gana en ambos cortes. Su selección depende del criterio agregado y no de una superioridad uniforme.

#### Incertidumbre frente a la media histórica

| Comparación | Diferencia puntual de WAPE | Intervalo bootstrap del 95 % |
|---|---:|---:|
| Total | −0,2913 puntos | **[−0,9100; +0,2889]** |
| Laboral | −1,4353 puntos | **[−1,8115; −1,0462]** |

En el total, el intervalo incluye cero. En laborales, permanece negativo bajo el procedimiento aplicado.

**Cómo defenderlo:**

> "Seleccionamos Gradient Boosting por tener el menor error total evaluado y una mejora concentrada en laborales. Reconocemos que su ventaja global es pequeña y no concluyente según el bootstrap, por lo que conservamos la media histórica como referencia y proponemos validar la selección con nuevas publicaciones."

### 12.5. Por qué hay un 3,17 % y un 3,35 %

- **3,17 %:** Gradient Boosting entrenado únicamente con laborales, en el experimento de ampliación.
- **3,35 %:** Gradient Boosting entrenado conjuntamente con los tres tipos de día, en el experimento de modelo común.

Las pruebas laborales son comparables, pero el entrenamiento no es el mismo. No es un error de redondeo.

Por la misma razón, el Ridge inicial de 7,05 % no equivale al Ridge original ajustado de 7,29 %, y el Gradient Boosting inicial de 7,83 % no equivale al original ajustado de 7,61 %.

## 13. Cómo se incorporó 2023

`ampliacion_2023.py` lee los libros de Subidas `.xlsb` contenidos en tres ZIP locales:

```text
Datos/Fuentes/Subidas/Tablas de Subidas y Bajadas_abr2023.zip
Datos/Fuentes/Subidas/Tablas de subidas y bajadas ago23.zip
Datos/Fuentes/Subidas/Tablas de subidas y bajadas nov23.zip
```

El procedimiento:

1. Abre la hoja `subidas_prom_laboral` del libro de Subidas.
2. Aplica un filtro provisional de candidatos BUS: paradero presente o servicio Sonda que comienza por T/F/B, excluyendo códigos de Metro y Metrotren.
3. Normaliza los nombres comunales y restaura correspondencias explícitas como `NUNOA` → `ÑUÑOA`.
4. Convierte las 48 columnas horarias a formato largo: una fila por comuna y franja.
5. Suma los valores publicados por comuna y franja.
6. Conserva la ausencia si no existe ningún valor utilizable en esa comuna y franja.
7. Construye los agregados sectoriales, rechazando los que carecen de alguna comuna.
8. Une esos antecedentes al historial original para los experimentos laborales.

Los libros no tienen una columna explícita de modo. **El filtro BUS es provisional, no una clasificación oficial verificada.** Tampoco se certifica que todos los vacíos internos de servicios equivalgan a cero.

Las sumas pueden usar los valores numéricos disponibles de una comuna. Por eso "completo a nivel comunal" no significa "sin omisiones de paraderos o servicios".

Las fuentes tienen diferencias de estructura y metadatos. `revision_datos_2023.md` registra, entre otras, una discrepancia de fechas en agosto y filas con `Semana` vacía en noviembre. Ese documento conserva una conclusión anterior a la integración y no está completamente actualizado.

Se utilizaron las Subidas laborales, no Bajadas, y no se fabricaron perfiles de sábados o domingos para 2023.

## 14. Qué se comprobó al ejecutar el proyecto

La verificación se realizó en una copia temporal de la rama final, con los ZIP de 2023 disponibles y las dependencias fijadas en `requirements.txt`.

| Comprobación | Resultado |
|---|---|
| Cinco pruebas unitarias existentes | 5 de 5 pasan |
| Auditoría y reproducción de etapa II | Pasa |
| Comparación inicial | Se reproduce |
| Robustez y ajuste | Se reproducen |
| Experimento laboral ampliado | Se reproduce |
| Modelo común ampliado | Se reproduce |
| Comparación de resultados guardados | 21 CSV coinciden con `rtol=1e-9` y `atol=1e-8` |
| Claves de evaluación | Las mismas 505 para las cinco variantes finales |
| Predicciones finales | Finitas y no negativas |
| Alteración de datos objetivo y posteriores | No cambia las variables históricas revisadas |
| Notebook sin resultados previos | Falla al abrir una figura aún no generada |
| Notebook con resultados y figuras pregenerados | Termina correctamente |

`rtol` es tolerancia relativa y `atol` tolerancia absoluta. Permiten pequeñas diferencias de cálculo numérico. La comparación no exige identidad binaria de cada archivo, pero sí coincidencia de sus tablas dentro de esas tolerancias.

Entorno verificado: Python 3.14.9, pandas 3.0.5, NumPy 2.5.3, scikit-learn 1.7.2, matplotlib 3.11.2 y pyxlsb 1.0.10.

Los cinco tests cubren:

- Fronteras de etiquetas y ausencias.
- Historial incompleto o inexistente.
- WAPE no evaluable cuando el total observado es cero.
- Cobertura sin contar exclusiones dos veces.
- Perfiles que no ocultan faltantes.

Los dos últimos commits agregaron experimentos, no nuevos tests unitarios. Las comprobaciones adicionales de los modelos ampliados se realizaron durante la revisión; no quedaron incorporadas a la suite del repositorio.

**Reproducibilidad no equivale a validez definitiva.** Dos ejecuciones pueden coincidir y compartir el mismo límite metodológico.

Los registros de esta ejecución quedaron en `/tmp/demanda-etapa3-check.zezRq8/logs/`. Esa ruta es temporal y puede desaparecer; no es un archivo permanente del proyecto.

## 15. Limitaciones y correcciones pendientes

### 15.1. Pocos cortes independientes

Hay 505 franjas evaluadas, pero solo dos publicaciones de prueba conjunta. Los perfiles vecinos de una misma publicación pueden compartir variaciones.

No se debe afirmar que existe una gran muestra temporal independiente. El paso siguiente es evaluar nuevas publicaciones sin reutilizarlas para seleccionar la receta.

### 15.2. Noviembre se reutiliza para ajustar y evaluar

En `validacion_robustez.py`, noviembre de 2025 sirve para elegir hiperparámetros. Los experimentos de ampliación y modelo común reutilizan esos hiperparámetros y vuelven a reportar noviembre dentro de la evaluación conjunta.

Esto significa que noviembre **no es una prueba independiente de la selección de parámetros**, aunque las variables de cada predicción respeten el tiempo.

Además, el resultado de abril se observó durante las iteraciones posteriores del proyecto. El análisis completo sigue siendo exploratorio y retrospectivo.

Corrección futura: separar más cortes para ajuste y prueba, o utilizar una evaluación temporal anidada con más publicaciones. No puede resolverse generando más remuestreos de las mismas franjas.

### 15.3. Bootstrap de franjas correlacionadas

El remuestreo conserva el corte, pero no bloques horarios completos. Una evaluación por bloques o cortes, con más publicaciones, representaría mejor parte de la dependencia.

La mejora laboral observada es defendible como resultado del experimento. Su intervalo no debe presentarse como una garantía universal.

### 15.4. Comparabilidad y cobertura de 2023

El filtro de modo y la semántica de vacíos requieren validación adicional. Los cambios de oferta, cobertura o procesamiento entre años podrían afectar la comparación.

No está probado cuánto de la diferencia se debe a patrones de movilidad y cuánto a esas diferencias de fuente.

### 15.5. Domingos

El WAPE final de 19,77 % muestra una dificultad real. La media histórica y Ridge original ajustado tienen menor error de domingo en esta evaluación.

No se demostró una causa. Son hipótesis para estudiar la menor estabilidad, el volumen, la cobertura o la falta de historia adicional de fines de semana. No hay que atribuir el resultado a clima, evasión o oferta sin datos que lo respalden.

### 15.6. Notebook y figuras

El notebook ejecuta `figuras_hito_3.main()` antes de ejecutar la ampliación. Más adelante intenta mostrar:

```text
Etapa_03/resultados/figuras/07_historial_ampliado.png
```

En una ejecución sin resultados previos, esa imagen todavía no existe y aparece `FileNotFoundError`.

La solución pendiente es generar las figuras después de los cálculos que las alimentan, o volver a generarlas antes de mostrarlas. No se modificó el notebook durante la revisión.

### 15.7. Interpretación de la presentación

La lámina 15 conserva la matriz de media histórica y el sesgo cercano a −1,84 %. El modelo final tiene un sesgo global aproximadamente −3,06 %.

Dos opciones correctas:

1. Recalcular y mostrar la interpretación del Gradient Boosting final.
2. Mantenerla, pero titularla explícitamente como análisis de la referencia inicial.

El análisis de residuos y la importancia de variables originales también deben identificarse como resultados de sus respectivos modelos, no atribuirse automáticamente al final.

### 15.8. Documentación y regla de selección

El README y el plan mezclan estados antiguos y nuevos. El plan inicial contemplaba selección por sector y un empate práctico de 0,5 puntos que favorecía al último observado. El código comparado selecciona globalmente por WAPE y la entrega final escoge una configuración común.

La mejora final de 0,29 puntos frente a la media está por debajo de esos 0,5 puntos del criterio inicial. Deben explicar que cambió la regla de selección, en lugar de afirmar que se siguió sin cambios.

Una regla definida antes de evaluar es más defendible que una elegida después de ver quién gana. La selección actual debe comunicarse como provisional.

### 15.9. Límite operativo

Subidas no equivalen a ocupación. Un bus puede recibir subidas en distintas paradas mientras otras personas bajan.

Para proponer flota o frecuencia hacen falta, al menos, capacidad, oferta, recorridos, ocupación y validación operacional. Aquí no se demostró ahorro, reducción de espera ni mejora de servicio.

## 16. Conclusiones al limpio

### Lo que logramos

1. Una base sectorial auditada que distingue ausencias de ceros.
2. Reproducción de la referencia de etapa II.
3. Comparación de cuatro métodos sobre una muestra común.
4. Evaluación por tiempo, tipo de día y bloques horarios.
5. Ajuste de parámetros y estimación exploratoria de incertidumbre.
6. Un experimento que muestra el efecto de ampliar el historial laboral.
7. Una configuración común con el menor WAPE total de las variantes finales evaluadas.
8. Resultados que pueden volver a calcularse y contrastarse.

### Lo que aprendimos

- La media histórica es una referencia difícil de superar y debe mantenerse en las comparaciones.
- Un modelo más complejo no gana automáticamente.
- Incorporar antecedentes antiguos favoreció a Gradient Boosting en laborales, pero perjudicó a la media histórica ampliada.
- El uso que se da a la historia importa; más antecedentes no garantizan menor error.
- La ventaja laboral del modelo ampliado es mayor que su ventaja total.
- Ningún modelo domina todos los cortes y tipos de día.
- Los domingos siguen siendo un punto débil.
- Coincidir en categorías no equivale a pronosticar bien el volumen.
- Reproducir cifras no elimina limitaciones de selección, cobertura o independencia.

### Lo que todavía no podemos concluir

- Que Gradient Boosting será mejor en cualquier publicación futura.
- Que la ventaja global sea concluyente.
- Que los datos de 2023 tengan exactamente la misma cobertura que los nuevos.
- Que se pronostique demanda real corregida por evasión.
- Que una etiqueta Alto signifique bus lleno.
- Que el resultado determine cuántos buses deben circular.

### Evaluación general

El proyecto mejoró desde la etapa II y es defendible como trabajo académico de pronóstico retrospectivo. Tiene datos reales, referencias sencillas, iteración, resultados reproducibles y límites identificables.

La defensa debe apoyarse en esa comparación, no en presentar el modelo como una solución operativa terminada.

## 17. Preguntas de defensa y respuestas recomendadas

### 1. ¿Qué pronostican exactamente?

> "La suma de subidas promedio registradas por sector, tipo de día y franja de treinta minutos. No estimamos personas únicas ni corregimos por evasión."

### 2. ¿Por qué se necesita una referencia simple?

> "Para comprobar si la complejidad aporta. Con el historial original, la media histórica tuvo el menor WAPE inicial, por lo que no podíamos justificar un modelo complejo solo por su nombre."

### 3. ¿Por qué cambió el modelo seleccionado?

> "La comparación inicial favoreció a la media histórica. Luego ajustamos parámetros y ampliamos el historial laboral; en el experimento final Gradient Boosting obtuvo el menor error total. Son versiones diferentes del experimento."

### 4. ¿Qué significa WAPE de 6,66 %?

> "Que la suma de errores absolutos equivale al 6,66 % del volumen observado de las 505 franjas evaluadas. No significa 93,34 % de acierto ni un error uniforme por franja."

### 5. ¿Qué significa 505?

> "Son combinaciones únicas de corte, sector, tipo de día y franja, completas y con historial. No son 505 días independientes."

### 6. ¿Todos los métodos se compararon en las mismas observaciones?

> "Sí. En el experimento final utilizan las mismas 505 claves. En el experimento exclusivamente laboral se utilizan las mismas 172."

### 7. ¿Por qué no trataron los ausentes como cero?

> "Porque ausencia de publicación no demuestra ausencia de subidas. Mantenemos la marca de ausencia y excluimos objetivos sectoriales incompletos."

### 8. ¿Por qué 3,17 % en una lámina y 3,35 % en otra?

> "El 3,17 % proviene de entrenar solo con laborales. El 3,35 % corresponde al modelo que aprende con los tres tipos de día y se evalúa en el subconjunto laboral."

### 9. ¿La mejora es estadísticamente significativa?

> "La diferencia laboral permanece favorable en el bootstrap aplicado. La diferencia global no: su intervalo incluye cero. Además, hay dependencia entre franjas y reutilización de noviembre para ajustar, por lo que interpretamos la evidencia como exploratoria."

### 10. ¿Por qué Gradient Boosting si mejora solo 0,29 puntos en el total?

> "Obtiene el menor WAPE total evaluado y una mejora mayor en laborales. Lo seleccionamos provisionalmente, no como un ganador universal. Si se prioriza simplicidad, la media histórica sigue siendo una alternativa defendible."

### 11. ¿Por qué no usar un modelo distinto por tipo de día?

> "Es una alternativa razonable que esta evaluación sugiere estudiar. Esta entrega compara una configuración común. No demostramos que sea superior a todas las combinaciones posibles de modelos especializados."

### 12. ¿Agregar 2023 mejoró también fines de semana?

> "No agregamos observaciones de sábado o domingo de 2023. La ampliación es laboral; en el modelo común podría influir indirectamente por entrenamiento compartido, pero no equivale a tener nueva historia de fines de semana."

### 13. ¿Por qué empeoró la media ampliada?

> "Da igual peso a cortes antiguos y recientes, y en esta evaluación quedó por debajo de los niveles observados. El experimento muestra el efecto, pero no demuestra si su causa es movilidad, oferta o cobertura."

### 14. ¿Por qué el último observado no cambia al agregar 2023?

> "Porque los cortes incorporados son anteriores al último antecedente completo ya disponible. Su regla sigue copiando el mismo valor reciente."

### 15. ¿Hay fuga de información?

> "Los controles revisados muestran que las variables históricas no incorporan valores del objetivo ni posteriores. Sin embargo, noviembre fue usado para ajustar hiperparámetros y después aparece en la evaluación conjunta; ese corte no es una prueba independiente del ajuste."

### 16. ¿Por qué no separar filas al azar?

> "Porque queremos simular un pronóstico temporal. Separar al azar franjas de una misma publicación no reproduce el uso del pasado para anticipar un corte posterior."

### 17. ¿Qué significan las variables más importantes?

> "La permutación mostró dependencia del último valor y del indicador de domingo en los modelos ajustados originales. Eso describe el uso predictivo de esas variables, no sus causas ni necesariamente el comportamiento del modelo final ampliado."

### 18. ¿La categoría Alto indica saturación?

> "No. Se define con terciles históricos del promedio por comuna. Para hablar de saturación necesitamos ocupación y capacidad."

### 19. ¿La normalización por comuna corrige el tamaño de los sectores?

> "Solo divide la suma por el número fijo de comunas para construir etiquetas comparables. No ajusta por población, superficie, oferta o número de paraderos."

### 20. ¿Por qué los domingos tienen más error?

> "Es un resultado observado, pero no identificamos una causa. Debemos revisar estabilidad, volumen y cobertura, y conseguir más cortes de fin de semana."

### 21. ¿Qué validaron con las pruebas?

> "Cinco tests de datos, cobertura, etiquetas e historial. Además reprodujimos 21 CSV y comprobamos las claves y la temporalidad de las variables de los modelos ampliados. Eso no sustituye una nueva prueba futura."

### 22. ¿Está listo para producción?

> "No. Tenemos una evaluación reproducible, pero necesitamos corregir la ejecución limpia del notebook, validar las fuentes ampliadas y evaluar nuevas publicaciones antes de desplegar."

### 23. ¿Qué harían después?

> "Congelaríamos la receta, evaluaríamos una nueva publicación independiente y revisaríamos especialmente domingos. También confirmaríamos el filtro BUS de 2023 y actualizaríamos residuos y etiquetas del modelo elegido."

## 18. Cómo explicar las 17 láminas sin mezclar experimentos

| Lámina | Qué explicar | Cuidado |
|---|---|---|
| 1. Portada | Objetivo y equipo | No prometer ocupación ni ajuste de flota. |
| 2. Problema | Diferencias de intensidad por horario y tipo de día | Hablar de subidas registradas. |
| 3. Datos | Cortes, sectores y unidad de observación | No llamar serie diaria a perfiles publicados. |
| 4. Mejoras | Auditoría, comparación y evaluación | Separar trabajo terminado de pendientes. |
| 5. Modelos | Dos referencias y dos modelos de corrección | ML aprende un residuo logarítmico sobre la media. |
| 6. Validación | Uso del pasado para cada corte | Reconocer la reutilización de noviembre en el ajuste. |
| 7. Resultados originales | Media histórica gana la comparación inicial | Ese ganador pertenece al historial y configuración originales. |
| 8. Bootstrap | Incertidumbre de la comparación original | El intervalo que incluye cero no demuestra equivalencia. |
| 9. Ajuste e importancia | Configuración ajustada y prueba de abril | No atribuir estas importancias al modelo final ampliado. |
| 10. Tipo de día | El total puede ocultar diferencias | Identificar de qué experimento son los números. |
| 11. Curvas | Forma horaria y cercanía entre observado y pronóstico | Los huecos no son ceros ni capacidad de buses. |
| 12. Residuos | Dónde y en qué dirección falla la referencia | El archivo analizado corresponde a media histórica. |
| 13. Ampliación 2023 | Experimento laboral: 4,83 % a 3,17 % para GB | Solo laborales; filtro de modo provisional. |
| 14. Selección final | Modelo común: 6,66 % total y 3,35 % laboral | Ventaja global pequeña; no gana todos los días ni ambos cortes. |
| 15. Interpretación | Etiquetas y sesgo | La matriz y el −1,84 % corresponden a media histórica. |
| 16. Limitaciones | Pocos cortes, cobertura y prueba no independiente | Plantear un siguiente paso concreto. |
| 17. Cierre | Qué logramos y qué falta validar | Evitar anunciar una solución operativa terminada. |

### Transición entre resultados originales y ampliados

> "Hasta aquí analizamos el historial original. La media histórica fue la referencia más competitiva. Después hicimos un experimento adicional con tres publicaciones laborales de 2023, para comprobar si otros métodos podían aprovechar ese historial."

### Transición del experimento laboral al modelo común

> "La prueba exclusivamente laboral favoreció al Gradient Boosting ampliado. Luego evaluamos una misma configuración para los tres tipos de día. Por eso el resultado laboral cambia de 3,17 % a 3,35 %: el entrenamiento ahora es compartido."

## 19. Diccionario de columnas y nombres de resultados

Las variables de entrada están en la sección 6. Esta tabla explica campos adicionales de datos y salidas.

| Nombre | Qué representa |
|---|---|
| `periodo` | Identificador año-mes de publicación o corte |
| `comuna` | Comuna normalizada |
| `sector` | Oriente o Sur |
| `tipo_dia` | Laboral, sábado o domingo |
| `media_hora` | Inicio de franja, en formato HH:MM |
| `subidas_promedio` | Valor comunal del panel original |
| `subidas` | Valor preparado para los experimentos ampliados, con ausencias conservadas |
| `subidas_sector` | Suma de los valores comunales del sector; solo interpretable como objetivo completo cuando tiene cobertura |
| `promedio_por_comuna` | Suma sectorial dividida por número de comunas |
| `n_comunas` | Seis para Oriente, diez para Sur |
| `relleno_cero` | Marca de celda añadida por ausencia, no categoría de demanda |
| `comunas_ausentes` | Cantidad de comunas sin observación en el agregado |
| `cobertura_completa` | Indicador de que no falta ninguna comuna |
| `observado` | Objetivo real utilizado en evaluación; vacío si no es completo |
| `prediccion` | Estimación del método, en la escala original |
| `metodo` | Método y, en algunas tablas, variante de historial |
| `historial` | Original o ampliado |
| `n` | Número de filas evaluadas en el grupo |
| `n_entreno` | Número de filas supervisadas usadas para ajustar el modelo |
| `n_entreno_ultimo_corte` | Cantidad de entrenamiento del último corte evaluado |
| `n_antecedentes`, `n_hist` | Cantidad de antecedentes completos para esa combinación |
| `cortes_historial` | Cantidad de antecedentes por fila en el experimento laboral |
| `ultimo_antecedente` | Identificador del antecedente completo más reciente |
| `q1`, `q2` | Umbrales terciles históricos del promedio por comuna |
| `etiqueta_real` | Categoría obtenida a partir del observado |
| `etiqueta_predicha` | Categoría obtenida a partir de la predicción |
| `participacion_diaria_pct` | Peso de una franja en el perfil diario completo |
| `n_total` | Combinaciones posibles antes de las exclusiones |
| `n_evaluadas` | Combinaciones completas con historial |
| `n_incompletas` | Objetivos que carecen de alguna comuna |
| `n_sin_historial` | Objetivos completos que carecen de antecedente completo |
| `pct_evaluadas`, `pct_incompletas`, `pct_sin_historial` | Porcentajes de esos grupos disjuntos |
| `franjas_completas_de_48` | Franjas con algún valor en todas las comunas en 2023 |
| `MAE`, `RMSE`, `WAPE_pct` | Métricas de error explicadas en la sección 9 |
| `WAPE_todos` | WAPE conjunto del experimento final |
| `LABORAL`, `SABADO`, `DOMINGO` como columnas | WAPE del subgrupo correspondiente |
| `2025-11`, `2026-04` como columnas | WAPE de cada corte, no el observado de una fila |
| `sesgo_pct` | Déficit o exceso neto porcentual |
| `error`, `err` | Predicción menos observado |
| `abs` | Error absoluto por fila |
| `e2` | Error al cuadrado por fila |
| `error_medio` | Promedio del error firmado de un bloque |
| `bloque` | Intervalo horario de análisis de residuos |
| `acierto_etiqueta_pct`, `acierto_pct` | Coincidencia de categorías |
| `altos_reales` | Filas observadas clasificadas Alto |
| `altos_detectados` | Altos reales también pronosticados Alto |
| `recall_alto_pct` | Porcentaje de altos reales detectados |
| `subestimacion_altos_pct` | Déficit de volumen en los altos reales |
| `factor_umbral` | Multiplicador aplicado a los terciles para sensibilidad |
| `IC95_inf`, `IC95_sup` | Límites bootstrap del WAPE de un método |
| `WAPE_IC95_inf`, `WAPE_IC95_sup` | Mismo significado en el experimento laboral |
| `dif_vs_media`, `dif_vs_seleccionado` | Media bootstrap de la diferencia frente a la referencia |
| `dif_IC95_inf`, `dif_IC95_sup` | Límites de la diferencia bootstrap |
| `dif_laboral_IC95_inf`, `dif_laboral_IC95_sup` | Límites de diferencia para laborales del modelo común |
| `prob_mejor_que_media` | Fracción de remuestreos con menor WAPE que la media |
| `mejores_params` | Configuración elegida en la búsqueda temporal |
| `WAPE_valid_2025_11` | Error de validación para comparar configuraciones |
| `WAPE_prueba_2026_04` | Error en abril después de elegir la configuración |
| `importancia` | Deterioro medio al permutar una variable |
| `desv` | Desviación de ese deterioro entre repeticiones |
| `entradas_sha256` | Huellas digitales de archivos para identificar las entradas usadas |

`FEATURES` y `FEATS` son listas de nombres de predictores. `PRUEBAS` contiene los cortes evaluados. `B = 2000` es el número de remuestreos. `ROOT`, `ENTRADA` y `SALIDA` son rutas del programa, no variables predictivas.

`CANON` contiene correspondencias de nombres comunales y `MAPA` asigna comunas a sectores. Un hash SHA-256 identifica un archivo; no certifica la calidad de sus datos.

### Vocabulario para la materia

| Concepto | Significado |
|---|---|
| Panel | Tabla de combinaciones de entidades y cortes |
| Agregación | Resumir varias filas, aquí sumando por sector y franja |
| Imputación | Sustituir un faltante; no confundir con observación real |
| Baseline | Referencia sencilla para comparar |
| Feature | Variable de entrada del modelo |
| Target | Variable que se quiere pronosticar |
| Regresión | Predicción de una cantidad numérica |
| Clasificación | Asignación de una categoría |
| Residuo | Diferencia respecto de una predicción o referencia; debe indicarse la escala y el signo |
| Regularización | Restricción que limita ajustes extremos |
| Hiperparámetro | Configuración elegida antes o durante la selección del modelo |
| Generalización | Desempeño fuera de los ejemplos usados para desarrollar el modelo |
| Sobreajuste | Aprendizaje de particularidades que no se mantienen fuera de la muestra |
| Estacionalidad | Patrón asociado al calendario; aquí solo se representa parcialmente |
| No linealidad | Relación que no sigue un efecto proporcional constante |
| Interacción | Efecto de una variable que depende de otra |
| Bootstrap | Remuestreo con reemplazo de datos disponibles |
| Pareado | Métodos evaluados sobre las mismas observaciones remuestreadas |
| Dependencia | Observaciones que comparten información o variaciones |
| Significancia | Evaluación de una diferencia frente a su variabilidad, bajo un procedimiento y supuestos |
| Causalidad | Efecto atribuible a una causa; no se demuestra con importancia predictiva |
| Reproducibilidad | Poder repetir el procedimiento y obtener resultados compatibles |
| Prueba ciega | Evaluación cuyo resultado no se usa para desarrollar o elegir la solución |

## 20. Mapa de archivos y orden de ejecución

| Archivo o carpeta | Función |
|---|---|
| `Etapa_02/resultados/panel_demanda_bus.csv` | Panel observado de referencia |
| `Etapa_02/resultados/panel_demanda_bus_modelo.csv` | Rejilla completa con marcas de ausencia |
| `Etapa_03/codigo/base_reproducible.py` | Auditoría y reproducción de etapa II |
| `Etapa_03/codigo/test_base_reproducible.py` | Cinco tests existentes |
| `Etapa_03/codigo/comparacion_modelos.py` | Comparación original |
| `Etapa_03/codigo/validacion_robustez.py` | Bootstrap, RMSE, ajuste, permutación, residuos y sensibilidad |
| `Etapa_03/codigo/ampliacion_2023.py` | Experimento laboral de ampliación |
| `Etapa_03/codigo/modelo_unico.py` | Comparación común de los tres tipos de día |
| `Etapa_03/codigo/figuras_hito_3.py` | Gráficos |
| `Etapa_03/notebooks/etapa_iii_final.ipynb` | Integración de cálculos y visualización |
| `Etapa_03/resultados/hito_1/` | Auditoría y referencias reproducidas |
| `Etapa_03/resultados/hito_2/` | Comparación original |
| `Etapa_03/resultados/hito_2b/` | Robustez y ajuste |
| `Etapa_03/resultados/hito_2c/` | Ampliación laboral |
| `Etapa_03/resultados/hito_2d/` | Modelo común final |
| `Etapa_03/resultados/figuras/` | Imágenes de resultados |
| `Etapa_03/presentacion/deck/` | Fuentes de presentación; pueden diferir del PDF enviado |
| `Etapa_03/revision_datos_2023.md` | Revisión de estructura y límites de 2023; conserva estado antiguo |

### Ejecución ordenada desde la raíz

Estos comandos presuponen la **rama final**, los paneles de etapa II y los tres ZIP disponibles. Los scripts reescriben salidas de etapa III: para verificar sin afectar la entrega, usar una copia del proyecto.

Ejemplo de entorno en Linux:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r Etapa_03/requirements.txt

export MPLBACKEND=Agg
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

python -m unittest discover -s Etapa_03/codigo -p 'test_*.py' -v
python Etapa_03/codigo/base_reproducible.py
python Etapa_03/codigo/comparacion_modelos.py
python Etapa_03/codigo/validacion_robustez.py
python Etapa_03/codigo/ampliacion_2023.py
python Etapa_03/codigo/modelo_unico.py
python Etapa_03/codigo/figuras_hito_3.py
```

`MPLBACKEND=Agg` permite generar gráficos sin abrir ventanas. Las otras dos variables limitan hilos de cálculo para facilitar la ejecución; no son variables del pronóstico.

El orden genera los resultados antes de las figuras y evita la dependencia de imágenes antiguas. No corrige el orden interno del notebook.

Para verificar después el notebook sin sobrescribir su archivo fuente:

```bash
python -m pip install nbconvert ipykernel
python -m jupyter nbconvert --to notebook --execute \
  Etapa_03/notebooks/etapa_iii_final.ipynb \
  --output etapa_iii_verificado.ipynb \
  --output-dir /tmp/demanda-notebook \
  --ExecutePreprocessor.timeout=180
```

La ejecución del notebook vuelve a ejecutar scripts y a escribir sus resultados, aunque el notebook de salida se guarde en `/tmp`. En Windows cambian la activación, las variables de entorno y las rutas; el ejemplo anterior es para Linux.

## 21. Práctica para comprobar que lo entendiste

### Ejercicio 1: métricas

Observados: 100, 200 y 0. Pronósticos: 90, 220 y 10.

1. Errores firmados: −10, +20 y +10.
2. Errores absolutos: 10, 20 y 10.
3. WAPE: `100 × 40 / 300 = 13,33 %`.
4. MAE: `40 / 3 = 13,33` unidades.
5. RMSE: `raíz((100 + 400 + 100) / 3) ≈ 14,14` unidades.
6. Sesgo: `100 × 20 / 300 = +6,67 %`.

El método sobreestima en el neto. La franja de observado cero no impide calcular WAPE porque el volumen total es positivo.

### Ejercicio 2: etiquetas

Umbrales inventados: `q1 = 100`, `q2 = 200`.

| Valor completo por comuna | Categoría |
|---|---|
| 0 | Nulo |
| 100 | Bajo |
| 150 | Medio |
| 200 | Medio |
| 201 | Alto |

Si falta una comuna, la categoría es Sin dato completo, independientemente de la suma parcial.

### Ejercicio 3: información futura

Para pronosticar abril de 2026, ¿puedes incluir su observado en la media histórica?

**No.** La media debe utilizar cortes anteriores. Sí se puede consultar abril después para medir el error.

### Ejercicio 4: incertidumbre

Un modelo tiene menor WAPE puntual, pero el intervalo de diferencia frente a la referencia es [−1; +0,5]. ¿Puedes afirmar superioridad concluyente?

**No.** El intervalo incluye cero. Tampoco demuestra equivalencia.

### Ejercicio 5: los dos experimentos laborales

¿El 3,17 % y el 3,35 % describen el mismo modelo entrenado?

**No.** Uno aprende únicamente con laborales y el otro con los tres tipos de día. La historia laboral ampliada está presente en ambos.

### Ejercicio 6: tamaño de muestra

¿Dos mil remuestreos convierten dos publicaciones de prueba en dos mil pruebas futuras?

**No.** Reorganizan las observaciones existentes; no crean información temporal nueva.

## 22. Resúmenes para explicar y cerrar

### Versión sencilla

> "Queríamos adivinar cuántas subidas de bus habría en cada horario. Primero ordenamos los datos y comprobamos cuándo realmente faltaba información. Probamos copiar el último valor, sacar un promedio y usar dos programas que corrigieran ese promedio. Con pocos antecedentes, el promedio funcionó muy bien. Al agregar información antigua de días laborales, Gradient Boosting mejoró. Pero no ganó siempre, y todavía necesitamos datos nuevos para comprobar que seguirá funcionando."

### Versión técnica de un minuto

> "En etapa III auditamos el panel sectorial y reprodujimos las referencias de etapa II. Comparamos media histórica, último observado, Ridge y Gradient Boosting con evaluación temporal sobre las mismas franjas. Incorporamos métricas por subgrupo, bootstrap pareado, ajuste de hiperparámetros y análisis de residuos. La comparación original favoreció a la media histórica. Después incorporamos tres cortes laborales de 2023 y evaluamos un modelo común. Gradient Boosting ampliado obtuvo 6,66 % de WAPE total y 3,35 % laboral, frente a 6,95 % y 4,79 % de la media histórica. La selección es provisional: la ventaja global no es concluyente, los domingos presentan mayor error y la evaluación conjunta reutiliza un corte de ajuste."

### Cierre recomendado

> "El resultado principal es una comparación reproducible que muestra cómo cambia el desempeño al ampliar el historial. Gradient Boosting obtuvo el menor error total evaluado, con una mejora concentrada en laborales. Conservamos la media histórica como referencia competitiva y proponemos comprobar la selección con nuevas publicaciones independientes. El alcance sigue siendo pronosticar subidas registradas; para decisiones de operación se necesitan datos y validaciones adicionales."

### Seis ideas para recordar antes de exponer

1. **Qué pronosticamos:** subidas registradas, no ocupación ni pasajeros corregidos por evasión.
2. **Qué ganó primero:** la media histórica, en la comparación inicial.
3. **Qué ganó después:** Gradient Boosting ampliado, según WAPE total de las variantes finales.
4. **Qué números recordar:** 505 franjas; 6,66 % total; 3,35 % laboral; media 6,95 % y 4,79 %.
5. **Qué reconocer:** ventaja global pequeña, domingos difíciles y validación retrospectiva con reutilización de noviembre.
6. **Qué falta:** nuevas publicaciones independientes, confirmación de las fuentes ampliadas y actualización de la interpretación del modelo final.

