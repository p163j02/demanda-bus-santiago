# Fuentes originales del DTPM

Esta es la ubicación canónica de los **datos de origen** utilizados en el proyecto o reservados para análisis complementarios futuros. Los libros Excel y paquetes ZIP se conservan tal como fueron descargados; no se reescribieron para organizarlos. Las salidas generadas por el proyecto permanecen en la carpeta de resultados de su etapa, por ejemplo `Etapa_02/resultados/`. En GitHub no se suben los libros Excel, los ZIP ni los CSV diarios originales; el `.gitignore` los excluye por tamaño y para evitar redistribuirlos sin verificar sus condiciones. Las instrucciones y los nombres esperados por el código se mantienen aquí.

## Organización

- `Subidas/`: libros de **Subidas por Paradero y Estación**. El panel de Etapa II usa noviembre de 2024, abril de 2025 v2, noviembre de 2025 y abril de 2026. También se conserva la variante de abril de 2025 sin `_v2` para documentar la selección de versión; no se usa en el pipeline actual.
- `Etapas/Utiles/`: nueve paquetes ZIP por corte, de agosto de 2022 a abril de 2026, y estructuras históricas. Se eliminaron las copias extraídas de abril de 2026 tras verificar sus hashes contra el ZIP conservado. Consulta el [inventario y las limitaciones de Etapas](Etapas/README.md).
- `Viajes/`: paquetes ZIP por los mismos cinco períodos. Para abril de 2026 se conservan también los archivos diarios extraídos que se exploraron anteriormente.
- `Referencias/`: diccionario oficial de campos, referencias geográficas y estructuras `.txt` separadas por año.

## Cortes disponibles

| Corte | Subidas | Etapas | Viajes |
|---|---:|---:|---:|
| Abril de 2024 | No hay un libro válido publicado en el enlace DTPM; el enlace entrega el libro v2 de abril de 2025 | ZIP disponible | ZIP disponible |
| Noviembre de 2024 | Sí | ZIP disponible | ZIP disponible |
| Abril de 2025 | Sí (se conserva la versión v2 usada y una variante sin v2) | ZIP disponible | ZIP disponible |
| Noviembre de 2025 | Sí | ZIP disponible | ZIP disponible |
| Abril de 2026 | Sí | ZIP disponible en `Etapas/Utiles/2026-04/` | ZIP y archivos diarios extraídos |

Los paquetes de Etapas/Viajes son fuentes complementarias: una etapa es un tramo y un viaje puede contener varias etapas. No se combinan directamente con el target de Subidas. Los archivos de períodos distintos permiten plantear análisis complementarios, pero la comparabilidad de cobertura y factores debe validarse antes de interpretar diferencias.

## Integridad y limpieza de duplicados

Los libros de Subidas descargados de nuevo y los ZIP de Etapas/Viajes de abril de 2026 se compararon con SHA-256. Eran copias binarias exactas de las fuentes que ya estaban aquí; esas copias redundantes se eliminaron después de la verificación. Los archivos originales canónicos permanecen intactos.

También se descargaron fuentes históricas de Subidas y Etapas, separadas de las entradas del modelo. En Etapas se conservaron agosto de 2022 y abril, agosto y noviembre de 2023 como candidatos pendientes de validar; los paquetes descargados de 2020–2021 se eliminaron por quedar fuera del alcance actual. Ninguna de estas fuentes históricas se incorporó automáticamente al panel.

Para una explicación sencilla, consulta la [guía de origen de datos y CSV](../../Documentacion/guia_sencilla_origen_datos_y_csv.md) y el [informe de revisión/consolidación](../../Documentacion/revision_descargas_dtpm_hoy.md).
