# rule_engine.py
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Rule:
    dimension: str
    layer: int  # 1 or 2
    keywords: List[str]
    negative_keywords: List[str]
    weight: int  # 1, 2 or 3
    min_matches: int
    score_if_met: float
    recommendation_key: str

@dataclass
class DimensionResult:
    dimension: str
    layer: int
    score: float
    evidence_found: List[str]
    gaps_identified: List[str]
    recommendation: str

class RuleEngine:
    """Motor de análise baseado em regras para o Framework AVALIA"""
    
    def __init__(self):
        self.rules = self._load_rules()
        self.recommendations = self._load_recommendations()
        
    def _load_rules(self) -> List[Rule]:
        """Carrega regras pré-definidas para cada dimensão"""
        return [
            # Camada 1 - Ancoragem
            Rule(
                dimension="ancoragem", layer=1,
                keywords=["pós-venda", "acompanhamento", "contrato", "renovação", "relacionamento"],
                negative_keywords=["apenas venda", "só entrega", "sem acompanhamento"],
                weight=3, min_matches=2, score_if_met=2.5,
                recommendation_key="ancoragem_estruturar"
            ),
            Rule(
                dimension="ancoragem", layer=1,
                keywords=["responsável", "dono", "gestor", "carteira"],
                negative_keywords=["ninguém acompanha", "cada um faz", "sem responsável"],
                weight=3, min_matches=1, score_if_met=2.0,
                recommendation_key="ancoragem_responsavel"
            ),
            Rule(
                dimension="ancoragem", layer=1,
                keywords=["indicador", "métrica", "sinal", "risco", "saúde do contrato"],
                negative_keywords=["sem indicador", "não mede", "não sabe"],
                weight=2, min_matches=2, score_if_met=1.5,
                recommendation_key="ancoragem_indicadores"
            ),
            
            # Camada 1 - Ecossistema
            Rule(
                dimension="ecossistema", layer=1,
                keywords=["rh", "sesmt", "trabalhador", "decisor", "stakeholder"],
                negative_keywords=["só a empresa", "um único contato"],
                weight=2, min_matches=3, score_if_met=2.0,
                recommendation_key="ecossistema_mapear"
            ),
            Rule(
                dimension="ecossistema", layer=1,
                keywords=["matriz", "mapa", "atores", "papéis", "responsabilidades"],
                negative_keywords=["não mapeia", "não diferencia"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="ecossistema_matriz"
            ),
            
            # Camada 1 - Evidências
            Rule(
                dimension="evidencias", layer=1,
                keywords=["nps", "csat", "satisfação", "pesquisa", "indicador"],
                negative_keywords=["sem pesquisa", "não mede satisfação"],
                weight=3, min_matches=1, score_if_met=2.0,
                recommendation_key="evidencias_pesquisa"
            ),
            Rule(
                dimension="evidencias", layer=1,
                keywords=["relatório", "dashboard", "painel", "bi", "dados"],
                negative_keywords=["sem relatório", "dados dispersos", "planilha solta"],
                weight=3, min_matches=2, score_if_met=2.5,
                recommendation_key="evidencias_painel"
            ),
            Rule(
                dimension="evidencias", layer=1,
                keywords=["histórico", "evolução", "série temporal", "longitudinal"],
                negative_keywords=["só pontual", "sem histórico"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="evidencias_historico"
            ),
            
            # Camada 1 - Jornada
            Rule(
                dimension="jornada", layer=1,
                keywords=["etapa", "fase", "onboarding", "ativação", "handoff"],
                negative_keywords=["sem etapa definida", "só executa"],
                weight=2, min_matches=2, score_if_met=2.0,
                recommendation_key="jornada_mapear"
            ),
            Rule(
                dimension="jornada", layer=1,
                keywords=["marco", "ponto de contato", "ritual", "reunião"],
                negative_keywords=["sem contato", "só quando problema"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="jornada_rituais"
            ),
            
            # Camada 1 - Governança
            Rule(
                dimension="governanca", layer=1,
                keywords=["raci", "matriz", "responsabilidade", "papel", "fluxo"],
                negative_keywords=["sem definição", "cada um faz", "improviso"],
                weight=3, min_matches=2, score_if_met=2.0,
                recommendation_key="governanca_matriz"
            ),
            Rule(
                dimension="governanca", layer=1,
                keywords=["escalona", "critério", "prioridade", "decisão"],
                negative_keywords=["sem critério", "depende da pessoa"],
                weight=3, min_matches=1, score_if_met=1.5,
                recommendation_key="governanca_criterios"
            ),
            Rule(
                dimension="governanca", layer=1,
                keywords=["reunião", "ritual", "comitê", "cadência"],
                negative_keywords=["sem reunião", "só quando precisa"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="governanca_rituais"
            ),
            
            # Camada 1 - Ação Estratégica
            Rule(
                dimension="acao_estrategica", layer=1,
                keywords=["plano de ação", "responsável", "prazo", "follow-up"],
                negative_keywords=["sem plano", "não acompanha", "só registra"],
                weight=3, min_matches=2, score_if_met=2.0,
                recommendation_key="acao_plano"
            ),
            Rule(
                dimension="acao_estrategica", layer=1,
                keywords=["renovação", "expansão", "upsell", "cross-sell"],
                negative_keywords=["só mantém", "sem crescimento"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="acao_retencao"
            ),
            
            # Camada 2 - Qualificação do Feedback
            Rule(
                dimension="qualificacao", layer=2,
                keywords=["reclamação", "dúvida", "sugestão", "elogio", "classificação"],
                negative_keywords=["tudo é reclamação", "sem categoria"],
                weight=3, min_matches=2, score_if_met=2.0,
                recommendation_key="qualificacao_taxonomia"
            ),
            Rule(
                dimension="qualificacao", layer=2,
                keywords=["causa", "raiz", "5 porquês", "análise"],
                negative_keywords=["só sintoma", "não investiga"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="qualificacao_causa"
            ),
            
            # Camada 2 - Ecossistema do Feedback
            Rule(
                dimension="ecossistema_fb", layer=2,
                keywords=["origem", "quem falou", "rh", "trabalhador", "decisor"],
                negative_keywords=["não registra origem", "sem identificação"],
                weight=2, min_matches=2, score_if_met=2.0,
                recommendation_key="ecossistema_fb_origem"
            ),
            
            # Camada 2 - Evidências do Feedback
            Rule(
                dimension="evidencias_fb", layer=2,
                keywords=["registro", "base", "sistema", "crm", "chamado"],
                negative_keywords=["planilha solta", "e-mail", "whatsapp", "informal"],
                weight=3, min_matches=2, score_if_met=2.0,
                recommendation_key="evidencias_fb_registro"
            ),
            Rule(
                dimension="evidencias_fb", layer=2,
                keywords=["recorrência", "histórico", "padrão", "tendência"],
                negative_keywords=["caso isolado", "não analisa padrão"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="evidencias_fb_recorrencia"
            ),
            
            # Camada 2 - Jornada do Feedback
            Rule(
                dimension="jornada_fb", layer=2,
                keywords=["etapa", "momento", "fase", "jornada"],
                negative_keywords=["sem vínculo", "não localiza"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="jornada_fb_vinculo"
            ),
            
            # Camada 2 - Governança do Feedback
            Rule(
                dimension="governanca_fb", layer=2,
                keywords=["responsável", "prazo", "sla", "tratativa"],
                negative_keywords=["sem dono", "sem prazo", "fica parado"],
                weight=3, min_matches=2, score_if_met=2.0,
                recommendation_key="governanca_fb_fluxo"
            ),
            Rule(
                dimension="governanca_fb", layer=2,
                keywords=["escalona", "crítico", "urgente", "prioridade"],
                negative_keywords=["tudo igual", "sem priorização"],
                weight=3, min_matches=1, score_if_met=1.5,
                recommendation_key="governanca_fb_criticidade"
            ),
            
            # Camada 2 - Ação Estratégica do Feedback
            Rule(
                dimension="acao_fb", layer=2,
                keywords=["retorno", "devolutiva", "fechamento", "loop"],
                negative_keywords=["não responde", "sem retorno", "fica aberto"],
                weight=3, min_matches=1, score_if_met=2.0,
                recommendation_key="acao_fb_loop"
            ),
            Rule(
                dimension="acao_fb", layer=2,
                keywords=["melhoria", "aprendizado", "mudança", "processo"],
                negative_keywords=["só resolve", "não melhora", "repete"],
                weight=2, min_matches=1, score_if_met=1.5,
                recommendation_key="acao_fb_aprendizado"
            ),
        ]
    
    def _load_recommendations(self) -> Dict[str, str]:
        """Biblioteca de recomendações pré-definidas por chave"""
        return {
            # Ancoragem
            "ancoragem_estruturar": "Definir institucionalmente o conceito de pós-venda em serviços de saúde, estabelecendo início, finalidade, responsáveis e indicadores mínimos.",
            "ancoragem_responsavel": "Designar formalmente um responsável pela visão integral do contrato, com autoridade para coordenar áreas e decisões.",
            "ancoragem_indicadores": "Criar painel mínimo de saúde contratual com indicadores de valor percebido, risco e oportunidade.",
            
            # Ecossistema
            "ecossistema_mapear": "Mapear atores do contrato diferenciando contratante, decisor, influenciador, usuário final e responsável técnico.",
            "ecossistema_matriz": "Desenvolver matriz de stakeholders por contrato com papéis, necessidades e canais de comunicação específicos.",
            
            # Evidências
            "evidencias_pesquisa": "Implementar pesquisa estruturada de satisfação com periodicidade definida e análise gerencial.",
            "evidencias_painel": "Integrar dados operacionais, de satisfação e contratuais em painel único de acompanhamento.",
            "evidencias_historico": "Estabelecer série histórica por contrato para permitir análise longitudinal de evolução.",
            
            # Jornada
            "jornada_mapear": "Desenhar jornada gerencial de pós-venda com marcos, responsáveis e indicadores por etapa.",
            "jornada_rituais": "Definir rituais de contato proativo por etapa da jornada para antecipação de riscos.",
            
            # Governança
            "governanca_matriz": "Formalizar matriz de responsabilidades (RACI) para acompanhamento contratual.",
            "governanca_criterios": "Estabelecer critérios objetivos para definição de criticidade e escalonamento.",
            "governanca_rituais": "Criar ritual de governança interáreas com periodicidade definida e pauta estruturada.",
            
            # Ação Estratégica
            "acao_plano": "Implementar rotina de gestão de ações com responsável, prazo, indicador e status rastreável.",
            "acao_retencao": "Vincular acompanhamento de pós-venda a indicadores de renovação e expansão contratual.",
            
            # Qualificação Feedback
            "qualificacao_taxonomia": "Criar taxonomia de feedback com categorias: reclamação, dúvida, sugestão, elogio, risco, oportunidade.",
            "qualificacao_causa": "Estabelecer método de análise de causa raiz para feedbacks críticos.",
            
            # Ecossistema Feedback
            "ecossistema_fb_origem": "Incluir campo obrigatório de origem do feedback com diferenciação de atores.",
            
            # Evidências Feedback
            "evidencias_fb_registro": "Centralizar registro de feedbacks em base estruturada com campos mínimos obrigatórios.",
            "evidencias_fb_recorrencia": "Implementar análise de recorrência para identificar padrões e priorizar intervenções.",
            
            # Jornada Feedback
            "jornada_fb_vinculo": "Vincular cada feedback à etapa da jornada em que ocorreu para análise contextual.",
            
            # Governança Feedback
            "governanca_fb_fluxo": "Definir fluxo institucional de tratativa com responsável, prazo e regra de escalonamento.",
            "governanca_fb_criticidade": "Criar matriz de criticidade com critérios objetivos para priorização.",
            
            # Ação Feedback
            "acao_fb_loop": "Garantir fechamento de loop com devolutiva ao cliente e registro de ação adotada.",
            "acao_fb_aprendizado": "Estabelecer rotina de revisão de feedbacks tratados para extração de aprendizado institucional.",
        }
    
    def analyze_text(self, text: str, dimension: str, layer: int) -> Dict:
        """Analisa um texto contra as regras de uma dimensão específica"""
        text_lower = text.lower()
        matching_rules = [r for r in self.rules if r.dimension == dimension and r.layer == layer]
        
        total_score = 0.0
        total_weight = 0
        evidence_found = []
        gaps_identified = []
        recommendations = []
        
        for rule in matching_rules:
            # Conta matches de keywords positivas
            positive_matches = sum(1 for kw in rule.keywords if kw.lower() in text_lower)
            # Conta matches de keywords negativas
            negative_matches = sum(1 for kw in rule.negative_keywords if kw.lower() in text_lower)
            
            # Aplica lógica da regra
            if positive_matches >= rule.min_matches and negative_matches == 0:
                total_score += rule.score_if_met * rule.weight
                total_weight += rule.weight
                evidence_found.append(f"Evidência: {', '.join(rule.keywords[:3])}")
            elif negative_matches > 0:
                gaps_identified.append(f"Lacuna: {', '.join(rule.negative_keywords[:2])}")
                recommendations.append(rule.recommendation_key)
            else:
                gaps_identified.append(f"Ausência de evidência para: {rule.keywords[0]}")
        
        # Calcula score final ponderado
        final_score = total_score / total_weight if total_weight > 0 else 1.0
        # Limita entre 0 e 3
        final_score = max(0.0, min(3.0, final_score))
        
        # Seleciona recomendação principal
        primary_recommendation = self.recommendations.get(
            recommendations[0] if recommendations else f"{dimension}_generico",
            "Revisar processos e evidências para esta dimensão."
        )
        
        return {
            "score": round(final_score, 2),
            "evidence": evidence_found[:3],  # Limita a 3 evidências
            "gaps": gaps_identified[:3],
            "recommendation": primary_recommendation
        }
    
    def analyze_document(self, extracted_text: str) -> Dict[str, DimensionResult]:
        """Analisa texto extraído de documento contra todas as regras"""
        results = {}
        dimensions_c1 = ["ancoragem", "ecossistema", "evidencias", "jornada", "governanca", "acao_estrategica"]
        dimensions_c2 = ["qualificacao", "ecossistema_fb", "evidencias_fb", "jornada_fb", "governanca_fb", "acao_fb"]
        
        for dim in dimensions_c1:
            analysis = self.analyze_text(extracted_text, dim, layer=1)
            results[f"c1_{dim}"] = DimensionResult(
                dimension=dim,
                layer=1,
                score=analysis["score"],
                evidence_found=analysis["evidence"],
                gaps_identified=analysis["gaps"],
                recommendation=analysis["recommendation"]
            )
        
        for dim in dimensions_c2:
            analysis = self.analyze_text(extracted_text, dim, layer=2)
            results[f"c2_{dim}"] = DimensionResult(
                dimension=dim,
                layer=2,
                score=analysis["score"],
                evidence_found=analysis["evidence"],
                gaps_identified=analysis["gaps"],
                recommendation=analysis["recommendation"]
            )
        
        return results