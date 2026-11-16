"""Hito 2d: un solo modelo para todos los tipos de día.

Gradient Boosting entrenado con todo el historial disponible (2023 solo existe para LABORAL;
sábado y domingo parten en 2024-11) contra la media histórica, sobre las mismas franjas
de prueba (2025-11 y 2026-04, los tres tipos de día), con bootstrap pareado.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Etapa_03/codigo"))
import ampliacion_2023 as a  # noqa: E402

SALIDA = ROOT / "Etapa_03/resultados/hito_2d"
FEATS = a.FEATURES + ["dia_LABORAL", "dia_SABADO", "dia_DOMINGO"]


def perfil(comunal):
    comunal = comunal.assign(sector=comunal.comuna.map(a.MAPA))
    return comunal.groupby(["periodo", "tipo_dia", "sector", "media_hora"]).agg(
        observado=("subidas", lambda s: s.sum() if s.notna().all() else np.nan)).reset_index()


def features(p):
    partes = []
    for dia, g in p.groupby("tipo_dia"):
        t = a.features(g.drop(columns="tipo_dia"))
        partes.append(t.assign(tipo_dia=dia))
    t = pd.concat(partes, ignore_index=True)
    for d in ["LABORAL", "SABADO", "DOMINGO"]:
        t[f"dia_{d}"] = t.tipo_dia.eq(d).astype(int)
    return t


def main():
    c2023 = pd.concat([a.leer_2023(p, z)[0] for p, z in a.FUENTES.items()]).assign(tipo_dia="LABORAL")
    pan = pd.read_csv(ROOT / "Etapa_02/resultados/panel_demanda_bus_modelo.csv")
    pan = pan[pan.comuna.isin(a.MAPA)].copy()
    pan["subidas"] = pan.subidas_promedio.where(pan.relleno_cero.eq(0))
    pan = pan[["periodo", "comuna", "tipo_dia", "media_hora", "subidas"]]
    t_orig, t_full = features(perfil(pan)), features(perfil(pd.concat([c2023, pan])))
    k = ["periodo", "tipo_dia", "sector", "media_hora"]
    ok = t_orig[t_orig.periodo.isin(a.PRUEBAS) & t_orig.observado.notna()][k]
    filas = []
    for corte in a.PRUEBAS:
        for nombre_t, t in [("orig", t_orig), ("full", t_full)]:
            ent = t[t.periodo.lt(corte) & t.observado.notna()]
            pr = t[t.periodo.eq(corte)].merge(ok[ok.periodo.eq(corte)], on=k)
            y = np.log1p(ent.observado) - ent.log_media
            preds = {}
            if nombre_t == "orig":
                preds["Media histórica (2024→)"] = pr.media
            for nm, mdl in [("Gradient Boosting", HistGradientBoostingRegressor(random_state=0, **a.GB_PARAMS)),
                            ("Ridge", Ridge(alpha=10))]:
                mdl.fit(ent[FEATS], y)
                etiqueta = f"{nm} ({'2023→' if nombre_t == 'full' else '2024→'})"
                preds[etiqueta] = np.expm1(pr.log_media + mdl.predict(pr[FEATS])).clip(lower=0)
            for m, p in preds.items():
                filas.append(pr[k + ["observado"]].assign(metodo=m, prediccion=np.asarray(p)))
    r = pd.concat(filas, ignore_index=True)
    r["abs"] = (r.prediccion - r.observado).abs()
    w = lambda g: 100 * g["abs"].sum() / g.observado.sum()
    general = r.groupby("metodo").apply(w, include_groups=False).rename("WAPE_todos").to_frame()
    general = general.join(r.groupby(["metodo", "tipo_dia"]).apply(w, include_groups=False).unstack())
    general = general.join(r.groupby(["metodo", "periodo"]).apply(w, include_groups=False).unstack())
    general["n"] = r.groupby("metodo").size()
    # bootstrap pareado vs media histórica
    ancho = r.pivot_table(index=k, columns="metodo", values="prediccion")
    obs = r.drop_duplicates(k).set_index(k).observado.reindex(ancho.index).to_numpy()
    rng = np.random.default_rng(42)
    gr = [np.flatnonzero(ancho.index.get_level_values("periodo") == p) for p in a.PRUEBAS]
    idx = np.stack([np.concatenate([rng.choice(g, len(g)) for g in gr]) for _ in range(2000)])
    o = obs[idx]
    W = {c: 100 * np.abs(ancho[c].to_numpy()[idx] - o).sum(1) / o.sum(1) for c in ancho}
    ref = W["Media histórica (2024→)"]
    general["dif_vs_media"] = [np.mean(W[m] - ref) for m in general.index]
    general["dif_IC95_inf"] = [np.percentile(W[m] - ref, 2.5) for m in general.index]
    general["dif_IC95_sup"] = [np.percentile(W[m] - ref, 97.5) for m in general.index]
    lab = np.flatnonzero(ancho.index.get_level_values("tipo_dia") == "LABORAL")
    gl = [np.intersect1d(g, lab) for g in gr]
    il = np.stack([np.concatenate([rng.choice(g, len(g)) for g in gl]) for _ in range(2000)])
    ol = obs[il]
    WL = {c: 100 * np.abs(ancho[c].to_numpy()[il] - ol).sum(1) / ol.sum(1) for c in ancho}
    rl = WL["Media histórica (2024→)"]
    general["dif_laboral_IC95_inf"] = [np.percentile(WL[m] - rl, 2.5) for m in general.index]
    general["dif_laboral_IC95_sup"] = [np.percentile(WL[m] - rl, 97.5) for m in general.index]
    general = general.sort_values("WAPE_todos")
    SALIDA.mkdir(parents=True, exist_ok=True)
    general.to_csv(SALIDA / "modelo_unico.csv")
    pd.set_option("display.width", 250)
    print(general.round(2).to_string())


if __name__ == "__main__":
    main()
