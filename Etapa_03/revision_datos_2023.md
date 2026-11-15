# Revisión de los libros de Subidas y Bajadas de 2023

## Conclusión

Los tres cortes son **candidatos para ampliar el historial laboral**, no una ampliación equivalente de los tres tipos de día del panel actual. No se han incorporado al panel ni se han recalculado pronósticos, umbrales o métricas.

Antes de integrarlos hay que resolver la separación BUS/Metro/Tren, el tratamiento de vacíos y las diferencias de estructura y metadatos. La propuesta más prudente es conservar la evaluación principal del Hito 1 y comparar, por separado y sobre las mismas filas laborales, el efecto de agregar el historial de 2023.

## Archivos y contenido

Se revisaron los seis libros `.xlsb` contenidos en estos ZIP de `Datos/Fuentes/Subidas/`:

- `Tablas de Subidas y Bajadas_abr2023.zip`.
- `Tablas de subidas y bajadas ago23.zip`.
- `Tablas de subidas y bajadas nov23.zip`.

Cada ZIP contiene un libro `Matriz_sub_SS_MH` y otro `Matriz_baj_SS_MH`. Cada libro tiene `FICHA_DATOS` y una hoja de datos: `subidas_prom_laboral` o `bajadas_prom_laboral`. Las fichas describen promedios laborales obtenidos de Bips! y GPS procesados en ADATRAP y declaran que no incluyen evasión.

| Corte | Período declarado en la ficha de Subidas | Filas de Subidas | Filas de Bajadas |
|---|---|---:|---:|
| Abril de 2023 | Laborales del 17 al 21 de abril | 65.188 | 67.857 |
| Agosto de 2023 | Laborales del 7 al 11 de agosto | 65.956 | 62.649 |
| Noviembre de 2023 | Laborales del 6 al 10 de noviembre | 67.052 | 70.203 |

Los conteos son de filas de datos, incluidos todos los modos; no de pasajeros, franjas sectoriales ni días independientes. Se excluyen las filas totalmente vacías. En noviembre se incluyen 1.096 filas con datos pero sin valor en `Semana`.

## Comparabilidad con el panel actual

- **Tiempo:** hay 48 columnas horarias, desde `0:00:00` hasta `23:30:00`. No hay hojas de sábado o domingo. Cada libro proporciona un perfil promedio, no cinco observaciones diarias separadas.
- **Formato:** las filas distinguen comuna, paradero, parada SIMT y servicio. Las medias horas están en columnas y existe `TOTAL`. El panel actual usa formato largo, con `Tipo_dia`, `Modo`, `Media_hora` y `Subidas_Promedio`. El constructor actual no puede leer los libros de 2023 sin adaptación.
- **Modo:** no existe `Modo`. Aparecen líneas de Metro, `METROTREN_NOS`, servicios con códigos T/F/B y filas sin servicio identificado. Filtrar únicamente códigos T descartaría parte de los candidatos BUS. La correspondencia de identificadores debe validarse antes de construir un filtro definitivo.
- **Territorio:** aparecen las 16 comunas de los sectores, pero con nombres como `NUNOA`, `SAN JOAQUIN` y `SAN RAMON`. Se necesita una correspondencia explícita con los nombres canónicos del panel; no basta el normalizador actual, que no restaura esas tildes.
- **Agregación:** habría que sumar los valores horarios por comuna después de separar modos y revisar servicios, zonas pagas y la columna `segunda_parada` de abril. No se debe sumar `TOTAL` a las medias horas ni sumar bajadas al objetivo de subidas.

La ficha de `Subida_Paradero_Estacion_2024.11.xlsb` también describe subidas Bips! con paradero estimado y sin evasión, pero incluye laboral, sábado y domingo y una columna explícita de modo. Esto apoya la relación conceptual entre las fuentes; no demuestra por sí solo igualdad de cobertura y procesamiento entre años.

## Calidad y advertencias

1. **Vacíos y ceros:** no hay valores horarios explícitos iguales a cero en ninguno de los tres libros de Subidas. Hay muchos vacíos; no se ha confirmado si representan ausencia de subidas, ausencia de servicio o datos no publicados. No deben convertirse automáticamente en ceros ni en categoría Nulo. Bajadas de abril sí contiene ceros explícitos; esa diferencia no permite inferir la semántica de los vacíos de Subidas.
2. **Valores y totales:** el recorrido completo no encontró valores horarios numéricos negativos, no finitos ni texto inesperado. En Subidas, todos los `TOTAL` numéricos coinciden con la suma de las medias horas publicadas, con tolerancia `rtol=1e-9`, `atol=1e-6`. Esto verifica consistencia aritmética, no cobertura completa. En Bajadas hay dos filas sin total numérico en agosto y una en noviembre.
3. **Noviembre:** las filas 65.959 a 67.054 de `subidas_prom_laboral` tienen datos y `Semana` vacía. Principalmente corresponden a Quinta Normal, Lo Prado e Independencia; hay dos filas de los sectores actuales, Providencia y Ñuñoa. Filtrar por `Semana` no vacía perdería observaciones. El período de esas filas no debe asignarse silenciosamente sin documentar la decisión.
4. **Agosto:** la ficha y el título de Subidas dicen laborales del 7 al 11; la columna `Semana` dice «7-13 agosto 2023». Hay una discrepancia de etiquetas que conviene confirmar, no interpretar automáticamente como promedio de siete días. Además, al menos 340 filas con códigos de servicio candidatos BUS carecen de comuna y paradero; no deben asignarse territorialmente por suposición.
5. **Bajadas de abril:** `FICHA_DATOS` indica «marzo 2023, 20 al 24», mientras el título de `bajadas_prom_laboral` y sus filas indican abril, 17 al 21. El archivo no debe usarse como un corte fechado inequívocamente hasta aclararlo. La ficha de Subidas de abril no presenta esa discrepancia.

### Disponibilidad horaria exploratoria de Subidas

Para explorar se marcaron como candidatos BUS los servicios con código T/F/B o identificador de paradero de bus, excluyendo códigos de Metro y Tren. Este filtro es provisional, no una clasificación oficial de modo.

| Corte | Oriente: franjas con algún valor en cada comuna / 48 | Sur: franjas con algún valor en cada comuna / 48 |
|---|---:|---:|
| Abril de 2023 | 46 | 40 |
| Agosto de 2023 | 45 | 40 |
| Noviembre de 2023 | 44 | 42 |

**No es una certificación de cobertura completa:** tener algún valor publicado en cada comuna no prueba que todos sus paraderos o servicios estén observados. Las franjas sin alguna comuna se concentran en la madrugada. No se pueden presentar totales diarios como completos con estos resultados.

## Recomendación para la siguiente fase

1. Mantener las métricas reproducidas del Hito 1 como referencia sin cambios.
2. Preparar, si se acuerda ampliar el alcance, un panel de Subidas de 2023 separado, únicamente laboral, con procedencia y ausencias explícitas. Bajadas queda fuera del objetivo actual.
3. Validar el filtro BUS y los metadatos antes de unirlo al historial. No imputar sábados y domingos ni reconstruir comunas sin respaldo.
4. Comparar historial original frente a historial ampliado sobre las mismas franjas laborales de los cortes evaluados. Más antecedentes no garantizan menor error; pueden introducir cambios de oferta, cobertura o patrones entre años.
5. Acordar por adelantado si esta comparación será un análisis de sensibilidad o modificará la evaluación principal y la regla de selección. Estos cortes anteriores no constituyen una nueva prueba futura independiente.

## Alcance de la revisión

Se extrajeron los ZIP y se convirtieron fichas y muestras a Markdown en `/tmp/docs/subidas_2023/`; se recorrieron todas las filas y se generaron también versiones Markdown completas y resúmenes de auditoría temporales. Se utilizaron `pyxlsb`, `openpyxl` y MarkItDown. Los originales y las salidas del Hito 1 permanecen sin cambios. No se revisaron fórmulas o formato visual, no se verificaron las discrepancias con DTPM y no se aprobó todavía la comparabilidad estadística para incorporar 2023.
