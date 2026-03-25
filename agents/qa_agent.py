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

    # USAMOS F-STRING PARA EVITAR O ERRO DE KEYERROR DO .FORMAT()
    # Isso injeta os dados sem mexer nas outras chaves do seu prompt
    prompt_final = f"""
    {IA1_QA_ARCHITECT_PROMPT}
    
    --- EXECUÇÃO OBRIGATÓRIA ---
    LINGUAGEM: {linguagem}
    FRAMEWORK: {framework}
    FUNCIONALIDADE: {detalhes}
    CATEGORIA: {funcao}
    
    REGRA: Se for Automação, gere o BDD (Gherkin) e o Código em {linguagem}.
    """

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
        "CONTEUDO_BRUTO": response.choices[0].message.content
    }

# ===============================
# IA2 - QA Auditor
# ===============================
def run_ia2_qa_auditor(architect_output):
    client = get_groq_client()

    prompt_final = f"""
    {IA2_QA_AUDITOR_PROMPT}
    
    --- VALIDAÇÃO TÉCNICA ---
    A stack DEVE ser: {architect_output['LINGUAGEM']} + {architect_output['FRAMEWORK']}.
    O conteúdo DEVE conter BDD se for Automação.
    
    CONTEÚDO PARA ANALISAR:
    {architect_output['CONTEUDO_BRUTO']}
    """

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

    # AQUI ESTAVA O ERRO: Usamos concatenação simples para não quebrar as chaves do seu prompt
    prompt_final = f"""
    {IA3_QA_EDITOR_PROMPT}
    
    --- DADOS PARA FORMATAÇÃO FINAL ---
    Linguagem: {architect_output['LINGUAGEM']}
    Framework: {architect_output['FRAMEWORK']}
    Rascunho: {architect_output['CONTEUDO_BRUTO']}
    Críticas: {auditor_output}
    """

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
        # Architect
        if status_callback: status_callback(f"Gerando em {linguagem}...")
        rascunho = run_ia1_qa_architect(funcao, detalhes, linguagem, framework)

        # Auditor
        if status_callback: status_callback("Validando BDD e Stack...")
        criticas = run_ia2_qa_auditor(rascunho)

        # Editor
        if status_callback: status_callback("Limpando resposta...")
        return run_ia3_qa_editor(rascunho, criticas)

    except Exception as e:
        # Agora o erro vai aparecer detalhado aqui se algo falhar
        return f"❌ Erro no processamento de QA: {str(e)}"
