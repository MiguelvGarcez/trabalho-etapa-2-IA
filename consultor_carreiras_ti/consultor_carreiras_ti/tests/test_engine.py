import unittest
from engine import carregar_base, calcular_compatibilidade, analisar_gaps, recomendar

class TestSistemaEspecialista(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = carregar_base()
        cls.neutro = {q["id"]: 3 for q in cls.base["questions"]}

    def test_dez_trilhas_no_ranking(self):
        ranking = calcular_compatibilidade(self.neutro, self.base)
        self.assertEqual(len(ranking), 10)
        self.assertEqual(len({x["trilha"] for x in ranking}), 10)

    def test_percentuais_validos_e_ordenados(self):
        ranking = calcular_compatibilidade(self.neutro, self.base)
        valores = [x["compatibilidade"] for x in ranking]
        self.assertTrue(all(0 <= x <= 100 for x in valores))
        self.assertEqual(valores, sorted(valores, reverse=True))

    def test_top3(self):
        resultado = recomendar(self.neutro, {}, self.base)
        self.assertEqual(len(resultado["top3"]), 3)

    def test_perfil_devops(self):
        respostas = self.neutro | {"infra":5, "automacao":5, "logica":4, "programacao":4, "visual":1}
        ranking = calcular_compatibilidade(respostas, self.base)
        self.assertIn(ranking[0]["trilha"], ["DevOps / SRE", "Cloud Architecture"])

    def test_perfil_dados(self):
        respostas = self.neutro | {"matematica":5, "dados":5, "logica":4, "programacao":4}
        ranking = calcular_compatibilidade(respostas, self.base)
        self.assertIn(ranking[0]["trilha"], ["Cientista de Dados", "Engenharia de Dados"])

    def test_perfil_web_visual(self):
        respostas = self.neutro | {"visual":5, "programacao":4, "comunicacao":4, "infra":1}
        ranking = calcular_compatibilidade(respostas, self.base)
        self.assertEqual(ranking[0]["trilha"], "Frontend / UX")

    def test_gaps_priorizam_lacunas(self):
        gaps = analisar_gaps("Backend", {}, self.base)
        self.assertTrue(any(g["gap"] > 0 for g in gaps))
        self.assertGreaterEqual(gaps[0]["gap"], gaps[-1]["gap"])

    def test_resposta_invalida(self):
        respostas = self.neutro | {"logica": 8}
        with self.assertRaises(ValueError):
            calcular_compatibilidade(respostas, self.base)

    def test_resposta_ausente(self):
        respostas = dict(self.neutro)
        respostas.pop("logica")
        with self.assertRaises(ValueError):
            calcular_compatibilidade(respostas, self.base)

if __name__ == "__main__":
    unittest.main(verbosity=2)
