"""Motor de inferência ponderado. A base de conhecimento fica em regras_carreiras.json."""
from __future__ import annotations
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent / "regras_carreiras.json"
NIVEIS = {"Não conheço": 0, "Iniciante": 1, "Básico": 2, "Intermediário": 3, "Avançado": 4}

def carregar_base(caminho=BASE):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

def validar_respostas(respostas, base=None):
    base = base or carregar_base()
    ids = {q["id"] for q in base["questions"]}
    ausentes = ids - set(respostas)
    invalidas = [k for k, v in respostas.items() if k in ids and (not isinstance(v, (int, float)) or not 1 <= v <= 5)]
    if ausentes:
        raise ValueError(f"Respostas ausentes: {', '.join(sorted(ausentes))}")
    if invalidas:
        raise ValueError(f"Respostas devem estar entre 1 e 5: {', '.join(invalidas)}")

def calcular_compatibilidade(respostas, base=None):
    """Calcula aderência relativa (0-100) e fatores de certeza (0-1).

    Pesos positivos representam afinidades; pesos negativos representam conflitos.
    A pontuação bruta positiva é ponderada pela intensidade da resposta (1..5).
    Penalidades são aplicadas após a normalização, sem permitir valores negativos.
    """
    base = base or carregar_base()
    validar_respostas(respostas, base)
    resultados = []
    for trilha, dados in base["tracks"].items():
        positivos = 0.0
        maximo = 0.0
        negativos = 0.0
        evidencias = []
        for pergunta in base["questions"]:
            chave = pergunta["id"]
            peso = float(dados["weights"].get(chave, 0))
            resposta = float(respostas[chave])
            intensidade = (resposta - 1) / 4
            if peso > 0:
                contribuicao = peso * intensidade
                positivos += contribuicao
                maximo += peso
                if resposta >= 4 and peso >= 0.5:
                    evidencias.append(f"Alta afinidade em {pergunta['label'].lower()}")
            elif peso < 0:
                negativos += abs(peso) * intensidade
                maximo += abs(peso) * 0.35
                if resposta >= 4:
                    evidencias.append(f"Possível conflito: {pergunta['label'].lower()}")
        percentual_base = (positivos / maximo * 100) if maximo else 0
        penalidade = 0
        motivos = []
        for regra in base.get("penalties", []):
            cond = regra["when"]
            atende = True
            for chave, limite in cond.items():
                campo = chave.replace("_max", "")
                if respostas.get(campo, 5) > limite:
                    atende = False
                    break
            if atende and trilha in regra["tracks"]:
                penalidade += regra["penalty"]
                motivos.append(regra["reason"])
        percentual = max(0.0, min(100.0, percentual_base - negativos * 2.0 - penalidade))
        fator_certeza = percentual / 100
        resultados.append({
            "trilha": trilha, "compatibilidade": round(percentual, 1),
            "fator_certeza": round(fator_certeza, 3),
            "pontuacao_base": round(percentual_base, 1),
            "penalidade": round(penalidade, 1),
            "evidencias": evidencias[:5], "conflitos": motivos
        })
    return sorted(resultados, key=lambda x: (-x["compatibilidade"], x["trilha"]))

def analisar_gaps(trilha, conhecimentos, base=None):
    """Compara conhecimento declarado aos requisitos mínimos de nível Júnior."""
    base = base or carregar_base()
    if trilha not in base["tracks"]:
        raise ValueError(f"Trilha desconhecida: {trilha}")
    gaps = []
    for habilidade, minimo in base["tracks"][trilha]["skills"].items():
        atual = NIVEIS.get(conhecimentos.get(habilidade, "Não conheço"), 0)
        falta = max(0, minimo - atual)
        gaps.append({
            "habilidade": habilidade, "nivel_atual": atual,
            "nivel_junior": minimo, "gap": falta,
            "status": "Atendido" if falta == 0 else ("Próximo" if falta == 1 else "Gap")
        })
    return sorted(gaps, key=lambda x: (-x["gap"], x["habilidade"]))

def gerar_roadmap(trilha, gaps, base=None):
    base = base or carregar_base()
    dados = base["tracks"][trilha]
    faltantes = [g["habilidade"] for g in gaps if g["gap"] > 0]
    etapas = []
    for etapa in dados["roadmap"]:
        etapas.append({
            "fase": etapa["phase"],
            "assuntos": etapa["topics"],
            "certificacoes": etapa["certifications"],
            "projeto": etapa["project"]
        })
    return {
        "trilha": trilha,
        "descricao": dados["description"],
        "prioridades": faltantes[:6],
        "etapas": etapas,
        "projeto_final": f"Projeto de portfólio: {dados['roadmap'][-1]['project']}"
    }

def recomendar(respostas, conhecimentos=None, base=None):
    base = base or carregar_base()
    ranking = calcular_compatibilidade(respostas, base)
    top3 = ranking[:3]
    escolhida = top3[0]["trilha"]
    gaps = analisar_gaps(escolhida, conhecimentos or {}, base)
    roadmap = gerar_roadmap(escolhida, gaps, base)
    return {"ranking": ranking, "top3": top3, "trilha_recomendada": escolhida,
            "gaps": gaps, "roadmap": roadmap}
