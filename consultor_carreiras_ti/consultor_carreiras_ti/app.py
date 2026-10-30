import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from engine import carregar_base, recomendar, NIVEIS

st.set_page_config(page_title="Consultor de Carreiras em TI", page_icon="🧭", layout="wide")
base = carregar_base()
st.title("🧭 Consultor Inteligente de Carreiras em TI")
st.caption("Sistema especialista com pontuação ponderada, fatores de certeza e análise de competências.")
st.info("Responda considerando seu interesse atual. Não existe resposta certa: o resultado é uma orientação inicial, não um teste psicométrico.")

if "etapa" not in st.session_state:
    st.session_state.etapa = 1
if "perfil" not in st.session_state:
    st.session_state.perfil = {"nome": "", "objetivo": "Conseguir meu primeiro emprego em TI", "horas": 6}
if "afinidades" not in st.session_state:
    st.session_state.afinidades = {q["id"]: 3 for q in base["questions"]}
if "conhecimentos" not in st.session_state:
    st.session_state.conhecimentos = {}

def avancar():
    st.session_state.etapa = min(4, st.session_state.etapa + 1)
def voltar():
    st.session_state.etapa = max(1, st.session_state.etapa - 1)

st.progress(st.session_state.etapa / 4, text=f"Etapa {st.session_state.etapa} de 4")

if st.session_state.etapa == 1:
    st.header("Passo 1 — Perfil pessoal")
    with st.form("perfil"):
        nome = st.text_input("Como podemos chamar você? (opcional)", value=st.session_state.perfil["nome"])
        objetivo = st.selectbox("Qual é seu principal objetivo?", [
            "Conseguir meu primeiro emprego em TI", "Mudar de área dentro de TI",
            "Conseguir estágio", "Evoluir na carreira atual", "Explorar possibilidades"
        ], index=["Conseguir meu primeiro emprego em TI","Mudar de área dentro de TI","Conseguir estágio","Evoluir na carreira atual","Explorar possibilidades"].index(st.session_state.perfil["objetivo"]))
        horas = st.slider("Quantas horas por semana você pode dedicar aos estudos?", 1, 40, int(st.session_state.perfil["horas"]))
        if st.form_submit_button("Continuar", type="primary"):
            st.session_state.perfil = {"nome": nome, "objetivo": objetivo, "horas": horas}
            avancar()
            st.rerun()

elif st.session_state.etapa == 2:
    st.header("Passo 2 — Afinidades e interesses")
    st.write("Use a escala de 1 (muito baixa) a 5 (muito alta). As respostas graduais alimentam os pesos do motor de inferência.")
    with st.form("afinidades"):
        for q in base["questions"]:
            st.session_state.afinidades[q["id"]] = st.slider(
                q["label"], 1, 5, int(st.session_state.afinidades[q["id"]]),
                key=f"q_{q['id']}"
            )
        if st.form_submit_button("Salvar afinidades", type="primary"):
            avancar()
            st.rerun()

elif st.session_state.etapa == 3:
    st.header("Passo 3 — Conhecimentos atuais")
    st.write("Informe seu nível em cada competência. O sistema comparará suas respostas com os requisitos mínimos definidos para nível Júnior na trilha recomendada.")
    trilhas = base["tracks"]
    habilidades = sorted({h for dados in trilhas.values() for h in dados["skills"]})
    opcoes = list(NIVEIS.keys())
    with st.form("conhecimentos"):
        cols = st.columns(2)
        for i, habilidade in enumerate(habilidades):
            with cols[i % 2]:
                atual = st.session_state.conhecimentos.get(habilidade, "Não conheço")
                st.session_state.conhecimentos[habilidade] = st.selectbox(
                    habilidade, opcoes, index=opcoes.index(atual), key=f"skill_{i}"
                )
        if st.form_submit_button("Ver resultado", type="primary"):
            avancar()
            st.rerun()

else:
    st.header("Passo 4 — Resultado e plano de desenvolvimento")
    resultado = recomendar(st.session_state.afinidades, st.session_state.conhecimentos, base)
    nome = st.session_state.perfil["nome"].strip()
    if nome:
        st.write(f"Olá, **{nome}**! Considerando seu objetivo — *{st.session_state.perfil['objetivo']}* — este é seu diagnóstico.")
    st.subheader("Ranking de compatibilidade — Top 3")
    df = pd.DataFrame([{"Posição": i+1, "Trilha": x["trilha"], "Compatibilidade": x["compatibilidade"], "Fator de certeza": x["fator_certeza"]} for i, x in enumerate(resultado["top3"])])
    st.dataframe(df, hide_index=True, use_container_width=True)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.barh([x["trilha"] for x in reversed(resultado["top3"])], [x["compatibilidade"] for x in reversed(resultado["top3"])])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Compatibilidade (%)")
    ax.set_title("Suas três trilhas mais compatíveis")
    st.pyplot(fig)
    escolhida = resultado["trilha_recomendada"]
    detalhe = resultado["ranking"][0]
    st.success(f"Trilha mais compatível: {escolhida} — {detalhe['compatibilidade']}%")
    st.write(base["tracks"][escolhida]["description"])
    with st.expander("Por que essa trilha foi recomendada?"):
        st.write("**Evidências favoráveis**")
        for item in detalhe["evidencias"] or ["As respostas apresentam aderência distribuída, sem uma afinidade isolada dominante."]:
            st.write(f"- {item}")
        if detalhe["conflitos"]:
            st.write("**Penalidades aplicadas**")
            for item in detalhe["conflitos"]:
                st.write(f"- {item}")
        st.caption(f"Pontuação antes dos ajustes: {detalhe['pontuacao_base']}%. Penalidade total: {detalhe['penalidade']} pontos. Fator de certeza: {detalhe['fator_certeza']}.")
    st.subheader("Análise de lacunas — caminho até Júnior")
    gaps_df = pd.DataFrame([{"Competência":g["habilidade"],"Seu nível":g["nivel_atual"],"Referência Júnior":g["nivel_junior"],"Lacuna":g["gap"],"Situação":g["status"]} for g in resultado["gaps"]])
    st.dataframe(gaps_df, hide_index=True, use_container_width=True)
    st.subheader("Roadmap personalizado")
    st.write(f"**Tempo disponível informado:** {st.session_state.perfil['horas']} horas por semana.")
    st.write("**Prioridades identificadas:** " + (", ".join(resultado["roadmap"]["prioridades"]) if resultado["roadmap"]["prioridades"] else "Você já atende aos requisitos mínimos cadastrados; aprofunde e produza evidências práticas."))
    for etapa in resultado["roadmap"]["etapas"]:
        with st.expander(etapa["fase"], expanded=True):
            st.markdown("**Estudar primeiro**")
            for assunto in etapa["assuntos"]:
                st.write(f"- {assunto}")
            st.markdown("**Certificações/cursos sugeridos**")
            for cert in etapa["certificacoes"]:
                st.write(f"- {cert}")
            st.markdown("**Projeto para o GitHub**")
            st.write(etapa["projeto"])
    st.caption("Certificações são sugestões, não pré-requisitos obrigatórios. Verifique preço, disponibilidade e conteúdo atual antes de se inscrever.")
    st.subheader("Comparação completa das 10 trilhas")
    all_df = pd.DataFrame([{"Trilha":x["trilha"],"Compatibilidade (%)":x["compatibilidade"]} for x in resultado["ranking"]])
    st.dataframe(all_df, hide_index=True, use_container_width=True)
    csv = all_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Baixar ranking em CSV", csv, "ranking_carreiras.csv", "text/csv")
    if st.button("Refazer diagnóstico"):
        st.session_state.etapa = 1
        st.rerun()

if st.session_state.etapa > 1 and st.session_state.etapa < 4:
    st.button("Voltar", on_click=voltar)
