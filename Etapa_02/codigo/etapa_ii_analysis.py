# %% [markdown]
# # Etapa II — análisis exploratorio y primer modelo
#
# **Proyecto:** predicción de subidas registradas de buses por comuna y franja de 30 minutos.
#
# Este análisis usa el panel armonizado de las cuatro tablas históricas de Subidas. El objetivo es `Subidas_Promedio`, no una estimación de pasajeros evadiendo el pago. Los resultados de la Tabla de Etapas (abril de 2026) se deben presentar como análisis complementario, no mezclar con este target.
#
# El corte abril de 2026 se reserva como prueba temporal final. Las combinaciones ausentes del panel de modelamiento fueron provisionalmente completadas con cero y se identifican con `relleno_cero`; validar esa interpretación con la semántica de publicación del DTPM.

# %%
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore", category=UserWarning)


def find_project_root() -> Path:
    starts = [Path.cwd(), *Path.cwd().parents]
    candidates = []
    for start in starts:
        candidates.extend([start, start / "demanda-bus-santiago"])
    for candidate in candidates:
        if (candidate / "Etapa_02/resultados/panel_demanda_bus_modelo.csv").exists():
            return candidate
    raise FileNotFoundError(
        "No encontré Etapa_02/resultados/panel_demanda_bus_modelo.csv. "
        "Ejecuta antes Etapa_02/codigo/build_panel.py."
    )


PROJECT_ROOT = find_project_root()
PROCESSED_DIR = PROJECT_ROOT / "Etapa_02" / "resultados"
FIGURES_DIR = PROCESSED_DIR / "figuras"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

panel = pd.read_csv(PROCESSED_DIR / "panel_demanda_bus_modelo.csv")
panel["periodo"] = panel["periodo"].astype(str)
panel["subidas_promedio"] = pd.to_numeric(panel["subidas_promedio"], errors="raise")
panel["relleno_cero"] = panel["relleno_cero"].astype(int)
PERIODS = sorted(panel["periodo"].unique())
KEYS = ["comuna", "tipo_dia", "media_hora"]
TARGET = "subidas_promedio"

print(f"Proyecto: {PROJECT_ROOT}")
print(f"Filas: {len(panel):,} | períodos: {PERIODS}")
print(f"Comunas de cobertura común: {panel['comuna'].nunique()} | "
      f"celdas imputadas a cero: {panel['relleno_cero'].sum():,}")

# %% [markdown]
# ## 1. Control básico de calidad
#
# El panel de modelamiento debe contener 36 comunas comparables × 3 tipos de día × 48 franjas × 4 cortes. Se excluyó `SIN_COMUNA` y las comunas que no aparecen en los cuatro períodos.

# %%
expected_rows_per_period = panel["comuna"].nunique() * 3 * 48
coverage = panel.groupby("periodo").size().rename("filas").to_frame()
coverage["esperadas"] = expected_rows_per_period
coverage["n_comunas"] = panel.groupby("periodo")["comuna"].nunique()
coverage["celdas_rellenas_cero"] = panel.groupby("periodo")["relleno_cero"].sum()
print(coverage)
assert panel[KEYS + [TARGET, "periodo"]].notna().all().all()
assert coverage["filas"].eq(expected_rows_per_period).all()
assert len(PERIODS) == 4

# %% [markdown]
# ## 2. Análisis descriptivo
#
# Las magnitudes de las tablas históricas se describen como subidas registradas. No se interpretan como el total real de pasajeros ni se comparan numéricamente con la suma del factor de expansión de Etapas.

# %%
daily_totals = (
    panel.groupby(["periodo", "tipo_dia"], as_index=False)[TARGET]
    .sum()
    .rename(columns={TARGET: "subidas_agregadas"})
)
daily_totals["periodo"] = pd.Categorical(daily_totals["periodo"], categories=PERIODS, ordered=True)
daily_totals = daily_totals.sort_values(["tipo_dia", "periodo"])
print("Suma de subidas por tipo de día y corte (36 comunas comunes):")
print(daily_totals.to_string(index=False))

# Razón laboral/domingo por corte; interpreta con cautela por los cambios de fuente y cobertura.
pivot_days = daily_totals.pivot(index="periodo", columns="tipo_dia", values="subidas_agregadas")
pivot_days["razon_laboral_domingo"] = pivot_days["LABORAL"] / pivot_days["DOMINGO"]
print("\nRazón de subidas laborales / domingo:")
print(pivot_days[["razon_laboral_domingo"]].to_string())

fig, ax = plt.subplots(figsize=(9, 5))
for day in ["LABORAL", "SABADO", "DOMINGO"]:
    subset = daily_totals[daily_totals["tipo_dia"] == day]
    ax.plot(subset["periodo"].astype(str), subset["subidas_agregadas"], marker="o", label=day)
ax.set(title="Subidas de bus agregadas por tipo de día y corte", xlabel="Corte", ylabel="Subidas promedio agregadas")
ax.grid(alpha=.25)
ax.legend(title="Tipo de día")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "subidas_por_corte_y_dia.png", dpi=160)
plt.show()

# Perfiles horarios para días laborales; comparar si se conserva el patrón punta mañana/tarde.
profile = (
    panel[panel["tipo_dia"] == "LABORAL"]
    .groupby(["periodo", "media_hora"], as_index=False)[TARGET]
    .sum()
)
fig, ax = plt.subplots(figsize=(11, 5))
for period in PERIODS:
    subset = profile[profile["periodo"] == period].sort_values("media_hora")
    ax.plot(subset["media_hora"], subset[TARGET], marker=".", linewidth=1.5, label=period)
ax.set(title="Perfil horario de subidas — días laborales", xlabel="Franja de 30 minutos", ylabel="Subidas promedio agregadas")
ax.tick_params(axis="x", rotation=60)
ax.grid(alpha=.25)
ax.legend(title="Corte")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "perfil_horario_laboral.png", dpi=160)
plt.show()

# Top 10 comunas en el último corte, día laboral.
latest_period = PERIODS[-1]
top_communes = (
    panel[(panel["periodo"] == latest_period) & (panel["tipo_dia"] == "LABORAL")]
    .groupby("comuna", as_index=False)[TARGET]
    .sum()
    .nlargest(10, TARGET)
    .sort_values(TARGET)
)
print(f"\nTop comunas — {latest_period}, LABORAL:")
print(top_communes.to_string(index=False))
fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(top_communes["comuna"], top_communes[TARGET], color="#2878a5")
ax.set(title=f"Top 10 comunas por subidas — {latest_period}, laboral", xlabel="Subidas promedio agregadas")
ax.grid(axis="x", alpha=.2)
fig.tight_layout()
fig.savefig(FIGURES_DIR / "top_comunas_2026_laboral.png", dpi=160)
plt.show()

# %% [markdown]
# ## 3. Baselines y protocolo de validación temporal
#
# Se reservan abril de 2026 como prueba final. Para comparar, se calculan: (a) último corte anterior para la misma comuna/día/franja; (b) media de cortes anteriores. Se añade un HistGradientBoosting como primer modelo de ML con comuna, calendario y demanda observada en cortes previos (lags por corte, no lags de 30 minutos). El ajuste es deliberadamente inicial, no una búsqueda extensa de hiperparámetros.
#
# MAPE se calcula solo sobre observaciones con valor real positivo; también se reporta WAPE para evitar que muchos valores pequeños dominen la interpretación porcentual.

# %%
def score_predictions(y_true, y_pred) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.maximum(np.asarray(y_pred, dtype=float), 0)
    positive = y_true > 0
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "WAPE_pct": float(100 * np.abs(y_true - y_pred).sum() / max(y_true.sum(), 1e-12)),
        "MAPE_positivos_pct": float(100 * np.mean(np.abs((y_true[positive] - y_pred[positive]) / y_true[positive]))) if positive.any() else float("nan"),
    }


def make_features(frame: pd.DataFrame, history_periods: list[str]) -> pd.DataFrame:
    result = frame[["comuna", "tipo_dia", "periodo", "media_hora"]].copy()
    parts = result["periodo"].str.split("-", expand=True).astype(int)
    result["corte_idx"] = result["periodo"].map({period: i for i, period in enumerate(PERIODS)}).astype(float)
    result["mes"] = parts[1].astype(str)
    minutes = result["media_hora"].str.slice(0, 2).astype(int) * 60 + result["media_hora"].str.slice(3, 5).astype(int)
    result["hora_sin"] = np.sin(2 * np.pi * minutes / 1440)
    result["hora_cos"] = np.cos(2 * np.pi * minutes / 1440)

    index = pd.MultiIndex.from_frame(result[KEYS])
    history = pd.concat(
        [panel.loc[panel["periodo"] == period].set_index(KEYS)[TARGET].rename(period)
         for period in history_periods], axis=1
    )
    result["lag_prev_log"] = np.log1p(history[history_periods[-1]].reindex(index).to_numpy())
    result["history_mean_log"] = np.log1p(history.mean(axis=1).reindex(index).to_numpy())
    return result[["comuna", "tipo_dia", "mes", "corte_idx", "hora_sin", "hora_cos", "lag_prev_log", "history_mean_log"]]


def fit_ml(train_periods: list[str], test_period: str) -> np.ndarray | None:
    supervised_periods = train_periods[1:]
    if not supervised_periods:
        return None  # Need a prior cut to construct leakage-free lag features.

    train_frames, train_targets = [], []
    for period in supervised_periods:
        period_index = PERIODS.index(period)
        frame = panel[panel["periodo"] == period].copy()
        prior_periods = PERIODS[:period_index]
        train_frames.append(make_features(frame, prior_periods))
        train_targets.append(frame[TARGET].to_numpy())
    X_train = pd.concat(train_frames, ignore_index=True)
    y_train = np.concatenate(train_targets)

    test = panel[panel["periodo"] == test_period].copy()
    X_test = make_features(test, train_periods)
    categorical = ["comuna", "tipo_dia", "mes"]
    numeric = ["corte_idx", "hora_sin", "hora_cos", "lag_prev_log", "history_mean_log"]
    preprocessor = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical),
         ("numeric", "passthrough", numeric)],
        sparse_threshold=0,
    )
    estimator = HistGradientBoostingRegressor(
        learning_rate=0.05, max_iter=200, max_leaf_nodes=15,
        l2_regularization=2.0, random_state=42, early_stopping=False,
    )
    model = Pipeline([("features", preprocessor), ("regressor", estimator)])
    model.fit(X_train, np.log1p(y_train))
    return np.expm1(model.predict(X_test))


def evaluate_split(train_periods: list[str], test_period: str) -> list[dict[str, object]]:
    train = panel[panel["periodo"].isin(train_periods)].copy()
    test = panel[panel["periodo"] == test_period].copy()
    previous = max(train_periods)
    latest_values = train[train["periodo"] == previous].set_index(KEYS)[TARGET]
    historical_mean = train.groupby(KEYS)[TARGET].mean()
    key_index = pd.MultiIndex.from_frame(test[KEYS])
    predictions = {
        "Último corte": latest_values.reindex(key_index).to_numpy(),
        "Media histórica": historical_mean.reindex(key_index).to_numpy(),
    }
    ml_prediction = fit_ml(train_periods, test_period)
    if ml_prediction is not None:
        predictions["HistGradientBoosting (lags por corte)"] = ml_prediction
    results = []
    for model_name, prediction in predictions.items():
        metrics = score_predictions(test[TARGET], prediction)
        results.append({"corte_prueba": test_period, "entrenamiento": ", ".join(train_periods), "modelo": model_name, **metrics})
    return results


# Validación temporal interna (orientativa) y prueba final bloqueada.
results = []
for train_periods, test_period in [
    ([PERIODS[0]], PERIODS[1]),
    (PERIODS[:2], PERIODS[2]),
    (PERIODS[:3], PERIODS[3]),
]:
    results.extend(evaluate_split(train_periods, test_period))
metrics_table = pd.DataFrame(results)
print(metrics_table.to_string(index=False, formatters={
    "MAE": "{:,.2f}".format,
    "RMSE": "{:,.2f}".format,
    "WAPE_pct": "{:,.2f}".format,
    "MAPE_positivos_pct": "{:,.2f}".format,
}))
metrics_table.to_csv(PROCESSED_DIR / "metricas_modelo_inicial.csv", index=False)

# %% [markdown]
# ## 4. Lectura preliminar y limitaciones
#
# - La comparación principal es entre modelos evaluados en el mismo corte futuro y sobre el mismo target.
# - Abril de 2026 queda como evaluación fuera de tiempo. Solo hay tres cortes históricos para entrenamiento y dos validaciones internas; la evidencia de generalización sigue siendo limitada.
# - El panel usa 36 comunas presentes en los cuatro cortes; la cobertura aumentó en abril de 2026. Se excluye `SIN_COMUNA` del modelo.
# - Los ceros sintéticos están marcados. Si la ausencia de filas no significa cero subidas, hay que revisar el tratamiento antes de aceptar las métricas.
# - La ficha de abril de 2026 agrega “u otro medio de pago”, mientras cortes anteriores refieren a bip!. Un cambio de medición puede afectar el test final.
# - Estas métricas no deben presentarse como predicción de pasajeros reales corregida por evasión.
# - La Tabla de Etapas y su factor de expansión sirven como análisis complementario de abril de 2026, no como etiqueta histórica del modelo.
