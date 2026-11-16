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

**Si Gradient Boosting ganó en abril (6,0 % vs 8,3 %), ¿por qué no lo eligieron?**
Porque en noviembre 2025 fue el peor (11 %) y en el conjunto es significativamente peor que la media (IC de la diferencia: +0,11 a +1,68 pp). Un solo corte favorable no basta. Lo dejamos como el candidato para cuando haya más historia.

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

**¿Por qué subestima?**
La demanda creció entre cortes y un promedio de cortes pasados reacciona con rezago.

**¿Qué harían con más tiempo?**
Integrar los cortes de 2022–2023, que ya están descargados y organizados, y repetir exactamente el mismo protocolo. Es lo que más necesita el ML para superar al baseline.
