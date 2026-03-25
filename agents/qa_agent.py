# agents/qa_agent.py

from prompts.qa_prompt_architect import IA1_QA_ARCHITECT_PROMPT
from prompts.qa_prompt_auditor import IA2_QA_AUDITOR_PROMPT
from prompts.qa_prompt_editor import IA3_QA_EDITOR_PROMPT
from services.groq_client import get_groq_client
# import streamlit as st

# Modelos por IA
MODEL_ARCHITECT = "openai/gpt-oss-120b"  # Criativo/robusto
MODEL_AUDITOR = "llama-3.3-70b-versatile"    # Lógico/determinístico
MODEL_EDITOR = "meta-llama/llama-4-scout-17b-16e-instruct"      # Rápido para formatação

# ===============================
# IA1 - QA Architect
# ===============================
def run_ia1_qa_architect(funcao, detalhes, linguagem=None, framework=None):
    client = get_groq_client()

    # AJUSTE PARA FUNCIONAR: Injetando as variáveis na string do prompt
    # O .format() substitui as chaves {linguagem}, {framework} e {detalhes} no seu IA1_QA_ARCHITECT_PROMPT
    prompt_final = IA1_QA_ARCHITECT_PROMPT.format(
        linguagem=linguagem,
        framework=framework,
        detalhes=detalhes
    )
    
    prompt_final += f"\n\n--- EXECUÇÃO ATUAL ---\n"
    prompt_final += f"[FUNCIONALIDADE SELECIONADA]: {funcao}\n"
    prompt_final += f"[CONTEXTO DO USUÁRIO]: {detalhes}\n"
    if linguagem: prompt_final += f"[LINGUAGEM OBRIGATÓRIA]: {linguagem}\n"
    if framework: prompt_final += f"[FRAMEWORK OBRIGATÓRIO]: {framework}\n"
    
    # Se for Automação, força o BDD no final do prompt do sistema
    if "Automação" in funcao:
        prompt_final += "\n[REGRA]: Gere primeiro o BDD (Gherkin) e depois o script técnico.\n"

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt_final}],
        model=MODEL_ARCHITECT,
        temperature=0.7,
        max_tokens=1800
    )

    return {
        "ID_FUNCAO": funcao,
        "LINGUAGEM": linguagem,
        "FRAMEWORK": framework,
        "CONTEUDO_BRUTO": response.choices[0].message.content,
        "NORMA_APLICADA": "ISTQB / ISO/IEC 29119"
    }

# ===============================
# IA2 - QA Auditor
# ===============================
def run_ia2_qa_auditor(architect_output):
    client = get_groq_client()

    prompt_final = f"{IA2_QA_AUDITOR_PROMPT}\n\n"
    prompt_final += f"--- VALIDAÇÃO DE STACK ---\n"
    prompt_final += f"A entrega DEVE ser em: {architect_output.get('LINGUAGEM')} com {architect_output.get('FRAMEWORK')}.\n"
    prompt_final += f"Se houver BDD ausente em Automação, aponte erro.\n"
    prompt_final += f"--- CONTEÚDO PARA AUDITORIA ---\n"
    prompt_final += f"Função: {architect_output['ID_FUNCAO']}\n"
    prompt_final += f"Conteúdo: {architect_output['CONTEUDO_BRUTO']}\n"

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt_final}],
        model=MODEL_AUDITOR,
        temperature=0.1,
        max_tokens=1000
    )

    return response.choices[0].message.content

# ===============================
# IA3 - QA Editor
# ===============================
def run_ia3_qa_editor(architect_output, auditor_output):
    client = get_groq_client()

    # O Editor também precisa dos dados da stack para formatar corretamente
    prompt_final = IA3_QA_EDITOR_PROMPT.format(
        linguagem=architect_output.get('LINGUAGEM'),
        framework=architect_output.get('FRAMEWORK')
    )
    
    prompt_final += f"\n\n--- INPUTS DE TRABALHO ---\n"
    prompt_final += f"RASCUNHO DO ARQUITETO: {architect_output['CONTEUDO_BRUTO']}\n"
    prompt_final += f"CRÍTICAS DO AUDITOR: {auditor_output}\n"

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt_final}],
        model=MODEL_EDITOR,
        temperature=0.5,
        max_tokens=1200
    )

    return response.choices[0].message.content

# ==========================================
# ORQUESTRADOR PARA STREAMLIT
# ==========================================
def process_full_qa_flow(funcao, detalhes, linguagem=None, framework=None, status_callback=None):
    try:
        # Passo 1: Architect
        if status_callback: 
            status_callback(f"Gerando rascunho em {linguagem}...")
        rascunho = run_ia1_qa_architect(funcao, detalhes, linguagem, framework)

        # Passo 2: Auditor
        if status_callback: 
            status_callback("Auditando conteúdo técnico...")
        criticas = run_ia2_qa_auditor(rascunho)

        # Passo 3: Editor
        if status_callback: 
            status_callback("Formatando e polindo resposta...")
        resultado_final = run_ia3_qa_editor(rascunho, criticas)

        return resultado_final

    except Exception as e:
        return f"❌ Erro no processamento de QA: {str(e)}"
