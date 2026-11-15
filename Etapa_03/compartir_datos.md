# Paquete de datos para el equipo — Etapa 3

El archivo **`Datos/Datos_equipo_etapa_03.zip`**, movido y renombrado desde `Datos.zip` sin alterar su contenido, reúne las fuentes necesarias para el trabajo actual y los candidatos seleccionados de ampliación. Se comparte por separado de la rama `etapa-03`: el `.gitignore` lo excluye, igual que los binarios originales. Por su tamaño aproximado de 14–15 GB, conviene enviarlo mediante un enlace de almacenamiento, no como adjunto ni dentro del pull request.

El `LEEME_DATOS.md` incluido conserva el nombre y la ubicación anteriores del paquete; la ruta actual es la indicada arriba. Las rutas internas y las instrucciones de extracción no cambian.

## Contenido y estado

### Datos utilizados actualmente

- Cuatro originales en `Datos/Fuentes/Subidas/`: noviembre de 2024, abril de 2025 **v2**, noviembre de 2025 y abril de 2026.
- `Etapa_02/resultados/panel_demanda_bus.csv`, `panel_demanda_bus_modelo.csv` y `panel_quality_report.json`.
- Referencias CSV y README de `Etapa_02/resultados/sectorial_simple/`, necesarias para cotejar la reproducción y consultar sus resultados.
- Las siete salidas de `Etapa_03/resultados/hito_1/`, para consultar el avance reproducido.

### Candidatos no integrados al modelo

- Los tres ZIP de Subidas/Bajadas de abril, agosto y noviembre de 2023, conservados sin modificar.
- Los nueve ZIP de `Datos/Fuentes/Etapas/Utiles/`: agosto de 2022; abril, agosto y noviembre de 2023; abril y noviembre de 2024; abril y noviembre de 2025; y abril de 2026.
- Las cinco estructuras históricas conservadas, incluido abril de 2022, que **no tiene base descargada**.
- Diccionario de campos, estructuras recientes y referencia geográfica de `Datos/Fuentes/Referencias/`.
- README de fuentes y registro de selección/limpieza de Etapas.

**No incluye** los paquetes de Viajes, los agregados históricos de 2011–2019 ni sus extracciones, la versión no seleccionada de Subidas de abril de 2025, ni las copias extraídas/archivos eliminados de Etapas. Es un paquete acotado para este trabajo, no una copia completa de toda la carpeta local `Datos/`.

## Cómo usarlo

1. Clonar el repositorio o actualizarlo a la rama del pull request que contiene el avance de etapa 3.
2. Abrir el ZIP y leer `LEEME_DATOS.md`. `MANIFIESTO_DATOS.json` lista las rutas, tamaños y SHA-256 de los archivos incluidos, distinguiendo entradas actuales, resultados y candidatos.
3. Extraer **en la raíz del repositorio**, sin crear otro nivel de carpeta. Las rutas comienzan con `Datos/`, `Etapa_02/` o `Etapa_03/`.
4. Si ya hay archivos en esas rutas, respaldarlos o comparar sus hashes antes de reemplazarlos. No extraer sobre trabajo local modificado sin revisarlo.
5. Seguir [las instrucciones del Hito 1](README.md#ejecutar-el-hito-1) para instalar dependencias, ejecutar la reproducción y correr las pruebas. El código se obtiene de Git, no del ZIP.

Para ejecutar solo el Hito 1 no hace falta descargar ni extraer las bases grandes: bastan los paneles, el reporte de calidad y las referencias de etapa 2, junto con el código del repositorio.

## Límites

El paquete conserva las rutas y los bytes de los originales. No transforma Etapas en Subidas ni confirma su comparabilidad. Los candidatos requieren auditoría completa, especialmente la cobertura de agosto de 2023, la discrepancia de columnas de 2022–2023 y el tratamiento de modos, zonas pagas y factores de expansión.

Las tablas de Etapas contienen registros individuales: compartir el paquete con el equipo para el proyecto no implica autorización para redistribuirlo públicamente. Verificar las condiciones de la fuente antes de publicar o reenviar los datos.
