"""Comparación oriente/sur y etiquetas horarias del avance de Etapa II.

Ejecutar después de etapa_ii_analysis.py. Se evalúa el modelo común ya existente;
no se ajustan hiperparámetros ni se entrenan modelos separados por sector.
"""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SECTORES = {
    "Oriente": ["LAS CONDES", "VITACURA", "LO BARNECHEA", "PROVIDENCIA", "LA REINA", "ÑUÑOA"],
    "Sur": ["LA CISTERNA", "EL BOSQUE", "SAN BERNARDO", "LA PINTANA", "SAN RAMÓN",
            "SAN MIGUEL", "LA GRANJA", "SAN JOAQUÍN", "PEDRO AGUIRRE CERDA", "LO ESPEJO"],
}
CLASES = ["Nulo", "Bajo", "Medio", "Alto"]
MODELOS = ["Último corte", "Media histórica", "HistGradientBoosting (lags por corte)"]
CLAVES = ["periodo", "sector", "tipo_dia", "media_hora"]


def etiquetar(valor, faltantes, q1, q2):
    if faltantes:
        return "Sin dato completo"
    if valor == 0:
        return "Nulo"
    if valor <= q1:
        return "Bajo"
    if valor <= q2:
        return "Medio"
    return "Alto"


def main():
    root = Path(__file__).resolve().parents[2]
    resultados = root / "Etapa_02/resultados"
    salida = resultados / "sectores"
    salida.mkdir(exist_ok=True)
    panel = pd.read_csv(resultados / "panel_demanda_bus_modelo.csv")
    mapa = {comuna: sector for sector, comunas in SECTORES.items() for comuna in comunas}
    assert len(mapa) == sum(map(len, SECTORES.values())) == 16
    assert set(mapa) <= set(panel.comuna)
    panel = panel[panel.comuna.isin(mapa)].copy()
    panel["sector"] = panel.comuna.map(mapa)
    assert len(panel) == 16 * 4 * 3 * 48
    assert not panel.duplicated(["periodo", "comuna", "tipo_dia", "media_hora"]).any()
    assert panel.subidas_promedio.ge(0).all()
    perfil = panel.groupby(CLAVES, as_index=False).agg(
        subidas_sector=("subidas_promedio", "sum"),
        promedio_por_comuna=("subidas_promedio", "mean"),
        comunas_ausentes=("relleno_cero", "sum"), n_comunas=("comuna", "size"),
    )
    assert perfil.n_comunas.eq(perfil.sector.map({s: len(cs) for s, cs in SECTORES.items()})).all()
    # Las ausencias no justifican una etiqueta de intensidad ni un cero observado.
    perfil["cobertura_completa"] = perfil.comunas_ausentes.eq(0)
    train = perfil[(perfil.periodo < "2026-04") & perfil.cobertura_completa & perfil.promedio_por_comuna.gt(0)]
    q1, q2 = train.promedio_por_comuna.quantile([1 / 3, 2 / 3]).tolist()
    assert 0 < q1 < q2
    assert [etiquetar(v, f, q1, q2) for v, f in [(0, 0), (q1, 0), (q2, 0), (q2 + 1, 0), (0, 1), (1, 1)]] == CLASES + ["Sin dato completo"] * 2
    perfil["etiqueta"] = [etiquetar(v, f, q1, q2) for v, f in zip(perfil.promedio_por_comuna, perfil.comunas_ausentes)]
    perfil["participacion_diaria_pct"] = perfil.subidas_sector / perfil.groupby(["periodo", "sector", "tipo_dia"]).subidas_sector.transform("sum") * 100
    assert np.allclose(perfil.groupby(["periodo", "sector", "tipo_dia"]).participacion_diaria_pct.sum(), 100)
    perfil.to_csv(salida / "perfil_y_etiquetas.csv", index=False)
    pd.DataFrame([{"sector": s, "comuna": c} for s, cs in SECTORES.items() for c in cs]).to_csv(salida / "comunas_sectores.csv", index=False)
    pred = pd.read_csv(resultados / "predicciones_modelo_inicial.csv")
    pred = pred[pred.comuna.isin(mapa)].copy()
    pred["sector"] = pred.comuna.map(mapa)
    assert np.isfinite(pred[["subidas_promedio", "prediccion"]].to_numpy()).all()
    pred = pred.merge(perfil[CLAVES + ["etiqueta", "cobertura_completa"]], on=CLAVES, validate="many_to_one")
    metricas = []
    # Reportamos el error de celdas comunales, sin cancelar errores al sumar por zona.
    for muestra, datos in [("Panel provisional", pred), ("Solo observadas", pred[pred.relleno_cero.eq(0)])]:
        for keys, grupo in datos.groupby(["periodo", "sector", "modelo"], sort=False):
            error = np.abs(grupo.subidas_promedio - grupo.prediccion)
            metricas.append(dict(zip(["periodo", "sector", "modelo"], keys), muestra=muestra,
                                 n=len(grupo), MAE=float(error.mean()),
                                 RMSE=float(np.sqrt(np.mean(error ** 2))),
                                 WAPE_pct=float(100 * error.sum() / grupo.subidas_promedio.sum())))
    metricas = pd.DataFrame(metricas)
    metricas.to_csv(salida / "metricas_por_sector.csv", index=False)
    detalle = []
    final = pred[(pred.periodo == "2026-04") & pred.relleno_cero.eq(0)]
    for (sector, modelo, etiqueta), grupo in final.groupby(["sector", "modelo", "etiqueta"], sort=False):
        error = np.abs(grupo.subidas_promedio - grupo.prediccion)
        detalle.append(dict(sector=sector, modelo=modelo, etiqueta=etiqueta, n=len(grupo),
                            MAE=float(error.mean()), WAPE_pct=float(100 * error.sum() / grupo.subidas_promedio.sum()) if grupo.subidas_promedio.sum() else None))
    detalle = pd.DataFrame(detalle)
    detalle.to_csv(salida / "metricas_por_sector_y_horario.csv", index=False)
    conteos = perfil[perfil.periodo.eq("2026-04")].groupby(["sector", "tipo_dia", "etiqueta"]).size().unstack(fill_value=0).reindex(columns=CLASES + ["Sin dato completo"], fill_value=0)
    assert conteos.sum(axis=1).eq(48).all()
    conteos.to_csv(salida / "conteo_etiquetas_abril_2026.csv")
    laboral = perfil[(perfil.periodo == "2026-04") & (perfil.tipo_dia == "LABORAL")]
    pivote = laboral.pivot(index="media_hora", columns="sector", values="participacion_diaria_pct")
    completos = laboral.pivot(index="media_hora", columns="sector", values="cobertura_completa").all(axis=1)
    hallazgos = {}
    for sector in SECTORES:
        zona = laboral[laboral.sector == sector]
        maximo = zona.loc[zona.subidas_sector.idxmax()]
        manana = zona[(zona.media_hora >= "06:00") & (zona.media_hora < "09:00")].participacion_diaria_pct.sum()
        tarde = zona[(zona.media_hora >= "16:00") & (zona.media_hora < "20:00")].participacion_diaria_pct.sum()
        hallazgos[sector] = dict(total_laboral=float(zona.subidas_sector.sum()), maximo_hora=maximo.media_hora,
                                 maximo_subidas=float(maximo.subidas_sector), manana_pct=float(manana), tarde_pct=float(tarde))
    maximos = perfil[perfil.tipo_dia.eq("LABORAL")].sort_values("subidas_sector").groupby(["periodo", "sector"]).tail(1)
    resumen = dict(sectores=SECTORES, n_celdas=len(panel), ceros_añadidos=int(panel.relleno_cero.sum()),
                   q1=q1, q2=q2, n_calibracion=len(train), cortes_calibracion=sorted(train.periodo.unique()),
                   unidad_umbral="subidas promedio agregadas divididas por el número fijo de comunas del sector",
                   regla="Nulo=0 observado, Bajo=(0,q1], Medio=(q1,q2], Alto>q2. Si falta una comuna: Sin dato completo.",
                   hallazgos=hallazgos, correlacion_laboral=float(pivote.Oriente.corr(pivote.Sur)),
                   correlacion_laboral_franjas_completas=float(pivote.loc[completos, "Oriente"].corr(pivote.loc[completos, "Sur"])),
                   maximos_laborales=maximos[["periodo", "sector", "media_hora", "subidas_sector"]].to_dict("records"),
                   perfiles_abril=perfil[perfil.periodo.eq("2026-04")].to_dict("records"),
                   perfiles_laborales=perfil[perfil.tipo_dia.eq("LABORAL")].to_dict("records"),
                   metricas=metricas.to_dict("records"), detalle=detalle.to_dict("records"),
                   conteos=conteos.reset_index().to_dict("records"))
    (salida / "resumen_presentacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    colores = {"Oriente": "#0F7774", "Sur": "#B6620C"}
    for normalizado in [False, True]:
        fig, ax = plt.subplots(figsize=(11, 4.8))
        for sector, datos in laboral.groupby("sector"):
            datos = datos.sort_values("media_hora")
            col = "participacion_diaria_pct" if normalizado else "subidas_sector"
            ax.plot(datos.media_hora, datos[col].where(datos.cobertura_completa),
                    label=sector, color=colores[sector], lw=2.5)
        ax.set_xticks(range(0, 48, 4), [f"{h:02}:00" for h in range(0, 24, 2)])
        ax.set(xlabel="Inicio de franja de 30 minutos", ylabel="% del total diario del sector" if normalizado else "Suma de Subidas_Promedio",
               title="Oriente y sur: día laboral, abril de 2026")
        ax.grid(alpha=.18); ax.legend(); fig.tight_layout()
        fig.savefig(salida / ("perfil_laboral_normalizado.png" if normalizado else "perfil_laboral_volumen.png"), dpi=180)
        plt.close(fig)
    print(json.dumps({k: v for k, v in resumen.items() if k in ["n_celdas", "ceros_añadidos", "q1", "q2", "n_calibracion", "hallazgos", "correlacion_laboral", "correlacion_laboral_franjas_completas"]}, ensure_ascii=False, indent=2))
    print(metricas[(metricas.periodo == "2026-04") & (metricas.muestra == "Solo observadas")].to_string(index=False))


if __name__ == "__main__":
    main()
