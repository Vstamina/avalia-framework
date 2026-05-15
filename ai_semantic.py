# ai_semantic.py
import json
from openai import OpenAI
from typing import Dict, List

SYSTEM_PROMPT = """
Você é um consultor sênior especialista em diagnóstico organizacional e gestão de pós-venda em serviços de saúde.
Sua tarefa é analisar textos extraídos de documentos corporativos e mapear evidências para as 12 dimensões do Framework AVALIA SESI.

Dimensões Camada 1: ancoragem, ecossistema, evidencias, jornada, governanca, acao_estrategica
Dimensões Camada 2: qualificacao, ecossistema_fb, evidencias_fb, jornada_fb, governanca_fb, acao_fb

Para cada dimensão, retorne um objeto com:
- evidencias: síntese objetiva do que foi identificado
- gaps: lacunas, fragilidades ou riscos
- recomendacoes: sugestão de intervenção técnica
- nota_sugerida: valor entre 0.0 e 3.0 (0=Sem evidência, 3=Prática estruturada)

Regras:
1. Retorne APENAS um JSON válido.
2. Use linguagem formal e impessoal.
3. Se não houver menção, atribua nota 0.0.

Estrutura de saída obrigatória:
{
  "camada_1": {
    "ancoragem": {"evidencias": "...", "gaps": "...", "recomendacoes": "...", "nota_sugerida": 1.5},
    ...
  },
  "camada_2": {
    "qualificacao": {"evidencias": "...", "gaps": "...", "recomendacoes": "...", "nota_sugerida": 1.0},
    ...
  }
}
"""

def analyze_with_gpt4(api_key: str, extracted_text: str, dims_c1: List[str], dims_c2: List[str]) -> Dict:
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("Chave de API inválida.")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Texto extraído para análise:\n\n{extracted_text}"}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        raw_json = response.choices[0].message.content
        parsed_data = json.loads(raw_json)
        
        if "camada_1" not in parsed_data or "camada_2" not in parsed_data:
            raise ValueError("Estrutura JSON inválida.")
            
        return parsed_data
        
    except Exception as e:
        raise RuntimeError(f"Erro na análise semântica: {str(e)}")