"""Hito 2b: robustez de la validación.

1. RMSE además de MAE/WAPE.
2. Bootstrap por franja: IC 95 % del WAPE de cada método y de la diferencia con la media histórica.
3. Residuos: dónde y en qué dirección se equivoca el modelo final.
4. Ajuste de hiperparámetros con validación temporal anidada (entrena 2025-04, valida 2025-11)
   y prueba final en 2026-04; importancia de variables por permutación en 2026-04.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Etapa_03/codigo"))
from comparacion_modelos import FEATURES, construir_tabla  # noqa: E402

ENTRADA = ROOT / "Etapa_03/resultados/hito_2/predicciones_modelos.csv"
SALIDA = ROOT / "Etapa_03/resultados/hito_2b"
BASE = "Media histórica"
B = 2000
rng = np.random.default_rng(42)


def wape(err_abs, obs):
    return 100 * err_abs.sum(axis=-1) / obs.sum(axis=-1)


def bootstrap(pred):
    """Remuestrea franjas (las mismas para todos los métodos) dentro de cada corte."""
    claves = ["periodo", "sector", "tipo_dia", "media_hora"]
    ancho = pred.pivot_table(index=claves, columns="metodo", values="prediccion")
    obs = pred.drop_duplicates(claves).set_index(claves).observado.reindex(ancho.index).to_numpy()
    idx_por_corte = [np.flatnonzero(ancho.index.get_level_values("periodo") == p)
                     for p in sorted(pred.periodo.unique())]
    muestras = np.stack([np.concatenate([rng.choice(ix, len(ix)) for ix in idx_por_corte]) for _ in range(B)])
    o = obs[muestras]
    filas, w_base = [], None
    for m in ancho.columns:
        w = wape(np.abs(ancho[m].to_numpy()[muestras] - o), o)
        if m == BASE:
            w_base = w
        filas.append((m, w))
    out = []
    for m, w in filas:
        d = w - w_base
        out.append(dict(metodo=m, WAPE_pct=wape(np.abs(ancho[m].to_numpy() - obs), obs),
                        IC95_inf=np.percentile(w, 2.5), IC95_sup=np.percentile(w, 97.5),
                        dif_vs_media=np.mean(d), dif_IC95_inf=np.percentile(d, 2.5),
                        dif_IC95_sup=np.percentile(d, 97.5),
                        prob_mejor_que_media=float(np.mean(d < 0)) if m != BASE else np.nan))
    return pd.DataFrame(out).sort_values("WAPE_pct")


def rmse_tabla(pred):
    g = pred.assign(e2=(pred.prediccion - pred.observado) ** 2)
    return g.groupby("metodo").e2.mean().pow(0.5).rename("RMSE").reset_index()


def residuos(pred):
    f = pred[pred.metodo.eq(BASE)].copy()
    f["error"] = f.prediccion - f.observado
    f["hora"] = f.media_hora.str[:2].astype(int)
    f["bloque"] = pd.cut(f.hora, [-1, 5, 9, 16, 20, 23],
                         labels=["Noche 00-06", "Punta mañana 06-10", "Valle 10-17", "Punta tarde 17-21", "Noche 21-24"])
    return f.groupby(["sector", "bloque"], observed=True).agg(
        n=("error", "size"), error_medio=("error", "mean"),
        sesgo_pct=("error", lambda e: 100 * e.sum() / f.loc[e.index, "observado"].sum()),
        WAPE_pct=("error", lambda e: 100 * e.abs().sum() / f.loc[e.index, "observado"].sum()),
    ).reset_index()


GRILLAS = {
    "Ridge (log)": [dict(alpha=a) for a in [0.01, 0.1, 1, 10, 100]],
    "Gradient Boosting (log)": [dict(max_depth=d, learning_rate=lr, max_iter=it, min_samples_leaf=10)
                                for d in [2, 3, 4] for lr in [0.03, 0.1] for it in [100, 300]],
}


def crear(nombre, params):
    if nombre.startswith("Ridge"):
        return Ridge(**params)
    return HistGradientBoostingRegressor(random_state=0, **params)


def ajuste_e_importancia(tabla):
    def ajustar(df, nombre, params):
        return crear(nombre, params).fit(df[FEATURES], np.log1p(df.observado) - df.log_media)

    def wape_df(modelo, df):
        p = np.expm1(df.log_media + modelo.predict(df[FEATURES])).clip(lower=0)
        return float(100 * (p - df.observado).abs().sum() / df.observado.sum())

    entreno, valida, prueba = (tabla[tabla.periodo.eq(p)] for p in ["2025-04", "2025-11", "2026-04"])
    resumen, busqueda, importancias = [], [], []
    for nombre, grilla in GRILLAS.items():
        for params in grilla:
            busqueda.append(dict(metodo=nombre, params=json.dumps(params),
                                 WAPE_valid_2025_11=wape_df(ajustar(entreno, nombre, params), valida)))
        sub = [b for b in busqueda if b["metodo"] == nombre]
        mejor = json.loads(min(sub, key=lambda b: b["WAPE_valid_2025_11"])["params"])
        final = ajustar(pd.concat([entreno, valida]), nombre, mejor)
        resumen.append(dict(metodo=nombre, mejores_params=mejor, WAPE_prueba_2026_04=wape_df(final, prueba)))
        imp = permutation_importance(final, prueba[FEATURES], np.log1p(prueba.observado) - prueba.log_media,
                                     n_repeats=20, random_state=0, scoring="neg_mean_absolute_error")
        importancias += [dict(metodo=nombre, variable=v, importancia=m, desv=s)
                         for v, m, s in zip(FEATURES, imp.importances_mean, imp.importances_std)]
    base = prueba.media
    resumen.append(dict(metodo=BASE, mejores_params={},
                        WAPE_prueba_2026_04=float(100 * (base - prueba.observado).abs().sum() / prueba.observado.sum())))
    return pd.DataFrame(resumen), pd.DataFrame(busqueda), pd.DataFrame(importancias)


def sensibilidad_umbrales(pred):
    """Pendiente de la Etapa II: ¿cambia la conclusión si se mueven los umbrales ±10 % / ±20 %?"""
    sys.path.insert(0, str(ROOT / "Etapa_02/codigo"))
    from analisis_sectores import etiquetar, SECTORES
    n = pred.sector.map({s: len(c) for s, c in SECTORES.items()})
    filas = []
    for f in [0.8, 0.9, 1.0, 1.1, 1.2]:
        real = [etiquetar(v, 0, a * f, b * f) for v, a, b in zip(pred.observado / n, pred.q1, pred.q2)]
        prono = [etiquetar(v, 0, a * f, b * f) for v, a, b in zip(pred.prediccion / n, pred.q1, pred.q2)]
        t = pred.assign(real=real, prono=prono)
        for m, g in t.groupby("metodo"):
            altos = g.real.eq("Alto")
            filas.append(dict(factor_umbral=f, metodo=m, acierto_pct=100 * g.real.eq(g.prono).mean(),
                              recall_alto_pct=100 * (altos & g.prono.eq("Alto")).sum() / altos.sum()))
    return pd.DataFrame(filas)


def main():
    pred = pd.read_csv(ENTRADA)
    sens = sensibilidad_umbrales(pred)
    SALIDA.mkdir(parents=True, exist_ok=True)
    sens.to_csv(SALIDA / "sensibilidad_umbrales.csv", index=False)
    print(sens.pivot(index="metodo", columns="factor_umbral", values="acierto_pct").round(1))
    print(sens.pivot(index="metodo", columns="factor_umbral", values="recall_alto_pct").round(1))
    boot = bootstrap(pred).merge(rmse_tabla(pred), on="metodo")
    res = residuos(pred)
    ajuste, busqueda, imp = ajuste_e_importancia(construir_tabla())
    SALIDA.mkdir(parents=True, exist_ok=True)
    boot.to_csv(SALIDA / "bootstrap_wape.csv", index=False)
    res.to_csv(SALIDA / "residuos_modelo_final.csv", index=False)
    ajuste.to_csv(SALIDA / "ajuste_hiperparametros_resumen.csv", index=False)
    busqueda.to_csv(SALIDA / "ajuste_hiperparametros_grilla.csv", index=False)
    imp.to_csv(SALIDA / "importancia_variables.csv", index=False)
    pd.set_option("display.width", 220)
    print(boot.round(3).to_string(index=False))
    print("\n", res.round(1).to_string(index=False))
    print("\n", ajuste.to_string(index=False))
    print("\n", imp.sort_values(["metodo", "importancia"], ascending=[True, False]).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
