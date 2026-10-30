# Consultor Inteligente de Carreiras em TI

Sistema especialista em Python para mapear afinidades, calcular compatibilidade com 10 trilhas de TI, identificar lacunas de competências e propor um roadmap para nível Júnior.

## Requisitos atendidos
- Escala gradual Likert de 1 a 5.
- Ranking de todas as 10 trilhas e exibição de Top 3 em percentual.
- Fatores de certeza e penalidades para perfis conflitantes.
- Base de conhecimento externa em JSON.
- Análise de gaps por competência.
- Roadmap com assuntos, certificações/cursos e projetos de portfólio.
- Interface Streamlit em etapas.
- Testes automatizados e personas para perfis ambíguos.

## Tecnologias
- Python 3.10+
- Streamlit
- Pandas
- Matplotlib
- JSON
- Motor de inferência próprio (soma ponderada + fatores de certeza)

Não usa Experta: o enunciado permite explicitamente um motor próprio. Essa opção também evita incompatibilidades de predicados da biblioteca Experta.

## Instalação no Windows (PowerShell)

Abra o terminal dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Se o comando `py` não existir, instale Python 3.11 ou 3.12 e marque a opção **Add Python to PATH** durante a instalação. O comando `python -m streamlit` evita depender do atalho `streamlit` no PATH.

Se o PowerShell bloquear a ativação do ambiente virtual, execute nesta janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## Testes

```bash
python -m unittest discover -s tests -v
python personas.py
```

## Estrutura

```text
consultor_carreiras_ti/
├── app.py
├── engine.py
├── regras_carreiras.json
├── personas.py
├── matriz_decisao.md
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_engine.py
```

## Como funciona
1. O usuário informa objetivo e disponibilidade semanal.
2. Responde 12 perguntas de afinidade em escala 1–5.
3. Informa o nível atual nas competências cadastradas.
4. O motor calcula a pontuação de cada trilha, aplica penalidades e ordena o ranking.
5. O sistema identifica gaps para nível Júnior e apresenta roadmap e projetos.
