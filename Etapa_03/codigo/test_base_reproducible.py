"""Casos límite pequeños; la ejecución principal comprueba los datos reales."""
import unittest

import numpy as np
import pandas as pd

from base_reproducible import (
    CLASES, METODOS, cargar_base, cobertura_predicciones, etiquetar,
    metricas_grupo, perfil_para_interpretar, pronosticar,
)


class BaseReproducibleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, _, cls.perfil = cargar_base()

    def test_fronteras_etiquetas_y_ausencias(self):
        casos = [(0, 0), (10, 0), (20, 0), (21, 0), (0, 1)]
        self.assertEqual([etiquetar(v, f, 10, 20) for v, f in casos],
                         CLASES + ["Sin dato completo"])

    def test_historial_incompleto_y_ausente(self):
        perfil = self.perfil.copy()
        franja = perfil.sector.eq("Sur") & perfil.tipo_dia.eq("LABORAL") & perfil.media_hora.eq("07:00")
        perfil.loc[franja & perfil.periodo.eq("2025-11"), "cobertura_completa"] = False
        pred = pronosticar(perfil, "2026-04")
        caso = pred[pred.sector.eq("Sur") & pred.tipo_dia.eq("LABORAL") & pred.media_hora.eq("07:00")]
        self.assertTrue(caso.n_antecedentes.eq(2).all())
        self.assertTrue(caso.ultimo_antecedente.eq("2025-04").all())
        previo = perfil.loc[franja & perfil.periodo.eq("2025-04"), "subidas_sector"].iloc[0]
        self.assertEqual(caso.loc[caso.metodo.eq(METODOS[1]), "prediccion"].iloc[0], previo)
        perfil.loc[franja & perfil.periodo.lt("2026-04"), "cobertura_completa"] = False
        pred = pronosticar(perfil, "2026-04")
        caso = pred[pred.sector.eq("Sur") & pred.tipo_dia.eq("LABORAL") & pred.media_hora.eq("07:00")]
        self.assertTrue(caso.prediccion.isna().all())
        self.assertTrue(caso.etiqueta_predicha.eq("Sin historial").all())

    def test_wape_no_evaluable_si_observado_cero(self):
        grupo = pd.DataFrame(dict(observado=[0.0], prediccion=[1.0],
                                  etiqueta_real=["Nulo"], etiqueta_predicha=["Bajo"]))
        self.assertTrue(np.isnan(metricas_grupo(grupo)["WAPE_pct"]))

    def test_cobertura_no_cuenta_exclusiones_dos_veces(self):
        pred = pd.DataFrame(dict(sector=["Sur"] * 4, periodo=["2026-04"] * 4,
                                 cobertura_completa=[True, False, True, False],
                                 n_antecedentes=[1, 1, 0, 0]))
        fila = cobertura_predicciones(pred, ["periodo", "sector"]).iloc[0]
        self.assertEqual((fila.n_evaluadas, fila.n_incompletas, fila.n_sin_historial), (1, 2, 1))
        self.assertEqual(fila.pct_evaluadas + fila.pct_incompletas + fila.pct_sin_historial, 100)

    def test_perfiles_no_ocultan_faltantes(self):
        perfil = perfil_para_interpretar(self.perfil)
        self.assertTrue(perfil.loc[~perfil.cobertura_completa, "subidas_sector"].isna().all())
        for _, grupo in perfil.groupby(["periodo", "sector", "tipo_dia"]):
            if not grupo.cobertura_completa.all():
                self.assertTrue(grupo.participacion_diaria_pct.isna().all())
            else:
                self.assertAlmostEqual(grupo.participacion_diaria_pct.sum(), 100)


if __name__ == "__main__":
    unittest.main()
