import streamlit as st
from services.groq_client import get_groq_client
from agents.qa_agent import process_full_qa_flow

# Configura a página do Streamlit
st.set_page_config(
    page_title="AI QA Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Conteúdo da barra lateral
with st.sidebar:
    st.title("🧪 AI QA Assistant")
    st.markdown("Especialista em QA para geração de artefatos técnicos e automação.")
    st.markdown("---")
    
    # Seleção direta da ferramenta de QA
    qa_tools = st.selectbox(
        "Selecione a funcionalidade de QA:",
        [
            "Gerar Requisitos Testáveis 📝",
            "Gerar Critérios de Aceitação ✅",
            "Gerar Análise de Risco ⚠️",
            "Gerar Cenários de Teste 📋",
            "Gerar Casos de Teste 🧩",
            "Gerar Testes BDD 🛠️",
            "Gerar Tabelas de Decisão 🔢",
            "Gerar Valores de Teste 🎯",
            "Gerar Dados de Teste 🧪",
            "Gerar Scripts de Setup 🖥️",
            "Gerar Scripts de Teste Automatizados 💻",
            "Gerar Testes Exploratórios 🔍",
            "Gerar Testes de Regressão 🔁",
            "Gerar Templates de Defeito 🐞",
            "Gerar Rastreabilidade 🗂️",
            "Gerar Relatórios de Teste 📊",
            "Gerar Métricas de Qualidade 📈",
            "Fluxo Guiado Completo 🚀"
        ]
    )
        
    # Variáveis de suporte para automação
    linguagem = None
    framework = None
    if qa_tools in ["Gerar Scripts de Teste Automatizados 💻", "Gerar Scripts de Setup 🖥️"]:
        linguagem = st.selectbox("Linguagem/Stack", ["Python 🐍", "JavaScript ✨", "C# 🎵", "Java ☕"])
        framework = st.text_input("Framework (Ex: Selenium, Playwright, Cypress)")

    st.markdown("---")
    st.markdown("IA pode cometer erros. Verifique os artefatos.")
    st.link_button("✉️ Suporte Técnico", "mailto:EMAIL")

# Interface Principal
st.title("Assistente Especialista em QA")
st.caption(f"Foco: {qa_tools}")

# Histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Inicialização do cliente Groq
try:
    client = get_groq_client()
except Exception as e:
    st.sidebar.error(f"Erro ao inicializar o cliente Groq: {e}")
    st.stop()

# Input do usuário
if prompt := st.chat_input("Descreva o requisito ou funcionalidade para testar..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento exclusivo via Agente de QA
    with st.chat_message("assistant"):
        with st.spinner("O Arquiteto, Auditor e Editor estão trabalhando..."):
            try:
                # Chamada do fluxo orquestrado de QA
                ai_resposta = process_full_qa_flow(
                    funcao=qa_tools,
                    detalhes=prompt,
                    linguagem=linguagem,
                    framework=framework
                )
                
                st.markdown(ai_resposta)
                st.session_state.messages.append({"role": "assistant", "content": ai_resposta})

            except Exception as e:
                st.error(f"Ocorreu um erro no processamento: {e}")
