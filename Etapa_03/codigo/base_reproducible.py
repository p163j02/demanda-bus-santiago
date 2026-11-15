"""Hito 1: auditar el panel y reproducir las referencias sectoriales de etapa 2."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
# Reutilizar funciones protegidas por main, sin ejecutar los análisis anteriores.
sys.path.insert(0, str(ROOT / "Etapa_02/codigo"))
from pronostico_sectorial_simple import METODOS, pronosticar
from analisis_sectores import CLASES, CLAVES, SECTORES, etiquetar

PERIODOS = ["2024-11", "2025-04", "2025-11", "2026-04"]
DIAS = ["DOMINGO", "LABORAL", "SABADO"]
CLAVES_COMUNA = ["periodo", "comuna", "tipo_dia", "media_hora"]
SALIDA = ROOT / "Etapa_03/resultados/hito_1"


def cargar_base():
    entrada = ROOT / "Etapa_02/resultados"
    panel = pd.read_csv(entrada / "panel_demanda_bus_modelo.csv")
    observado = pd.read_csv(entrada / "panel_demanda_bus.csv")
    assert not panel.isna().any().any(), "El panel contiene valores ausentes"
    assert not panel.duplicated(CLAVES_COMUNA).any(), "Claves comunales duplicadas"
    assert not observado.duplicated(CLAVES_COMUNA).any()
    assert np.isfinite(panel.subidas_promedio).all() and panel.subidas_promedio.ge(0).all()
    assert panel.relleno_cero.isin([0, 1]).all(), "Marca de ausencia inválida"
    franjas = [f"{m // 60:02d}:{m % 60:02d}" for m in range(0, 1440, 30)]
    rejilla = pd.MultiIndex.from_product(
        [PERIODOS, sorted(panel.comuna.unique()), DIAS, franjas], names=CLAVES_COMUNA)
    assert len(panel.comuna.unique()) == 36 and "SIN_COMUNA" not in set(panel.comuna)
    assert pd.MultiIndex.from_frame(panel[CLAVES_COMUNA]).sort_values().equals(rejilla.sort_values())
    cotejo = panel.merge(observado, on=CLAVES_COMUNA, how="left", validate="one_to_one",
                         suffixes=("", "_fuente"), indicator=True)
    assert cotejo.relleno_cero.eq(1).equals(cotejo._merge.eq("left_only")), "Ausencias mal marcadas"
    presentes = cotejo.relleno_cero.eq(0)
    np.testing.assert_allclose(cotejo.loc[presentes, "subidas_promedio"],
                               cotejo.loc[presentes, "subidas_promedio_fuente"], rtol=1e-9)
    assert cotejo.loc[~presentes, "subidas_promedio"].eq(0).all()
    mapa = {c: s for s, comunas in SECTORES.items() for c in comunas}
    assert len(mapa) == 16 and set(mapa) <= set(panel.comuna)
    sectorial = panel[panel.comuna.isin(mapa)].copy()
    sectorial["sector"] = sectorial.comuna.map(mapa)
    perfil = sectorial.groupby(CLAVES, as_index=False).agg(
        subidas_sector=("subidas_promedio", "sum"),
        promedio_por_comuna=("subidas_promedio", "mean"),
        comunas_ausentes=("relleno_cero", "sum"), n_comunas=("comuna", "size"))
    assert len(perfil) == 2 * 4 * 3 * 48
    assert perfil.n_comunas.eq(perfil.sector.map({s: len(cs) for s, cs in SECTORES.items()})).all()
    perfil["cobertura_completa"] = perfil.comunas_ausentes.eq(0)
    return panel, sectorial, perfil


def metricas_grupo(grupo):
    error = (grupo.prediccion - grupo.observado).abs()
    total = grupo.observado.sum()
    altos = grupo.etiqueta_real.eq("Alto")
    return dict(n=len(grupo), MAE=float(error.mean()),
                WAPE_pct=float(100 * error.sum() / total) if total > 0 else np.nan,
                acierto_etiqueta_pct=float(100 * grupo.etiqueta_real.eq(grupo.etiqueta_predicha).mean()),
                altos_reales=int(altos.sum()),
                altos_detectados=int((altos & grupo.etiqueta_predicha.eq("Alto")).sum()))


def cobertura_predicciones(pred, claves):
    filas = []
    for valores, grupo in pred.groupby(claves, sort=False):
        completa = grupo.cobertura_completa
        historial = grupo.n_antecedentes.gt(0)
        fila = dict(zip(claves, valores), n_total=len(grupo),
                    n_evaluadas=int((completa & historial).sum()),
                    n_incompletas=int((~completa).sum()),
                    n_sin_historial=int((completa & ~historial).sum()))
        assert fila["n_total"] == sum(fila[k] for k in ["n_evaluadas", "n_incompletas", "n_sin_historial"])
        for nombre in ["evaluadas", "incompletas", "sin_historial"]:
            fila[f"pct_{nombre}"] = 100 * fila[f"n_{nombre}"] / fila["n_total"]
        filas.append(fila)
    return pd.DataFrame(filas)


def perfil_para_interpretar(perfil):
    salida = perfil.copy()
    salida.loc[~salida.cobertura_completa, ["subidas_sector", "promedio_por_comuna"]] = np.nan
    claves_dia = ["periodo", "sector", "tipo_dia"]
    completa = salida.groupby(claves_dia).cobertura_completa.transform("all")
    total = salida.groupby(claves_dia).subidas_sector.transform("sum")
    salida["participacion_diaria_pct"] = (100 * salida.subidas_sector / total.where(total.gt(0))).where(completa)
    return salida


def comprobar_temporalidad(perfil, pred):
    columnas = ["prediccion", "q1", "q2", "n_antecedentes", "ultimo_antecedente"]
    for corte in PERIODOS[1:]:
        alterado = perfil.copy()
        futuro = alterado.periodo.ge(corte)
        alterado.loc[futuro, ["subidas_sector", "promedio_por_comuna"]] *= 10
        alterado.loc[futuro, "cobertura_completa"] = ~alterado.loc[futuro, "cobertura_completa"]
        pd.testing.assert_frame_equal(pronosticar(perfil, corte)[columnas],
                                      pronosticar(alterado, corte)[columnas])
    anteriores = pred.ultimo_antecedente.notna()
    assert pred.loc[anteriores, "ultimo_antecedente"].lt(pred.loc[anteriores, "periodo"]).all()
    primero = pred[pred.periodo.eq(PERIODOS[1])]
    pd.testing.assert_frame_equal(
        primero[primero.metodo.eq(METODOS[0])].drop(columns="metodo").reset_index(drop=True),
        primero[primero.metodo.eq(METODOS[1])].drop(columns="metodo").reset_index(drop=True))


def main():
    panel, sectorial, perfil = cargar_base()
    pred = pd.concat([pronosticar(perfil, corte) for corte in PERIODOS[1:]], ignore_index=True)
    comprobar_temporalidad(perfil, pred)
    evaluables = pred[pred.observado.notna() & pred.prediccion.notna()]
    assert np.isfinite(evaluables[["observado", "prediccion"]]).all().all()
    claves = ["periodo", "sector", "metodo"]
    metricas = pd.DataFrame([dict(zip(claves, valores), **metricas_grupo(grupo))
                            for valores, grupo in evaluables.groupby(claves, sort=False)])
    filas = ["periodo", "sector", "tipo_dia", "media_hora"]
    pd.testing.assert_frame_equal(
        evaluables[evaluables.metodo.eq(METODOS[0])][filas].reset_index(drop=True),
        evaluables[evaluables.metodo.eq(METODOS[1])][filas].reset_index(drop=True))
    antecedente = ROOT / "Etapa_02/resultados/sectorial_simple"
    pd.testing.assert_frame_equal(metricas, pd.read_csv(antecedente / "metricas.csv"), rtol=1e-9, atol=1e-8)
    pd.testing.assert_frame_equal(pred, pd.read_csv(antecedente / "predicciones.csv"), rtol=1e-9, atol=1e-8)
    final = evaluables[evaluables.periodo.eq(PERIODOS[-1]) & evaluables.metodo.eq(METODOS[0])]
    confusion = pd.crosstab([final.sector, final.etiqueta_real], final.etiqueta_predicha).reindex(
        pd.MultiIndex.from_product([SECTORES, CLASES], names=["sector", "etiqueta_real"]), fill_value=0
    ).reindex(columns=CLASES, fill_value=0)
    assert confusion.to_numpy().sum() == len(final)
    for sector in SECTORES:
        matriz = confusion.loc[sector]
        metrica = metricas[metricas.periodo.eq(PERIODOS[-1]) &
                           metricas.sector.eq(sector) & metricas.metodo.eq(METODOS[0])].iloc[0]
        assert matriz.to_numpy().sum() == metrica.n
        assert matriz.loc["Alto"].sum() == metrica.altos_reales
        assert matriz.loc["Alto", "Alto"] == metrica.altos_detectados
        np.testing.assert_allclose(100 * np.trace(matriz.to_numpy()) / metrica.n,
                                   metrica.acierto_etiqueta_pct)
    pd.testing.assert_frame_equal(confusion, pd.read_csv(
        antecedente / "confusion_etiquetas_abril_2026.csv", index_col=[0, 1]), check_names=False)
    cobertura = cobertura_predicciones(pred[pred.metodo.eq(METODOS[0])], ["periodo", "sector"])
    cobertura_dia = cobertura_predicciones(pred[pred.metodo.eq(METODOS[0])], ["periodo", "sector", "tipo_dia"])
    perfil_salida = perfil_para_interpretar(perfil)
    q1, q2 = pred.loc[pred.periodo.eq(PERIODOS[-1]), ["q1", "q2"]].iloc[0]
    perfil_salida["etiqueta"] = [etiquetar(v, f, q1, q2) for v, f in
                                 zip(perfil.promedio_por_comuna, perfil.comunas_ausentes)]
    entradas = [ROOT / "Etapa_02/resultados" / nombre for nombre in
                ["panel_demanda_bus_modelo.csv", "panel_demanda_bus.csv", "panel_quality_report.json"]]
    reporte = dict(
        n_celdas_panel=len(panel), n_celdas_comunales_sectores=len(sectorial),
        n_celdas_sectoriales=len(perfil), ceros_anadidos_panel=int(panel.relleno_cero.sum()),
        ceros_anadidos_sectores=int(sectorial.relleno_cero.sum()),
        ceros_observados_comunales_sectores=int((sectorial.relleno_cero.eq(0) & sectorial.subidas_promedio.eq(0)).sum()),
        nulos_sectoriales_confirmados=int((perfil.cobertura_completa & perfil.subidas_sector.eq(0)).sum()),
        sectores=SECTORES, periodos=PERIODOS,
        entradas_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in entradas},
        entorno=dict(python=sys.version.split()[0], pandas=pd.__version__, numpy=np.__version__),
        reproduccion="Predicciones, métricas y matriz de etapa 2 coinciden (rtol=1e-9, atol=1e-8).",
        alcance_auditoria="Paneles incluidos contrastados entre sí; libros originales no releídos.")
    # Escribir solo después de superar todos los controles, sin sobrescribir etapa 2.
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, frame in [("perfil_sectorial.csv", perfil_salida), ("predicciones.csv", pred),
                          ("metricas.csv", metricas), ("cobertura.csv", cobertura),
                          ("cobertura_por_tipo_dia.csv", cobertura_dia)]:
        frame.to_csv(SALIDA / nombre, index=False)
    confusion.to_csv(SALIDA / "confusion_etiquetas_abril_2026.csv")
    (SALIDA / "auditoria_panel.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
    print(cobertura.to_string(index=False))
    print(metricas[metricas.periodo.eq(PERIODOS[-1])].to_string(index=False))
    print("Hito 1: auditoría, reproducción y temporalidad OK.")


if __name__ == "__main__":
    main()
