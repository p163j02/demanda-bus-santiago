"""Hito 2c: sensibilidad al historial ampliado con las Subidas laborales de 2023.

Los libros de 2023 (abr, ago, nov) solo traen promedio LABORAL y no tienen columna de modo.
Filtro BUS (provisional, documentado en revision_datos_2023.md): filas con paradero de bus
o con servicio Sonda que empieza por T/F/B. Se excluyen líneas de Metro (L*) y Metrotren.
Una comuna sin ningún valor en una franja queda AUSENTE (no cero): la franja sectorial se
marca incompleta, igual que en el panel 2024-2026.

Comparación: mismas franjas LABORALES de las pruebas 2025-11 y 2026-04, con
  A) historial original (2024-11 en adelante)
  B) historial ampliado (2023-04, 2023-08, 2023-11 + original)
"""
from pathlib import Path
import sys
import zipfile
import io
import tempfile

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Etapa_02/codigo"))
from analisis_sectores import SECTORES  # noqa: E402

FUENTES = {
    "2023-04": "Tablas de Subidas y Bajadas_abr2023.zip",
    "2023-08": "Tablas de subidas y bajadas ago23.zip",
    "2023-11": "Tablas de subidas y bajadas nov23.zip",
}
CANON = {"NUNOA": "ÑUÑOA", "SAN JOAQUIN": "SAN JOAQUÍN", "SAN RAMON": "SAN RAMÓN"}
MAPA = {c: s for s, cs in SECTORES.items() for c in cs}
SALIDA = ROOT / "Etapa_03/resultados/hito_2c"
PRUEBAS = ["2025-11", "2026-04"]
FRANJAS = [f"{m // 60:02d}:{m % 60:02d}" for m in range(0, 1440, 30)]
GB_PARAMS = dict(max_depth=2, learning_rate=0.03, max_iter=100, min_samples_leaf=10)  # ajustados en hito_2b
FEATURES = ["log_media", "log_ultimo", "hora_sin", "hora_cos", "temporada_nov", "sector_sur"]


def leer_2023(periodo, nombre_zip):
    with zipfile.ZipFile(ROOT / "Datos/Fuentes/Subidas" / nombre_zip) as z:
        miembro = next(n for n in z.namelist() if "Matriz_sub" in n and n.endswith(".xlsb"))
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "sub.xlsb"
            ruta.write_bytes(z.read(miembro))
            d = pd.read_excel(ruta, sheet_name="subidas_prom_laboral", engine="pyxlsb", header=1)
    servicio = d["servicio Sonda"].astype("string")
    es_bus = (d.paradero.notna() | servicio.str.match(r"^[TFB]", na=False)) & \
        ~servicio.str.match(r"^(L\d|METROTREN)", na=False)
    d = d[es_bus].copy()
    d["comuna"] = d.Comuna.astype("string").str.strip().str.upper().replace(CANON)
    d = d[d.comuna.isin(MAPA)]
    horas = [c for c in d.columns if isinstance(c, str) and c.count(":") == 2]
    assert len(horas) == 48, horas
    largo = d.melt(id_vars="comuna", value_vars=horas, var_name="h", value_name="v")
    largo["media_hora"] = largo.h.map(lambda h: f"{int(h.split(':')[0]):02d}:{h.split(':')[1]}")
    largo["v"] = pd.to_numeric(largo.v, errors="coerce")
    agg = largo.groupby(["comuna", "media_hora"]).v.agg(lambda s: s.sum() if s.notna().any() else np.nan)
    rejilla = pd.MultiIndex.from_product([sorted(MAPA), FRANJAS], names=["comuna", "media_hora"])
    agg = agg.reindex(rejilla).reset_index(name="subidas")
    agg["periodo"] = periodo
    return agg, int(es_bus.sum())


def perfil_sectorial(comunal):
    comunal = comunal.assign(sector=comunal.comuna.map(MAPA))
    return comunal.groupby(["periodo", "sector", "media_hora"]).agg(
        observado=("subidas", lambda s: s.sum() if s.notna().all() else np.nan)).reset_index()


def panel_actual_laboral():
    p = pd.read_csv(ROOT / "Etapa_02/resultados/panel_demanda_bus_modelo.csv")
    p = p[p.tipo_dia.eq("LABORAL") & p.comuna.isin(MAPA)].copy()
    p["subidas"] = p.subidas_promedio.where(p.relleno_cero.eq(0))  # ausencia != cero
    return p[["periodo", "comuna", "media_hora", "subidas"]]


def features(perfil):
    """Media histórica y último observado usando solo cortes completos anteriores."""
    perfil = perfil.sort_values("periodo")
    filas = []
    for (sector, franja), g in perfil.groupby(["sector", "media_hora"]):
        hist = []
        for _, r in g.iterrows():
            if hist:
                filas.append(dict(periodo=r.periodo, sector=sector, media_hora=franja, observado=r.observado,
                                  media=np.mean(hist), ultimo=hist[-1], n_hist=len(hist)))
            if pd.notna(r.observado):
                hist.append(r.observado)
    t = pd.DataFrame(filas)
    minutos = t.media_hora.str[:2].astype(int) * 60 + t.media_hora.str[3:].astype(int)
    t["hora_sin"], t["hora_cos"] = np.sin(2 * np.pi * minutos / 1440), np.cos(2 * np.pi * minutos / 1440)
    t["log_media"], t["log_ultimo"] = np.log1p(t.media), np.log1p(t.ultimo)
    t["temporada_nov"] = t.periodo.str.endswith("-11").astype(int)
    t["sector_sur"] = t.sector.eq("Sur").astype(int)
    return t


def evaluar(t, filas_objetivo, historial):
    out = []
    for corte in PRUEBAS:
        entreno = t[t.periodo.lt(corte) & t.observado.notna()]
        prueba = t[t.periodo.eq(corte)].merge(filas_objetivo[filas_objetivo.periodo.eq(corte)],
                                              on=["periodo", "sector", "media_hora"])
        y = np.log1p(entreno.observado) - entreno.log_media
        preds = {"Media histórica": prueba.media, "Último observado": prueba.ultimo}
        for nombre, modelo in [("Ridge (log)", Ridge(alpha=10)),
                               ("Gradient Boosting (log)", HistGradientBoostingRegressor(random_state=0, **GB_PARAMS))]:
            modelo.fit(entreno[FEATURES], y)
            preds[nombre] = np.expm1(prueba.log_media + modelo.predict(prueba[FEATURES])).clip(lower=0)
        for m, p in preds.items():
            out.append(prueba[["periodo", "sector", "media_hora", "observado"]].assign(
                metodo=m, prediccion=np.asarray(p), historial=historial,
                n_entreno=len(entreno), cortes_historial=prueba.n_hist.to_numpy()))
    return pd.concat(out, ignore_index=True)


def main():
    leidos = [leer_2023(p, z) for p, z in FUENTES.items()]
    c2023 = pd.concat([l[0] for l in leidos])
    actual = panel_actual_laboral()
    perfil_orig = perfil_sectorial(actual)
    perfil_amp = perfil_sectorial(pd.concat([c2023, actual]))
    t_orig, t_amp = features(perfil_orig), features(perfil_amp)
    # Mismas filas: completas en el objetivo y con historial en ambas versiones.
    claves = ["periodo", "sector", "media_hora"]
    ok = t_orig[t_orig.periodo.isin(PRUEBAS) & t_orig.observado.notna()][claves].merge(
        t_amp[t_amp.periodo.isin(PRUEBAS) & t_amp.observado.notna()][claves])
    res = pd.concat([evaluar(t_orig, ok, "Original (2024-11 →)"),
                     evaluar(t_amp, ok, "Ampliado (2023-04 →)")])
    res["abs"] = (res.prediccion - res.observado).abs()
    res["err"] = res.prediccion - res.observado
    resumen = res.groupby(["historial", "metodo"]).apply(lambda g: pd.Series(dict(
        n=len(g), WAPE_pct=100 * g["abs"].sum() / g.observado.sum(),
        sesgo_pct=100 * g.err.sum() / g.observado.sum(),
        n_entreno_ultimo_corte=int(g.n_entreno.max()))), include_groups=False).reset_index()
    por_corte = res.groupby(["historial", "periodo", "metodo"]).apply(
        lambda g: 100 * g["abs"].sum() / g.observado.sum(), include_groups=False).rename("WAPE_pct").reset_index()
    cobertura = perfil_amp[perfil_amp.periodo.str.startswith("2023")].groupby(["periodo", "sector"]).observado.apply(
        lambda s: int(s.notna().sum())).rename("franjas_completas_de_48").reset_index()
    # Volumen comparable: solo franjas completas en TODOS los cortes del sector.
    comunes = perfil_amp.groupby(["sector", "media_hora"]).observado.transform(lambda s: s.notna().all())
    niveles = perfil_amp[comunes].groupby(["periodo", "sector"]).observado.sum().unstack().round(0)
    # Bootstrap pareado (mismas franjas, remuestreo dentro de cada corte) contra la referencia:
    # media histórica con historial original, que es el modelo seleccionado en la evaluación principal.
    res["clave"] = res.historial + " | " + res.metodo
    ancho = res.pivot_table(index=claves, columns="clave", values="prediccion")
    obs = res.drop_duplicates(claves).set_index(claves).observado.reindex(ancho.index).to_numpy()
    ref = "Original (2024-11 →) | Media histórica"
    rng = np.random.default_rng(42)
    grupos = [np.flatnonzero(ancho.index.get_level_values("periodo") == p) for p in PRUEBAS]
    idx = np.stack([np.concatenate([rng.choice(g, len(g)) for g in grupos]) for _ in range(2000)])
    o = obs[idx]
    w = {c: 100 * np.abs(ancho[c].to_numpy()[idx] - o).sum(1) / o.sum(1) for c in ancho.columns}
    ic = pd.DataFrame([dict(clave=c, WAPE_IC95_inf=np.percentile(v, 2.5), WAPE_IC95_sup=np.percentile(v, 97.5),
                            dif_vs_seleccionado=np.mean(v - w[ref]),
                            dif_IC95_inf=np.percentile(v - w[ref], 2.5), dif_IC95_sup=np.percentile(v - w[ref], 97.5))
                       for c, v in w.items()])
    resumen["clave"] = resumen.historial + " | " + resumen.metodo
    resumen = resumen.merge(ic, on="clave").drop(columns="clave").sort_values("WAPE_pct")
    SALIDA.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(SALIDA / "resumen_sensibilidad.csv", index=False)
    por_corte.to_csv(SALIDA / "wape_por_corte.csv", index=False)
    cobertura.to_csv(SALIDA / "cobertura_2023.csv", index=False)
    niveles.to_csv(SALIDA / "volumen_laboral_por_corte.csv")
    pd.set_option("display.width", 200)
    print("Filas BUS 2023:", [l[1] for l in leidos])
    print(cobertura.to_string(index=False))
    print("\nVolumen laboral sumado (franjas completas):\n", niveles)
    print("\n", resumen.round(2).to_string(index=False))
    print("\n", por_corte.pivot_table(index="metodo", columns=["historial", "periodo"], values="WAPE_pct").round(2))


if __name__ == "__main__":
    main()
