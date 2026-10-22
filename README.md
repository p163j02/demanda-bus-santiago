# Predicción de demanda de buses en Santiago

Proyecto de Ciencia de Datos para explorar y pronosticar las subidas registradas de buses por comuna, tipo de día y franja de 30 minutos, usando cortes publicados por DTPM. El avance actual incluye preparación de datos, análisis descriptivo, baselines y un primer modelo temporal.

> **Alcance:** el target es `Subidas_Promedio` de las tablas históricas de Subidas. No representa el total real de pasajeros ni corrige por evasión. Las métricas son preliminares; hay pocos cortes y las combinaciones ausentes tratadas provisionalmente como cero deben validarse.

## Estructura

```text
demanda-bus-santiago/
├── Etapa_01/       Propuesta e informe de la primera entrega
├── Etapa_02/       Código, notebook, resultados y guion del avance
├── Etapa_03/       Espacio de referencia para la presentación técnica final
├── Etapa_04/       Espacio de referencia para la feria de proyectos
├── Datos/
│   └── Fuentes/    Ubicación local de los datos fuente DTPM
└── Documentacion/  Bitácora, rúbrica y guías de datos
```

## Para empezar

El notebook anotado está en [`Etapa_02/notebooks/etapa_ii_avance.ipynb`](Etapa_02/notebooks/etapa_ii_avance.ipynb). Para ejecutarlo solo se necesita el panel de modelamiento incluido en `Etapa_02/resultados/` y las dependencias de Python (`pandas`, `scikit-learn` y `matplotlib`).

Desde la raíz del repositorio:

```bash
uv run --with pandas --with scikit-learn --with matplotlib \
  python Etapa_02/codigo/etapa_ii_analysis.py
```

Para regenerar los paneles desde los libros originales:

```bash
uv run --with openpyxl --with pyxlsb \
  python Etapa_02/codigo/build_panel.py
```

Este último paso requiere además LibreOffice (`libreoffice` o `soffice`) y los cuatro libros de Subidas en `Datos/Fuentes/Subidas/`. Sus nombres y períodos están documentados en [`Datos/Fuentes/README.md`](Datos/Fuentes/README.md).

## Política de datos

Los archivos fuente originales (libros Excel, paquetes ZIP y datos CSV de gran tamaño) **no se incluyen en GitHub**, por tamaño y para evitar redistribuir datos sin verificar sus condiciones. Se conservan localmente bajo `Datos/Fuentes/`, pero están excluidos del control de versiones. Los paneles procesados y resultados pequeños de Etapa II sí están incluidos para que se pueda revisar y ejecutar el análisis sin descargar todos los archivos originales.

## Guías y resultados

- [Informe de la propuesta — Etapa I](Etapa_01/entrega/Informe_Etapa_I.pdf)
- [Notebook anotado — Etapa II](Etapa_02/notebooks/etapa_ii_avance.ipynb)
- [Guion de presentación — Etapa II](Etapa_02/presentacion/guion_etapa_ii.md)
- [Panel y métricas preliminares](Etapa_02/resultados/README.md)
- [Diccionario de salidas](Etapa_02/resultados/DICCIONARIO_SALIDAS.md)
- [Guía sencilla sobre fuentes y CSV](Documentacion/guia_sencilla_origen_datos_y_csv.md)
- [Bitácora y limitaciones de datos](Documentacion/bitacora_datos_proyecto.md)
- [Revisión de las descargas DTPM](Documentacion/revision_descargas_dtpm_hoy.md)

Las salidas deben interpretarse junto con las advertencias sobre cobertura comunal, medios de pago, ceros provisionales e incertidumbre de la validación temporal.
