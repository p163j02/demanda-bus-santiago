"""Hito 3: figuras para la presentación técnica, a partir de resultados/hito_2."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ENTRADA = ROOT / "Etapa_03/resultados/hito_2"
SALIDA = ROOT / "Etapa_03/resultados/figuras"
ORDEN = ["Media histórica", "Último observado", "Ridge (log)", "Gradient Boosting (log)"]
COLOR = {"Media histórica": "#1f6f8b", "Último observado": "#9aa5b1",
         "Ridge (log)": "#e3a33b", "Gradient Boosting (log)": "#c0504d"}
CLASES = ["Nulo", "Bajo", "Medio", "Alto"]
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def barras_agrupadas(ax, tabla, grupos, titulo, ylabel="WAPE (%)"):
    ancho = 0.8 / len(ORDEN)
    x = np.arange(len(grupos))
    for i, m in enumerate(ORDEN):
        vals = [tabla.loc[(g, m)] for g in grupos]
        barras = ax.bar(x + (i - 1.5) * ancho, vals, ancho, label=m, color=COLOR[m])
        ax.bar_label(barras, fmt="%.1f", fontsize=8)
    ax.set_xticks(x, grupos)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo, loc="left", fontweight="bold")


def fig_wape_por_corte(pred, conj):
    cortes = sorted(pred.periodo.unique())
    tabla = {}
    for (p, m), g in pred.groupby(["periodo", "metodo"]):
        tabla[(p, m)] = 100 * (g.prediccion - g.observado).abs().sum() / g.observado.sum()
    for m in ORDEN:
        tabla[("Conjunto", m)] = conj.set_index("metodo").loc[m, "WAPE_pct"]
    fig, ax = plt.subplots(figsize=(10, 5))
    barras_agrupadas(ax, pd.Series(tabla), cortes + ["Conjunto"],
                     "Error de pronóstico por corte de prueba (menor es mejor)")
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(SALIDA / "01_wape_por_corte.png", dpi=160)


def fig_wape_por_dia(dia):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, corte in zip(axes, sorted(dia.periodo.unique())):
        t = dia[dia.periodo.eq(corte)].set_index(["tipo_dia", "metodo"]).WAPE_pct
        barras_agrupadas(ax, t, ["LABORAL", "SABADO", "DOMINGO"], f"Prueba {corte}")
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle("WAPE por tipo de día: los domingos concentran el error", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(SALIDA / "02_wape_por_tipo_dia.png", dpi=160)


def fig_curvas(pred, corte="2026-04", dia="LABORAL"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    for ax, sector in zip(axes, ["Oriente", "Sur"]):
        sub = pred[pred.periodo.eq(corte) & pred.tipo_dia.eq(dia) & pred.sector.eq(sector)]
        obs = sub[sub.metodo.eq(ORDEN[0])].sort_values("media_hora")
        ax.plot(obs.media_hora, obs.observado, color="black", lw=2.2, label="Observado")
        for m in ["Media histórica", "Gradient Boosting (log)"]:
            s = sub[sub.metodo.eq(m)].sort_values("media_hora")
            ax.plot(s.media_hora, s.prediccion, color=COLOR[m], lw=1.6, ls="--", label=m)
        ax.set_title(f"{sector} — {dia.lower()}, {corte}", loc="left", fontweight="bold")
        ax.set_xticks(obs.media_hora[::4])
        ax.tick_params(axis="x", rotation=60)
        ax.set_ylabel("Subidas por franja de 30 min")
    axes[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDA / "03_curvas_observado_vs_pronostico.png", dpi=160)


def fig_confusion(pred, metodo="Media histórica", corte="2026-04"):
    sub = pred[pred.periodo.eq(corte) & pred.metodo.eq(metodo)]
    m = pd.crosstab(sub.etiqueta_real, sub.etiqueta_predicha).reindex(index=CLASES, columns=CLASES, fill_value=0)
    m = m.loc[m.sum(axis=1).gt(0) | m.sum(axis=0).gt(0), m.sum(axis=0).gt(0) | m.sum(axis=1).gt(0)]
    fig, ax = plt.subplots(figsize=(5, 4.3))
    ax.imshow(m.to_numpy(), cmap="Blues")
    for (i, j), v in np.ndenumerate(m.to_numpy()):
        ax.text(j, i, v, ha="center", va="center", color="white" if v > m.to_numpy().max() / 2 else "black")
    ax.set_xticks(range(m.shape[1]), m.columns)
    ax.set_yticks(range(m.shape[0]), m.index)
    ax.set_xlabel("Etiqueta pronosticada")
    ax.set_ylabel("Etiqueta real")
    ax.set_title(f"Intensidad horaria — {metodo}, {corte}", loc="left", fontsize=10, fontweight="bold")
    fig.tight_layout()
    fig.savefig(SALIDA / "04_confusion_modelo_final.png", dpi=160)


def fig_bootstrap(boot):
    b = boot.set_index("metodo").loc[ORDEN[::-1]]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for i, (m, r) in enumerate(b.iterrows()):
        ax.plot([r.IC95_inf, r.IC95_sup], [i, i], color=COLOR[m], lw=6, solid_capstyle="round")
        ax.plot(r.WAPE_pct, i, "o", color="black", ms=8)
        ax.text(r.IC95_sup + 0.15, i, f"{r.WAPE_pct:.2f} % [{r.IC95_inf:.1f}–{r.IC95_sup:.1f}]", va="center", fontsize=10)
    ax.set_yticks(range(len(b)), b.index)
    ax.set_xlabel("WAPE conjunto (%) con intervalo de confianza 95 % (bootstrap, 2.000 remuestreos)")
    ax.set_xlim(5.5, 12.5)
    ax.set_title("Media histórica y Ridge se solapan: empate estadístico", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(SALIDA / "05_bootstrap_ic95.png", dpi=160)


def fig_residuos(res):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bloques = list(dict.fromkeys(res.bloque))
    x = np.arange(len(bloques))
    for k, (sector, color) in enumerate([("Oriente", "#1f6f8b"), ("Sur", "#e3a33b")]):
        v = res[res.sector.eq(sector)].set_index("bloque").reindex(bloques).sesgo_pct
        b = ax.bar(x + (k - 0.5) * 0.38, v, 0.38, label=sector, color=color)
        ax.bar_label(b, fmt="%.1f", fontsize=9)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x, bloques)
    ax.set_ylabel("Sesgo (%)  <0 = subestima")
    ax.set_title("El modelo final subestima levemente en todos los bloques", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDA / "06_sesgo_por_bloque.png", dpi=160)


def fig_ampliacion(res, vol):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw=dict(width_ratios=[1.6, 1]))
    hist = ["Original (2024-11 →)", "Ampliado (2023-04 →)"]
    t = res.set_index(["historial", "metodo"]).WAPE_pct
    x = np.arange(len(ORDEN))
    for k, (h, c) in enumerate(zip(hist, ["#9aa5b1", "#1f6f8b"])):
        b = a1.bar(x + (k - 0.5) * 0.38, [t[(h, m)] for m in ORDEN], 0.38, label=h, color=c)
        a1.bar_label(b, fmt="%.1f", fontsize=9)
    a1.set_xticks(x, [m.replace(" (log)", "") for m in ORDEN], fontsize=10)
    a1.set_ylabel("WAPE laboral (%)")
    a1.set_title("Más historia: el ML mejora, la media empeora", loc="left", fontweight="bold")
    a1.legend(frameon=False, title="Historial")
    v = vol.set_index("periodo")
    for s, c in [("Oriente", "#1f6f8b"), ("Sur", "#e3a33b")]:
        a2.plot(v.index, v[s] / 1000, marker="o", color=c, label=s)
    a2.set_ylabel("Subidas laborales (miles)")
    a2.set_title("La demanda crece entre cortes", loc="left", fontweight="bold")
    a2.tick_params(axis="x", rotation=45)
    a2.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDA / "07_historial_ampliado.png", dpi=160)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    amp = ROOT / "Etapa_03/resultados/hito_2c"
    if amp.exists():
        fig_ampliacion(pd.read_csv(amp / "resumen_sensibilidad.csv"), pd.read_csv(amp / "volumen_laboral_por_corte.csv"))
    rob = ROOT / "Etapa_03/resultados/hito_2b"
    if rob.exists():
        fig_bootstrap(pd.read_csv(rob / "bootstrap_wape.csv"))
        fig_residuos(pd.read_csv(rob / "residuos_modelo_final.csv"))
    pred = pd.read_csv(ENTRADA / "predicciones_modelos.csv")
    conj = pd.read_csv(ENTRADA / "metricas_conjuntas.csv")
    dia = pd.read_csv(ENTRADA / "metricas_por_tipo_dia.csv")
    fig_wape_por_corte(pred, conj)
    fig_wape_por_dia(dia)
    fig_curvas(pred)
    fig_confusion(pred)
    print("Figuras en", SALIDA)


if __name__ == "__main__":
    main()
