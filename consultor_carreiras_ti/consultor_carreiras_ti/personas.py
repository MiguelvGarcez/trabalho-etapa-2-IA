"""Perfis sintéticos para testar cenários representativos e ambíguos."""
from engine import carregar_base, recomendar

base = carregar_base()
base_respostas = {q["id"]: 3 for q in base["questions"]}
personas = {
    "Infraestrutura e automação": base_respostas | {"infra":5,"automacao":5,"logica":4,"programacao":4,"visual":1},
    "Dados e estatística": base_respostas | {"matematica":5,"dados":5,"logica":4,"programacao":4},
    "Web e design": base_respostas | {"visual":5,"programacao":4,"comunicacao":4,"infra":1},
    "Qualidade e detalhes": base_respostas | {"qualidade":5,"logica":4,"organizacao":4,"programacao":3},
    "Gestão e comunicação": base_respostas | {"comunicacao":5,"organizacao":5,"colaboracao":5,"programacao":1},
    "Perfil ambíguo dados + web": base_respostas | {"dados":5,"matematica":4,"visual":5,"programacao":4,"comunicacao":4}
}
for nome, respostas in personas.items():
    resultado = recomendar(respostas, {}, base)
    print(f"{nome:30} -> Top 3: " + " | ".join(f"{x['trilha']} ({x['compatibilidade']}%)" for x in resultado["top3"]))
