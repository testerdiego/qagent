import streamlit as st
from services.groq_client import get_groq_client
from agents.qa_agent import process_full_qa_flow

# 1. Configuração da Página
st.set_page_config(
    page_title="AI Artifact Creator",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Barra Lateral (Configurações de Contexto)
with st.sidebar:
    st.title("🛠️ AI Artifact Creator")
    st.markdown("Assistente inteligente para criação de artefatos de qualidade.")
    st.markdown("---")
    
    # Menu Consolidado (5 Categorias Principais)
    qa_tools = st.selectbox(
        "O que vamos construir hoje?",
        [
            "Planejamento: Requisitos e Riscos 📝",
            "Design: Cenários e Casos de Teste 🧩",
            "Automação: BDD e Scripts 💻",
            "Execução: Dados e Setup de Ambiente 🧪",
            "Relatórios: Bugs e Métricas de Qualidade 📊"
        ]
    )
    
    st.markdown("### 🛠️ Stack Técnica")
    # Agora a stack é solicitada de forma global para dar contexto à IA
    linguagem = st.selectbox(
        "Linguagem Principal:", 
        ["Python 🐍", "JavaScript ✨", "C# 🎵", "Java ☕", "TypeScript 🟦", "Outra/Não aplicável"]
    )
    
    framework = st.text_input(
        "Framework / Biblioteca:", 
        placeholder="Ex: Playwright, Cypress, Selenium, JUnit..."
    )

    st.markdown("---")
    st.caption("⚠️ A IA precisa de detalhes técnicos para não ser vaga. Seja específico no chat.")
    
    # Link de suporte
    st.link_button("✉️ Suporte Técnico", "mailto:suporte@exemplo.com")

# 3. Interface Principal (Chat)
st.title("Assistente Especialista em QA")
st.info(f"**Modo Ativo:** {qa_tools} | **Stack:** {linguagem} + {framework if framework else 'Nenhum'}")

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Lógica de Execução
try:
    client = get_groq_client()
except Exception as e:
    st.sidebar.error(f"Erro ao conectar com a API: {e}")
    st.stop()

# Captura o Input do Usuário
if prompt := st.chat_input("Descreva a funcionalidade ou o que você deseja criar..."):
    
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento com o Agente de QA
    with st.chat_message("assistant"):
        # Mensagem de status para o usuário
        status_placeholder = st.empty()
        status_placeholder.info("🤖 Analisando contexto e consultando especialistas...")
        
        try:
            # Chama o orquestrador (Architect -> Auditor -> Editor)
            # Passamos linguagem e framework explicitamente para o agente
            ai_resposta = process_full_qa_flow(
                funcao=qa_tools,
                detalhes=prompt,
                linguagem=linguagem,
                framework=framework
            )
            
            status_placeholder.empty()
            st.markdown(ai_resposta)
            
            # Adiciona resposta da IA ao histórico
            st.session_state.messages.append({"role": "assistant", "content": ai_resposta})

        except Exception as e:
            status_placeholder.empty()
            st.error(f"Ocorreu um erro técnico: {e}")

# Rodapé decorativo
st.markdown("---")
st.caption("Focado em ISTQB, ISO/IEC 29119 e boas práticas de engenharia de software.")
