"""Hito 2: comparar baselines con modelos de ML usando validación temporal de origen móvil.

Idea: cada fila objetivo (periodo, sector, tipo_dia, franja) ya tiene dos pronósticos
calculados solo con cortes anteriores (Hito 1): media histórica y último observado.
Los modelos de ML aprenden a combinarlos y corregirlos con el contexto de la franja.

Validación (origen móvil, sin fuga temporal):
  - prueba 2025-11: entrena con objetivos de 2025-04
  - prueba 2026-04: entrena con objetivos de 2025-04 y 2025-11
Selección: WAPE conjunto de 2025-11 + 2026-04 (criterio fijado en el plan).
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Etapa_02/codigo"))
from analisis_sectores import etiquetar, SECTORES  # noqa: E402

ENTRADA = ROOT / "Etapa_03/resultados/hito_1/predicciones.csv"
SALIDA = ROOT / "Etapa_03/resultados/hito_2"
PRUEBAS = ["2025-11", "2026-04"]
N_COMUNAS = {s: len(c) for s, c in SECTORES.items()}


def construir_tabla():
    pred = pd.read_csv(ENTRADA)
    claves = ["periodo", "sector", "tipo_dia", "media_hora"]
    ancho = pred.pivot_table(index=claves, columns="metodo", values="prediccion", dropna=False).reset_index()
    ancho = ancho.rename(columns={"Media histórica": "media", "Último observado": "ultimo"})
    info = pred[pred.metodo.eq("Media histórica")][claves + ["observado", "cobertura_completa",
                                                           "n_antecedentes", "q1", "q2"]]
    tabla = info.merge(ancho, on=claves, validate="one_to_one")
    # Mismas filas evaluables que el Hito 1: objetivo completo y con historial.
    tabla = tabla[tabla.cobertura_completa & tabla.n_antecedentes.gt(0)
                  & tabla.observado.notna() & tabla.media.notna()].copy()
    minutos = tabla.media_hora.str[:2].astype(int) * 60 + tabla.media_hora.str[3:].astype(int)
    tabla["hora_sin"] = np.sin(2 * np.pi * minutos / 1440)
    tabla["hora_cos"] = np.cos(2 * np.pi * minutos / 1440)
    tabla["log_media"] = np.log1p(tabla.media)
    tabla["log_ultimo"] = np.log1p(tabla.ultimo)
    tabla["temporada_nov"] = tabla.periodo.str.endswith("-11").astype(int)
    for dia in ["LABORAL", "SABADO", "DOMINGO"]:
        tabla[f"dia_{dia}"] = tabla.tipo_dia.eq(dia).astype(int)
    tabla["sector_sur"] = tabla.sector.eq("Sur").astype(int)
    return tabla.reset_index(drop=True)


FEATURES = ["log_media", "log_ultimo", "hora_sin", "hora_cos", "temporada_nov",
            "dia_LABORAL", "dia_SABADO", "dia_DOMINGO", "sector_sur"]


def modelos():
    return {
        "Ridge (log)": lambda: RidgeCV(alphas=np.logspace(-3, 2, 20)),
        "Gradient Boosting (log)": lambda: HistGradientBoostingRegressor(
            max_iter=200, learning_rate=0.05, max_depth=3, min_samples_leaf=10, random_state=0),
    }


def predecir_ml(tabla):
    filas = []
    for corte in PRUEBAS:
        entreno = tabla[tabla.periodo.lt(corte)]
        prueba = tabla[tabla.periodo.eq(corte)]
        assert entreno.periodo.max() < corte, "Fuga temporal"
        # Objetivo: log del observado. Se modela el residuo sobre la media histórica.
        y = np.log1p(entreno.observado) - entreno.log_media
        for nombre, fabrica in modelos().items():
            modelo = fabrica().fit(entreno[FEATURES], y)
            p = np.expm1(prueba.log_media + modelo.predict(prueba[FEATURES])).clip(lower=0)
            filas.append(prueba.assign(metodo=nombre, prediccion=p.to_numpy(),
                                       n_entreno=len(entreno)))
        for nombre, col in [("Media histórica", "media"), ("Último observado", "ultimo")]:
            filas.append(prueba.assign(metodo=nombre, prediccion=prueba[col], n_entreno=len(entreno)))
    out = pd.concat(filas, ignore_index=True)
    divisor = out.sector.map(N_COMUNAS)
    out["etiqueta_real"] = [etiquetar(v, 0, a, b) for v, a, b in zip(out.observado / divisor, out.q1, out.q2)]
    out["etiqueta_predicha"] = [etiquetar(v, 0, a, b) for v, a, b in zip(out.prediccion / divisor, out.q1, out.q2)]
    return out


def metricas(g):
    err = g.prediccion - g.observado
    altos = g.etiqueta_real.eq("Alto")
    return pd.Series(dict(
        n=len(g), MAE=err.abs().mean(),
        WAPE_pct=100 * err.abs().sum() / g.observado.sum(),
        sesgo_pct=100 * err.sum() / g.observado.sum(),  # >0 sobreestima
        acierto_etiqueta_pct=100 * g.etiqueta_real.eq(g.etiqueta_predicha).mean(),
        altos_reales=int(altos.sum()),
        altos_detectados=int((altos & g.etiqueta_predicha.eq("Alto")).sum()),
        subestimacion_altos_pct=100 * (-err[altos]).clip(lower=0).sum() / max(g.observado[altos].sum(), 1),
    ))


def main():
    tabla = construir_tabla()
    pred = predecir_ml(tabla)
    agrupar = lambda claves: pred.groupby(claves, sort=False).apply(metricas, include_groups=False).reset_index()
    por_corte = agrupar(["periodo", "sector", "metodo"])
    por_dia = agrupar(["periodo", "tipo_dia", "metodo"])
    conjunto = agrupar(["metodo"]).sort_values("WAPE_pct")
    # Robustez: WAPE por corte, para ver si el ganador es consistente.
    estabilidad = agrupar(["periodo", "metodo"]).pivot(index="metodo", columns="periodo", values="WAPE_pct")
    ganador = conjunto.iloc[0].metodo
    seleccion = dict(
        criterio="Menor WAPE conjunto 2025-11 + 2026-04 (validación de origen móvil)",
        modelo_seleccionado=ganador,
        ranking=conjunto[["metodo", "WAPE_pct", "MAE", "sesgo_pct", "acierto_etiqueta_pct"]].round(3).to_dict("records"),
        wape_por_corte=estabilidad.round(3).to_dict(),
        gana_en_ambos_cortes=bool((estabilidad.idxmin() == ganador).all()),
        features=FEATURES,
    )
    SALIDA.mkdir(parents=True, exist_ok=True)
    pred.to_csv(SALIDA / "predicciones_modelos.csv", index=False)
    por_corte.to_csv(SALIDA / "metricas_por_corte.csv", index=False)
    por_dia.to_csv(SALIDA / "metricas_por_tipo_dia.csv", index=False)
    conjunto.to_csv(SALIDA / "metricas_conjuntas.csv", index=False)
    (SALIDA / "seleccion.json").write_text(json.dumps(seleccion, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.set_option("display.width", 200)
    print(conjunto.round(2).to_string(index=False))
    print("\nWAPE por corte:\n", estabilidad.round(2))
    print("\nSeleccionado:", ganador, "| gana en ambos cortes:", seleccion["gana_en_ambos_cortes"])


if __name__ == "__main__":
    main()
