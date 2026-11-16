# Preguntas probables — Etapa III

Las cifras salen de `resultados/hito_2`, `resultados/hito_2b` y `notebooks/etapa_iii_final.ipynb`.

## Validación

**¿Por qué no usaron K-fold / cross-validation normal?**
Porque mezcla el futuro con el pasado: el modelo podría entrenar con abril 2026 y predecir noviembre 2025. Usamos validación de **origen móvil**, que es la cross-validation para series de tiempo: cada prueba solo ve cortes anteriores. Un control automático altera los datos futuros y comprueba que ningún pronóstico cambie.

**¿Solo dos cortes de prueba? ¿No es poco?**
Sí, y lo reconocemos. Con 4 cortes, y al menos uno necesario como historial y otro para entrenar, dos pruebas es el máximo. Para compensar, calculamos intervalos de confianza por bootstrap sobre 505 franjas.

**¿Por qué WAPE y no MAPE?**
MAPE explota en franjas con pocas subidas (de madrugada, dividir por números cercanos a 0). WAPE divide el error total por las subidas totales, así que pesa más donde viaja más gente, que es lo que importa para la flota. Además reportamos MAE y RMSE.

**¿Cómo saben que la media histórica es mejor que Ridge?**
No lo afirmamos: la diferencia es de +0,09 pp, con IC 95 % de [−0,56; +0,73], lo que es un **empate estadístico**. Elegimos la media por ser más simple y porque detecta más franjas Alto (159 contra 151 de 166).

**¿Cómo ajustaron los hiperparámetros?**
Con una grilla entrenada en abr-2025 y validada en nov-2025. La mejor configuración se reentrenó con ambos cortes y se probó una sola vez en abr-2026. Gradient Boosting: profundidad 2, tasa 0,03, 100 iteraciones. Ridge: α = 10.

## Modelos

**¿Al final cuál es el modelo elegido?**
Depende del segmento. En días laborales, Gradient Boosting entrenado con el historial 2023–2026 (WAPE 3,2 %). En sábado y domingo, la media histórica, porque no hay datos de 2023 para esos días.

**¿No es contradictorio que con 4 cortes gane la media y con 7 gane Gradient Boosting?**
No. Con 4 cortes, el ML entrena con 173 filas y la media histórica aún no arrastra años antiguos. Con 7 cortes laborales, el ML entrena con 429 filas, y la media histórica empeora porque promedia 2023, cuando la demanda era 24 a 27 % menor. El ML usa el último observado para corregir esa tendencia.

**¿La mejora con 2023 es significativa?**
Sí: Gradient Boosting ampliado contra la media histórica original da −1,6 pp, con IC 95 % [−2,1; −1,2], sobre las mismas 172 franjas laborales.

**¿Qué tan confiables son los datos de 2023?**
Tienen el mismo origen (ADATRAP, sin evasión), pero solo traen días laborales y no tienen columna de modo. Filtramos BUS por paradero y código de servicio (T/F/B), excluyendo Metro y Metrotren. Cuadran con la tendencia de los cortes siguientes. La cobertura del Sur es menor (40 a 42 de 48 franjas completas), y las franjas incompletas se excluyen.

**¿Qué aprende el modelo de ML?**
Por importancia de permutación, sobre todo el **último valor observado** (tendencia reciente) y **si es domingo**. Corrige la media histórica, no reemplaza el perfil horario.

**¿Por qué modelar el residuo en logaritmo?**
Las subidas van de cero a ~30.000 por franja. En logaritmo, el error se vuelve relativo y el modelo no queda dominado por las horas punta.

## Datos

**¿Qué hacen con los datos faltantes?**
Distinguimos ausencia (comuna sin registro) de cero real. Una franja con alguna comuna ausente no se pronostica ni se evalúa. Por eso se excluye entre el 5 % y el 19 % de las franjas por corte, sobre todo de madrugada en el Sur.

**¿Pronostican pasajeros reales?**
No: subidas registradas (validaciones). La evasión no está corregida, y es parte del trabajo futuro.

## Interpretación

**¿El modelo sirve en la práctica?**
En días laborales y sábados el error es de ~3–6 %, suficiente para anticipar las puntas. El domingo tiene entre 14 % y 23 % de error y debe usarse con cautela. El modelo subestima ~2 % (~4 % en la punta de la tarde del Sur), así que conviene planificar con margen.

**¿Por qué subestima la media histórica?**
Porque la demanda crece en cada corte (Oriente +24 % entre abr-2023 y abr-2026) y un promedio de cortes pasados siempre llega atrasado.
