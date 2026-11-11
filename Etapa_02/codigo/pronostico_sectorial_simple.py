"""Pronóstico sectorial de Subidas con media histórica y etiquetas horarias.

Usa solamente el panel principal y excluye agregados sectoriales incompletos
al construir antecedentes y evaluar. No requiere ejecutar los modelos previos.
"""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analisis_sectores import SECTORES, CLASES, CLAVES, etiquetar

METODOS = ["Media histórica", "Último observado"]


def pronosticar(perfil, corte):
    historia = perfil[(perfil.periodo < corte) & perfil.cobertura_completa]
    positivos = historia.loc[historia.promedio_por_comuna.gt(0), "promedio_por_comuna"]
    q1, q2 = positivos.quantile([1 / 3, 2 / 3]).tolist()
    assert 0 < q1 < q2
    filas = []
    for _, actual in perfil[perfil.periodo.eq(corte)].iterrows():
        anteriores = historia[(historia.sector == actual.sector) &
                              (historia.tipo_dia == actual.tipo_dia) &
                              (historia.media_hora == actual.media_hora)].sort_values("periodo")
        for metodo in METODOS:
            valor = (anteriores.subidas_sector.mean() if metodo == "Media histórica"
                     else anteriores.subidas_sector.iloc[-1]) if len(anteriores) else np.nan
            etiqueta_real = etiquetar(actual.promedio_por_comuna, actual.comunas_ausentes, q1, q2)
            etiqueta_pred = etiquetar(valor / actual.n_comunas, 0, q1, q2) if pd.notna(valor) else "Sin historial"
            filas.append(dict(periodo=corte, sector=actual.sector, tipo_dia=actual.tipo_dia,
                              media_hora=actual.media_hora, metodo=metodo,
                              observado=actual.subidas_sector if actual.cobertura_completa else np.nan,
                              prediccion=valor, etiqueta_real=etiqueta_real, etiqueta_predicha=etiqueta_pred,
                              cobertura_completa=bool(actual.cobertura_completa),
                              n_antecedentes=len(anteriores),
                              ultimo_antecedente=anteriores.periodo.iloc[-1] if len(anteriores) else None,
                              q1=q1, q2=q2))
    return pd.DataFrame(filas)


def main():
    root = Path(__file__).resolve().parents[2]
    salida = root / "Etapa_02/resultados/sectorial_simple"
    salida.mkdir(exist_ok=True)
    panel = pd.read_csv(root / "Etapa_02/resultados/panel_demanda_bus_modelo.csv")
    mapa = {c: s for s, cs in SECTORES.items() for c in cs}
    assert len(mapa) == 16 and set(mapa) <= set(panel.comuna)
    panel = panel[panel.comuna.isin(mapa)].copy()
    panel["sector"] = panel.comuna.map(mapa)
    assert len(panel) == 16 * 4 * 3 * 48
    assert panel.subidas_promedio.ge(0).all()
    assert not panel.duplicated(["periodo", "comuna", "tipo_dia", "media_hora"]).any()
    perfil = panel.groupby(CLAVES, as_index=False).agg(
        subidas_sector=("subidas_promedio", "sum"), promedio_por_comuna=("subidas_promedio", "mean"),
        comunas_ausentes=("relleno_cero", "sum"), n_comunas=("comuna", "size"))
    perfil["cobertura_completa"] = perfil.comunas_ausentes.eq(0)
    assert len(perfil) == 2 * 4 * 3 * 48
    assert perfil.n_comunas.eq(perfil.sector.map({s: len(cs) for s, cs in SECTORES.items()})).all()
    periodos = sorted(perfil.periodo.unique())
    pred = pd.concat([pronosticar(perfil, corte) for corte in periodos[1:]], ignore_index=True)
    assert pred.loc[pred.ultimo_antecedente.notna(), "ultimo_antecedente"].lt(
        pred.loc[pred.ultimo_antecedente.notna(), "periodo"]).all()
    # Comprobar que cambiar los objetivos futuros no altera pronósticos ni umbrales.
    alterado = perfil.copy()
    alterado.loc[alterado.periodo.eq(periodos[-1]), ["subidas_sector", "promedio_por_comuna"]] *= 10
    pd.testing.assert_frame_equal(
        pronosticar(perfil, periodos[-1])[["prediccion", "q1", "q2"]],
        pronosticar(alterado, periodos[-1])[["prediccion", "q1", "q2"]])
    q1, q2 = pred.loc[pred.periodo.eq(periodos[-1]), ["q1", "q2"]].iloc[0]
    assert [etiquetar(v, f, q1, q2) for v, f in [(0, 0), (q1, 0), (q2, 0), (q2 + 1, 0), (0, 1)]] == CLASES + ["Sin dato completo"]
    perfil["etiqueta"] = [etiquetar(v, f, q1, q2) for v, f in zip(perfil.promedio_por_comuna, perfil.comunas_ausentes)]
    perfil["participacion_diaria_pct"] = perfil.subidas_sector / perfil.groupby(["periodo", "sector", "tipo_dia"]).subidas_sector.transform("sum") * 100
    evaluables = pred[pred.observado.notna() & pred.prediccion.notna()].copy()
    assert np.isfinite(evaluables[["observado", "prediccion"]].to_numpy()).all()
    metricas, detalle = [], []
    for keys, grupo in evaluables.groupby(["periodo", "sector", "metodo"], sort=False):
        error = (grupo.observado - grupo.prediccion).abs()
        altos = grupo.etiqueta_real.eq("Alto")
        metricas.append(dict(zip(["periodo", "sector", "metodo"], keys),
                             n=len(grupo), MAE=float(error.mean()),
                             WAPE_pct=float(100 * error.sum() / grupo.observado.sum()),
                             acierto_etiqueta_pct=float(100 * grupo.etiqueta_real.eq(grupo.etiqueta_predicha).mean()),
                             altos_reales=int(altos.sum()),
                             altos_detectados=int((altos & grupo.etiqueta_predicha.eq("Alto")).sum())))
        for etiqueta, sub in grupo.groupby("etiqueta_real"):
            e = (sub.observado - sub.prediccion).abs()
            detalle.append(dict(zip(["periodo", "sector", "metodo"], keys), etiqueta=etiqueta, n=len(sub),
                                MAE=float(e.mean()), acierto_etiqueta_pct=float(100 * sub.etiqueta_real.eq(sub.etiqueta_predicha).mean())))
    metricas = pd.DataFrame(metricas)
    assert metricas.groupby(["periodo", "sector"]).n.nunique().eq(1).all()
    final = evaluables[(evaluables.periodo == periodos[-1]) & (evaluables.metodo == "Media histórica")]
    confusion = pd.crosstab([final.sector, final.etiqueta_real], final.etiqueta_predicha).reindex(
        pd.MultiIndex.from_product([SECTORES, CLASES], names=["sector", "etiqueta_real"]), fill_value=0).reindex(columns=CLASES, fill_value=0)
    assert confusion.to_numpy().sum() == len(final)
    conteos = perfil[perfil.periodo.eq(periodos[-1])].groupby(["sector", "tipo_dia", "etiqueta"]).size().unstack(fill_value=0).reindex(columns=CLASES + ["Sin dato completo"], fill_value=0)
    assert conteos.sum(axis=1).eq(48).all()
    for name, frame in [("perfil_sectorial.csv", perfil), ("predicciones.csv", pred),
                        ("metricas.csv", metricas), ("metricas_por_horario.csv", pd.DataFrame(detalle))]:
        frame.to_csv(salida / name, index=False)
    confusion.to_csv(salida / "confusion_etiquetas_abril_2026.csv")
    conteos.to_csv(salida / "conteo_etiquetas_abril_2026.csv")
    abril = perfil[perfil.periodo.eq(periodos[-1])]
    laboral = abril[abril.tipo_dia.eq("LABORAL")]
    hallazgos = {}
    for sector in SECTORES:
        z = laboral[laboral.sector.eq(sector)]
        maximo = z.loc[z.subidas_sector.idxmax()]
        hallazgos[sector] = dict(total_laboral=float(z.subidas_sector.sum()), maximo_hora=maximo.media_hora,
                                 maximo_subidas=float(maximo.subidas_sector),
                                 manana_pct=float(z.loc[z.media_hora.ge("06:00") & z.media_hora.lt("09:00"), "participacion_diaria_pct"].sum()),
                                 tarde_pct=float(z.loc[z.media_hora.ge("16:00") & z.media_hora.lt("20:00"), "participacion_diaria_pct"].sum()))
    hist = perfil[(perfil.periodo < periodos[-1]) & perfil.cobertura_completa & perfil.promedio_por_comuna.gt(0)]
    ejemplo = pred[(pred.periodo == periodos[-1]) & (pred.sector == "Sur") &
                   (pred.tipo_dia == "LABORAL") & (pred.media_hora == "07:00")]
    resumen = dict(sectores=SECTORES, periodos=periodos, n_celdas_comunales=len(panel),
                   n_celdas_sectoriales=len(perfil), ceros_añadidos=int(panel.relleno_cero.sum()),
                   q1=float(q1), q2=float(q2), n_calibracion=len(hist), hallazgos=hallazgos,
                   perfiles_abril=abril.to_dict("records"), metricas=metricas.to_dict("records"),
                   detalle=detalle, conteos=conteos.reset_index().to_dict("records"),
                   confusion=confusion.reset_index().to_dict("records"), ejemplo=ejemplo.to_dict("records"),
                   historia_ejemplo=perfil[(perfil.periodo < periodos[-1]) & perfil.sector.eq("Sur") & perfil.tipo_dia.eq("LABORAL") & perfil.media_hora.eq("07:00")].to_dict("records"),
                   maximos_laborales=perfil[perfil.tipo_dia.eq("LABORAL")].sort_values("subidas_sector").groupby(["periodo", "sector"]).tail(1).to_dict("records"))
    (salida / "resumen_presentacion.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    for sector in SECTORES:
        g = final[(final.sector == sector) & final.tipo_dia.eq("LABORAL")].sort_values("media_hora")
        fig, ax = plt.subplots(figsize=(11, 4.8))
        ax.plot(g.media_hora, g.observado, label="Observado", color="#0F7774", lw=2.5)
        ax.plot(g.media_hora, g.prediccion, label="Media histórica", color="#B6620C", lw=2, ls="--")
        ax.set_xticks(range(0, len(g), 4), g.media_hora.iloc[::4], rotation=35)
        ax.set(title=f"{sector}: laboral, abril de 2026", xlabel="Inicio de franja de 30 minutos", ylabel="Suma de Subidas_Promedio")
        ax.grid(alpha=.2); ax.legend(); fig.tight_layout()
        fig.savefig(salida / f"pronostico_{sector.lower()}.png", dpi=180); plt.close(fig)
    print(metricas[metricas.periodo.eq(periodos[-1])].to_string(index=False))
    print("Umbrales:", q1, q2, "| Franjas positivas de calibración:", len(hist))
    print("Autocontroles: cobertura, fronteras de etiquetas y ausencia de información futura: OK")


if __name__ == "__main__":
    main()
