# framework_engine.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ==========================================================
# DIMENSÕES DO FRAMEWORK AVALIA
# ==========================================================

DIMENSIONS_C1 = [
    "ancoragem",
    "ecossistema",
    "evidencias",
    "jornada",
    "governanca",
    "acao_estrategica",
]

DIMENSIONS_C2 = [
    "qualificacao",
    "ecossistema_fb",
    "evidencias_fb",
    "jornada_fb",
    "governanca_fb",
    "acao_fb",
]


DIMENSION_NAMES = {
    "ancoragem": "Ancoragem do Problema",
    "ecossistema": "Visão de Ecossistema",
    "evidencias": "Análise de Evidências",
    "jornada": "Leitura da Jornada",
    "governanca": "Integração e Governança",
    "acao_estrategica": "Ação Estratégica",
    "qualificacao": "Qualificação do Feedback",
    "ecossistema_fb": "Ecossistema do Feedback",
    "evidencias_fb": "Evidências do Feedback",
    "jornada_fb": "Jornada do Feedback",
    "governanca_fb": "Governança do Feedback",
    "acao_fb": "Ação Baseada em Feedback",
}


DIMENSION_LAYER = {
    "ancoragem": 1,
    "ecossistema": 1,
    "evidencias": 1,
    "jornada": 1,
    "governanca": 1,
    "acao_estrategica": 1,
    "qualificacao": 2,
    "ecossistema_fb": 2,
    "evidencias_fb": 2,
    "jornada_fb": 2,
    "governanca_fb": 2,
    "acao_fb": 2,
}

DEFAULT_STRATEGIC_IMPACT = {
    "ancoragem": "Alto",
    "ecossistema": "Médio",
    "evidencias": "Alto",
    "jornada": "Alto",
    "governanca": "Alto",
    "acao_estrategica": "Médio",
    "qualificacao": "Alto",
    "ecossistema_fb": "Médio",
    "evidencias_fb": "Alto",
    "jornada_fb": "Alto",
    "governanca_fb": "Alto",
    "acao_fb": "Médio",
}

# ==========================================================
# MODELOS DE DADOS
# ==========================================================

class DimensionData(BaseModel):
    score: Optional[float] = None
    evidencias: str = ""
    gaps: str = ""
    recomendacoes: str = ""
    impacto_estrategico: str = "Medio"


class LacunaItem(BaseModel):
    lacuna: str
    evidencia: str
    impacto: str


class AssessmentResult(BaseModel):
    dimension_key: str
    camada: int
    dimensao: str
    score_final: float
    nivel_maturidade: str
    impacto_estrategico_aplicado: str
    prioridade_intervencao: str
    texto_diagnostico: str
    recomendacao_estrategica: str
    lacunas: List[LacunaItem] = Field(default_factory=list)


class AssessmentSummary(BaseModel):
    indice_geral: float
    nivel_geral: str
    indice_camada_1: float
    nivel_camada_1: str
    indice_camada_2: float
    nivel_camada_2: str
    principal_forca: str
    principal_lacuna: str
    dimensoes_criticas: List[str]
    dimensoes_maior_maturidade: List[str]
    dimensoes_em_evolucao: List[str]


# ==========================================================
# RÉGUA DE MATURIDADE
# ==========================================================

MATURITY_RULER = [
    {
        "nivel": "Incipiente",
        "min": 0.00,
        "max": 0.99,
        "descricao": (
            "Ausência de evidências suficientes, práticas não formalizadas "
            "ou baixa capacidade de gestão estruturada da dimensão analisada."
        ),
    },
    {
        "nivel": "Inicial",
        "min": 1.00,
        "max": 1.74,
        "descricao": (
            "Existência de práticas pontuais, ainda pouco formalizadas, "
            "dependentes de pessoas ou aplicadas de modo fragmentado."
        ),
    },
    {
        "nivel": "Organizado",
        "min": 1.75,
        "max": 2.49,
        "descricao": (
            "Existência de práticas reconhecíveis, com algum grau de consistência, "
            "ainda que parcialmente integradas ou com oportunidades de aprimoramento."
        ),
    },
    {
        "nivel": "Estruturado",
        "min": 2.50,
        "max": 3.00,
        "descricao": (
            "Práticas formalizadas, integradas, acompanhadas por indicadores "
            "e utilizadas de forma recorrente para decisão, aprendizagem e melhoria contínua."
        ),
    },
]


def normalize_score(score: Optional[float]) -> float:
    if score is None:
        return 0.0

    try:
        numeric_score = float(score)
    except (TypeError, ValueError):
        return 0.0

    return round(max(0.0, min(3.0, numeric_score)), 2)


def get_maturity_label(score: float) -> str:
    score = normalize_score(score)

    if score < 1.00:
        return "Incipiente"
    if score < 1.75:
        return "Inicial"
    if score < 2.50:
        return "Organizado"

    return "Estruturado"


def get_maturity_description(score: float) -> str:
    label = get_maturity_label(score)

    for item in MATURITY_RULER:
        if item["nivel"] == label:
            return item["descricao"]

    return ""


def sugerir_impacto_estrategico(
    score: Optional[float] = None,
    dimension_key: Optional[str] = None,
) -> str:
    if dimension_key in DEFAULT_STRATEGIC_IMPACT:
        return DEFAULT_STRATEGIC_IMPACT[dimension_key]

    score = normalize_score(score)

    if score < 1.75:
        return "Alto"

    if score < 2.50:
        return "Médio"

    return "Baixo"


def get_priority_label(score: float, impacto: str = "Medio") -> str:
    score = normalize_score(score)
    impacto_normalizado = normalize_impact(impacto)

    if score < 1.00:
        return "Alta"

    if score < 1.75:
        if impacto_normalizado == "Alto":
            return "Alta"
        return "Média"

    if score < 2.50:
        if impacto_normalizado == "Alto":
            return "Média"
        return "Monitoramento"

    return "Manutenção"


def normalize_impact(impacto: str) -> str:
    if not impacto:
        return "Medio"

    value = impacto.strip().lower()

    if value in ["alto", "alta"]:
        return "Alto"

    if value in ["baixo", "baixa"]:
        return "Baixo"

    return "Medio"


# ==========================================================
# OBJETIVOS DAS DIMENSÕES
# ==========================================================

DIMENSION_OBJECTIVES = {
    "ancoragem": (
        "Avaliar se existe compreensão clara, compartilhada e operacional "
        "sobre o papel do pós-venda, seu início, seus responsáveis e sua finalidade gerencial."
    ),
    "ecossistema": (
        "Avaliar se a organização reconhece e gerencia os múltiplos atores envolvidos "
        "na relação contratual, distinguindo contratante, decisor, influenciadores, áreas técnicas e usuários finais."
    ),
    "evidencias": (
        "Avaliar se a organização dispõe de dados suficientes, integrados e acionáveis "
        "para acompanhar contratos, orientar decisões, antecipar riscos e demonstrar valor."
    ),
    "jornada": (
        "Avaliar se o contrato é acompanhado como uma jornada contínua de experiência, "
        "valor, comunicação, risco e aprendizagem, e não apenas como uma sequência de entregas operacionais."
    ),
    "governanca": (
        "Avaliar se existem papéis, responsabilidades, fluxos, critérios e rituais de governança "
        "para coordenar o acompanhamento contratual."
    ),
    "acao_estrategica": (
        "Avaliar se o pós-venda gera ações concretas, valor percebido, renovação, expansão, "
        "aprendizagem organizacional e melhoria contínua."
    ),
    "qualificacao": (
        "Avaliar se a organização diferencia feedbacks por natureza, causa, impacto, criticidade "
        "e potencial de ação."
    ),
    "ecossistema_fb": (
        "Avaliar se o feedback é interpretado considerando quem falou, de qual posição falou, "
        "quem deve receber retorno e quais cuidados institucionais devem orientar a devolutiva."
    ),
    "evidencias_fb": (
        "Avaliar se os feedbacks são registrados, classificados, integrados e analisados "
        "como evidência gerencial."
    ),
    "jornada_fb": (
        "Avaliar se o feedback é localizado na etapa da jornada em que surgiu, permitindo "
        "compreender fricções, recorrências e oportunidades de prevenção."
    ),
    "governanca_fb": (
        "Avaliar se o feedback possui fluxo institucional claro, com papéis, prazos, criticidade, "
        "escalonamento e fechamento de loop."
    ),
    "acao_fb": (
        "Avaliar se o feedback tratado gera consequência, aprendizado, melhoria, prevenção "
        "e retroalimentação do pós-venda."
    ),
}


# ==========================================================
# LACUNAS E RECOMENDAÇÕES POR DIMENSÃO E NÍVEL
# ==========================================================

CONTEXT_RULES = {
    "ancoragem": {
        "Incipiente": {
            "diagnostico": (
                "A dimensão apresenta baixa evidência de institucionalização do pós-venda. "
                "O acompanhamento tende a ocorrer de modo reativo, sem definição clara de início, finalidade e responsáveis."
            ),
            "lacunas": [
                {
                    "lacuna": "Ausência de conceito operacional formal de pós-venda",
                    "evidencia": "Não há definição institucional clara sobre quando o pós-venda começa e quais entregas deve contemplar.",
                    "impacto": "Pode gerar leituras distintas entre áreas e reduzir a consistência do acompanhamento contratual.",
                },
                {
                    "lacuna": "Responsabilidade difusa pela gestão do contrato",
                    "evidencia": "A condução do relacionamento depende de iniciativas individuais ou de arranjos informais.",
                    "impacto": "Aumenta o risco de descontinuidade, omissões e baixa coordenação entre áreas.",
                },
                {
                    "lacuna": "Baixa antecipação de riscos contratuais",
                    "evidencia": "O pós-venda é acionado principalmente quando há demanda explícita ou problema instalado.",
                    "impacto": "Reduz a capacidade preventiva e compromete a demonstração contínua de valor.",
                },
            ],
            "recomendacao": (
                "Formalizar o conceito de pós-venda, definindo marco inicial, finalidade, responsáveis, "
                "critérios mínimos de acompanhamento e gatilhos de atuação preventiva."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Há reconhecimento da importância do pós-venda, mas a prática ainda se mostra parcial, "
                "reativa e dependente de pessoas-chave."
            ),
            "lacunas": [
                {
                    "lacuna": "Handoff comercial-operacional pouco estruturado",
                    "evidencia": "A passagem da venda para a operação não apresenta rito padronizado.",
                    "impacto": "Pode gerar perda de contexto, desalinhamento de expectativas e retrabalho.",
                },
                {
                    "lacuna": "Critérios de saúde contratual pouco definidos",
                    "evidencia": "A identificação de risco depende mais de percepção do que de indicadores formais.",
                    "impacto": "Dificulta priorização e intervenção antes do agravamento do problema.",
                },
                {
                    "lacuna": "Visão estratégica ainda limitada",
                    "evidencia": "O acompanhamento concentra-se na execução técnica e não na gestão de valor percebido.",
                    "impacto": "Reduz a contribuição do pós-venda para retenção, renovação e expansão.",
                },
            ],
            "recomendacao": (
                "Estruturar o handoff comercial-operacional e criar indicadores mínimos de saúde contratual, "
                "com rotina de acompanhamento desde o início da vigência."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A dimensão apresenta práticas reconhecíveis de acompanhamento, mas ainda há espaço para "
                "ampliar a integração estratégica e a demonstração recorrente de valor."
            ),
            "lacunas": [
                {
                    "lacuna": "Demonstração de valor ainda pontual",
                    "evidencia": "Os resultados são apresentados em momentos específicos, sem rotina estratégica consolidada.",
                    "impacto": "Pode enfraquecer a percepção de valor ao longo da vigência contratual.",
                },
                {
                    "lacuna": "Baixa sistematização de oportunidades",
                    "evidencia": "Expansões e melhorias nem sempre são registradas e acompanhadas como parte do pós-venda.",
                    "impacto": "Reduz a capacidade de transformar relacionamento em inovação e crescimento contratual.",
                },
                {
                    "lacuna": "Ritual estratégico com decisores ainda insuficiente",
                    "evidencia": "O contato com decisores pode ocorrer sem cadência ou pauta gerencial padronizada.",
                    "impacto": "Dificulta alinhamento estratégico e antecipação de decisões de renovação.",
                },
            ],
            "recomendacao": (
                "Implantar rotina periódica de revisão estratégica com clientes, com pauta de valor, riscos, "
                "oportunidades, indicadores e plano de evolução contratual."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A dimensão apresenta maturidade elevada, com práticas formalizadas e capacidade de decisão. "
                "A agenda principal passa a ser refinamento, escala e inteligência preditiva."
            ),
            "lacunas": [
                {
                    "lacuna": "Oportunidade de automação preditiva",
                    "evidencia": "Há base de acompanhamento, mas nem todos os alertas são automatizados.",
                    "impacto": "Pode limitar a velocidade de resposta em carteiras maiores.",
                },
                {
                    "lacuna": "Personalização em escala",
                    "evidencia": "O acompanhamento estruturado pode exigir segmentação mais fina por perfil de contrato.",
                    "impacto": "Risco de aplicar o mesmo padrão de relacionamento a contratos com necessidades distintas.",
                },
                {
                    "lacuna": "Integração com inovação de serviços",
                    "evidencia": "Os aprendizados do pós-venda podem ser melhor conectados ao desenvolvimento de novas soluções.",
                    "impacto": "Reduz o potencial de inovação orientada pela experiência do cliente.",
                },
            ],
            "recomendacao": (
                "Evoluir para gestão preditiva do pós-venda, com segmentação por perfil de contrato, "
                "alertas automatizados e integração dos aprendizados à inovação de serviços."
            ),
        },
    },

    "ecossistema": {
        "Incipiente": {
            "diagnostico": (
                "A relação contratual é lida de forma restrita, com baixa diferenciação entre os atores "
                "que participam, influenciam ou experimentam os serviços."
            ),
            "lacunas": [
                {
                    "lacuna": "Ausência de mapa formal de stakeholders",
                    "evidencia": "Os atores do contrato não estão organizados em uma matriz institucional.",
                    "impacto": "Dificulta reconhecer decisores, influenciadores, usuários finais e áreas técnicas relevantes.",
                },
                {
                    "lacuna": "Comunicação pouco segmentada",
                    "evidencia": "As mensagens tendem a ser padronizadas para públicos com papéis distintos.",
                    "impacto": "Pode reduzir aderência, clareza e efetividade da comunicação.",
                },
                {
                    "lacuna": "Baixa visibilidade da experiência do trabalhador",
                    "evidencia": "A gestão pode se concentrar no contratante formal, sem captar adequadamente a experiência do usuário final.",
                    "impacto": "Problemas de adesão e percepção podem permanecer invisíveis até afetarem o contrato.",
                },
            ],
            "recomendacao": (
                "Construir matriz de stakeholders por contrato, distinguindo decisores, influenciadores, "
                "áreas técnicas, RH, SESMT, lideranças e usuários finais."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "A organização reconhece múltiplos atores, mas ainda não os gerencia de forma sistemática "
                "ao longo da jornada contratual."
            ),
            "lacunas": [
                {
                    "lacuna": "Mapeamento informal de atores",
                    "evidencia": "A identificação de stakeholders depende do conhecimento das equipes.",
                    "impacto": "Pode gerar perda de informação em mudanças de equipe ou de interlocutores.",
                },
                {
                    "lacuna": "Baixa diferenciação entre decisor e usuário final",
                    "evidencia": "As percepções de quem contrata e de quem utiliza o serviço podem ser tratadas como equivalentes.",
                    "impacto": "Distorce a leitura de satisfação e de valor percebido.",
                },
                {
                    "lacuna": "Pouca gestão dos influenciadores internos",
                    "evidencia": "Áreas que afetam adesão e percepção nem sempre são acompanhadas como atores estratégicos.",
                    "impacto": "Reduz capacidade de mobilização e sustentação do contrato.",
                },
            ],
            "recomendacao": (
                "Formalizar o mapa de atores do contrato e criar estratégias de comunicação e devolutiva "
                "por perfil de stakeholder."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "Há reconhecimento dos principais atores e alguma estrutura de relacionamento, mas a gestão "
                "do ecossistema ainda pode avançar em segmentação, cadência e inteligência relacional."
            ),
            "lacunas": [
                {
                    "lacuna": "Segmentação relacional ainda limitada",
                    "evidencia": "Nem todos os atores possuem estratégia específica de acompanhamento.",
                    "impacto": "Pode enfraquecer engajamento, adesão e percepção de valor.",
                },
                {
                    "lacuna": "Rede de influência pouco monitorada",
                    "evidencia": "Influenciadores informais podem não ser acompanhados de modo sistemático.",
                    "impacto": "Dificulta antecipar resistências ou oportunidades dentro da empresa contratante.",
                },
                {
                    "lacuna": "Devolutivas pouco calibradas por público",
                    "evidencia": "A comunicação de resultados pode não variar conforme o papel do interlocutor.",
                    "impacto": "Reduz a eficácia da demonstração de valor.",
                },
            ],
            "recomendacao": (
                "Implantar gestão segmentada do ecossistema contratual, com matriz de atores, canais, "
                "mensagens, periodicidade e critérios de devolutiva por público."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A gestão do ecossistema está consolidada. A principal oportunidade é ampliar inteligência "
                "relacional e integração com indicadores de valor e risco."
            ),
            "lacunas": [
                {
                    "lacuna": "Monitoramento avançado da rede de influência",
                    "evidencia": "A estrutura existe, mas pode evoluir para análise mais preditiva de relações e riscos.",
                    "impacto": "A organização pode perder sinais fracos de insatisfação ou oportunidade.",
                },
                {
                    "lacuna": "Integração parcial com métricas de contrato",
                    "evidencia": "Nem sempre o comportamento dos atores é conectado a renovação, expansão ou risco.",
                    "impacto": "Reduz a capacidade analítica do relacionamento.",
                },
                {
                    "lacuna": "Aprendizagem intercontratual pouco explorada",
                    "evidencia": "Padrões de ecossistema podem não ser comparados entre clientes similares.",
                    "impacto": "Limita benchmarking e melhoria do modelo de atendimento.",
                },
            ],
            "recomendacao": (
                "Evoluir a gestão de stakeholders para inteligência relacional, conectando atores, riscos, "
                "adesão, satisfação e oportunidades de expansão."
            ),
        },
    },

    "evidencias": {
        "Incipiente": {
            "diagnostico": (
                "A dimensão revela baixa capacidade de transformar dados em evidências gerenciais. "
                "As informações existem de forma dispersa ou insuficiente."
            ),
            "lacunas": [
                {
                    "lacuna": "Dados dispersos entre áreas ou sistemas",
                    "evidencia": "Informações relevantes não estão integradas em uma visão única do contrato.",
                    "impacto": "Dificulta tomada de decisão e acompanhamento longitudinal.",
                },
                {
                    "lacuna": "Ausência de indicadores mínimos",
                    "evidencia": "Não há painel consolidado com métricas de uso, satisfação, risco e valor.",
                    "impacto": "Reduz a capacidade de demonstrar resultados e antecipar problemas.",
                },
                {
                    "lacuna": "Baixa rastreabilidade histórica",
                    "evidencia": "A análise tende a ser pontual, sem comparação temporal.",
                    "impacto": "Impede identificar evolução, recorrência ou deterioração contratual.",
                },
            ],
            "recomendacao": (
                "Criar painel mínimo de acompanhamento contratual, integrando indicadores operacionais, "
                "satisfação, utilização, risco e evidências de valor."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Existem fontes de dados relevantes, mas a análise ainda é manual, fragmentada ou pouco conectada "
                "à decisão gerencial."
            ),
            "lacunas": [
                {
                    "lacuna": "Análise fragmentada por área",
                    "evidencia": "Cada área acompanha seus próprios dados sem integração suficiente.",
                    "impacto": "Dificulta visão sistêmica do contrato.",
                },
                {
                    "lacuna": "Pouco cruzamento entre indicadores",
                    "evidencia": "Satisfação, uso, renovação, reclamações e risco nem sempre são analisados conjuntamente.",
                    "impacto": "Reduz capacidade de identificar causas e priorizar ações.",
                },
                {
                    "lacuna": "Baixa conversão de dados em narrativa de valor",
                    "evidencia": "Os dados existem, mas nem sempre são traduzidos para o cliente como benefício percebido.",
                    "impacto": "Enfraquece a demonstração de valor e a sustentação da renovação.",
                },
            ],
            "recomendacao": (
                "Integrar dados operacionais, relacionais e contratuais em uma leitura única, com análise "
                "de tendências, riscos e valor percebido."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "Há evidências e indicadores relevantes, mas a maturidade ainda pode avançar em integração, "
                "automação e uso preditivo dos dados."
            ),
            "lacunas": [
                {
                    "lacuna": "Integração parcial de bases",
                    "evidencia": "Alguns indicadores são acompanhados, mas ainda podem permanecer em bases separadas.",
                    "impacto": "Limita análises mais profundas sobre causas e efeitos.",
                },
                {
                    "lacuna": "Uso ainda descritivo dos dados",
                    "evidencia": "Os dados explicam o passado, mas nem sempre antecipam riscos futuros.",
                    "impacto": "Reduz a capacidade preventiva do pós-venda.",
                },
                {
                    "lacuna": "Indicadores pouco vinculados ao roadmap",
                    "evidencia": "Nem todos os indicadores se conectam diretamente a ações de melhoria.",
                    "impacto": "Pode gerar monitoramento sem consequência gerencial.",
                },
            ],
            "recomendacao": (
                "Evoluir o painel de evidências para modelo analítico de decisão, conectando indicadores, "
                "tendências, riscos, ações e resultados."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A gestão por evidências está consolidada. A oportunidade está em avançar para analytics, "
                "benchmarking e inteligência preditiva."
            ),
            "lacunas": [
                {
                    "lacuna": "Benchmarking ainda pouco explorado",
                    "evidencia": "Os dados internos podem ser comparados de modo mais sistemático entre contratos e segmentos.",
                    "impacto": "Limita a identificação de padrões superiores de desempenho.",
                },
                {
                    "lacuna": "Automação preditiva parcial",
                    "evidencia": "Nem todos os alertas de risco e oportunidade são automatizados.",
                    "impacto": "Pode reduzir velocidade de resposta.",
                },
                {
                    "lacuna": "Aprendizagem analítica ainda expansível",
                    "evidencia": "Insights podem ser melhor traduzidos em inovação e redesenho de serviços.",
                    "impacto": "Reduz o potencial estratégico da base de dados.",
                },
            ],
            "recomendacao": (
                "Implantar analytics avançado, benchmarking e alertas preditivos para apoiar decisões "
                "de retenção, expansão, melhoria e inovação."
            ),
        },
    },

    "jornada": {
        "Incipiente": {
            "diagnostico": (
                "A jornada do cliente ainda não está formalmente estruturada como instrumento de gestão. "
                "Predomina uma lógica operacional de entrega."
            ),
            "lacunas": [
                {
                    "lacuna": "Ausência de mapa de jornada",
                    "evidencia": "As etapas do relacionamento não estão descritas sob a ótica da experiência.",
                    "impacto": "Dificulta identificar pontos de fricção, risco e geração de valor.",
                },
                {
                    "lacuna": "Contatos majoritariamente reativos",
                    "evidencia": "A interação ocorre principalmente diante de dúvidas, problemas ou demandas.",
                    "impacto": "Reduz a capacidade de antecipar necessidades do cliente.",
                },
                {
                    "lacuna": "Renovação tratada como evento isolado",
                    "evidencia": "O processo de renovação não está suficientemente conectado à trajetória do contrato.",
                    "impacto": "Enfraquece retenção e demonstração de valor acumulado.",
                },
            ],
            "recomendacao": (
                "Mapear a jornada de pós-venda com etapas, marcos, responsáveis, riscos, mensagens e "
                "indicadores de experiência."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Há marcos operacionais de acompanhamento, mas a jornada ainda não é plenamente gerida "
                "como experiência contínua de valor."
            ),
            "lacunas": [
                {
                    "lacuna": "Jornada mais operacional do que gerencial",
                    "evidencia": "As etapas existem, mas estão centradas na execução e não na experiência.",
                    "impacto": "Reduz a capacidade de identificar valor percebido e fricções.",
                },
                {
                    "lacuna": "Régua de comunicação insuficiente",
                    "evidencia": "Não há cadência padronizada de contato por etapa.",
                    "impacto": "Pode gerar insegurança, baixa adesão ou percepção de ausência.",
                },
                {
                    "lacuna": "Pouca conexão entre jornada e indicadores",
                    "evidencia": "As fases do contrato nem sempre possuem métricas próprias.",
                    "impacto": "Dificulta avaliar onde ocorrem problemas e oportunidades.",
                },
            ],
            "recomendacao": (
                "Desenhar régua de comunicação e checkpoints por etapa, vinculando jornada, satisfação, "
                "uso, risco e valor percebido."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A jornada apresenta estrutura reconhecível, mas pode avançar em personalização, análise "
                "de fricções e integração com resultados contratuais."
            ),
            "lacunas": [
                {
                    "lacuna": "Personalização limitada da jornada",
                    "evidencia": "A mesma lógica de acompanhamento pode ser aplicada a contratos com perfis distintos.",
                    "impacto": "Reduz aderência e relevância da experiência.",
                },
                {
                    "lacuna": "Fricções pouco analisadas como causa sistêmica",
                    "evidencia": "Problemas são resolvidos, mas nem sempre usados para redesenhar a jornada.",
                    "impacto": "Aumenta risco de recorrência.",
                },
                {
                    "lacuna": "Baixa conexão com expansão e renovação",
                    "evidencia": "A jornada nem sempre alimenta decisões comerciais e estratégicas.",
                    "impacto": "Limita a contribuição da experiência para retenção e crescimento.",
                },
            ],
            "recomendacao": (
                "Integrar jornada a indicadores de valor, risco, renovação e expansão, com análise de "
                "causa raiz dos pontos de fricção."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A jornada está formalizada e acompanhada. A evolução recomendada envolve orquestração "
                "por dados e personalização em escala."
            ),
            "lacunas": [
                {
                    "lacuna": "Orquestração em tempo real ainda limitada",
                    "evidencia": "A jornada pode depender de rituais fixos, sem adaptação automática a sinais de comportamento.",
                    "impacto": "Pode reduzir agilidade em situações de risco ou oportunidade.",
                },
                {
                    "lacuna": "Personalização avançada ainda expansível",
                    "evidencia": "Segmentações podem não capturar todas as diferenças de perfil dos contratos.",
                    "impacto": "Limita diferenciação da experiência.",
                },
                {
                    "lacuna": "Integração com ecossistema externo",
                    "evidencia": "A jornada pode não contemplar plenamente parceiros e atores indiretos.",
                    "impacto": "Reduz visão sistêmica da experiência.",
                },
            ],
            "recomendacao": (
                "Evoluir para jornada orquestrada por dados, com alertas, segmentação dinâmica e personalização "
                "das interações conforme comportamento e risco."
            ),
        },
    },

    "governanca": {
        "Incipiente": {
            "diagnostico": (
                "A governança do pós-venda apresenta baixa formalização. Papéis, fluxos e critérios de decisão "
                "ainda dependem de arranjos informais."
            ),
            "lacunas": [
                {
                    "lacuna": "Papéis e responsabilidades não formalizados",
                    "evidencia": "Não há matriz clara de responsabilidades para acompanhamento contratual.",
                    "impacto": "Pode gerar sobreposição, omissão ou demora na resposta.",
                },
                {
                    "lacuna": "Ausência de critérios de escalonamento",
                    "evidencia": "Problemas críticos podem ser tratados conforme julgamento individual.",
                    "impacto": "Aumenta risco de inconsistência e atraso decisório.",
                },
                {
                    "lacuna": "Dependência de pessoas-chave",
                    "evidencia": "Conhecimento e decisão se concentram em poucos profissionais.",
                    "impacto": "Fragiliza continuidade e governança institucional.",
                },
            ],
            "recomendacao": (
                "Formalizar matriz RACI, ritos de acompanhamento, critérios de criticidade e fluxo de escalonamento "
                "para a gestão contratual."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Existem responsáveis e práticas de coordenação, mas ainda sem governança plenamente formalizada, "
                "rastreável e sustentada por indicadores."
            ),
            "lacunas": [
                {
                    "lacuna": "Rituais sem pauta estruturada",
                    "evidencia": "Reuniões e acompanhamentos podem ocorrer sem padrão mínimo de análise.",
                    "impacto": "Reduz consistência da decisão e da priorização.",
                },
                {
                    "lacuna": "Escalonamento informal",
                    "evidencia": "O encaminhamento de problemas depende de redes pessoais e experiência acumulada.",
                    "impacto": "Pode atrasar respostas a situações críticas.",
                },
                {
                    "lacuna": "Baixa transparência de pendências",
                    "evidencia": "Status, responsáveis e prazos podem não estar visíveis para todas as áreas envolvidas.",
                    "impacto": "Dificulta coordenação e responsabilização.",
                },
            ],
            "recomendacao": (
                "Implantar fluxo formal de governança com pauta, ata, responsáveis, prazos, critérios de criticidade "
                "e painel de pendências."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A governança apresenta estrutura reconhecível, mas ainda pode avançar em integração interáreas, "
                "automação e homogeneidade entre contratos."
            ),
            "lacunas": [
                {
                    "lacuna": "Governança desigual entre contratos",
                    "evidencia": "Contratos maiores podem receber acompanhamento mais estruturado do que contratos menores.",
                    "impacto": "Gera variação de qualidade e risco de inconsistência institucional.",
                },
                {
                    "lacuna": "Integração parcial entre níveis operacional e estratégico",
                    "evidencia": "Nem todas as decisões operacionais são conectadas a fóruns estratégicos.",
                    "impacto": "Pode limitar aprendizado e tomada de decisão de maior alcance.",
                },
                {
                    "lacuna": "Automação limitada de fluxos",
                    "evidencia": "Escalonamentos e aprovações podem depender de controles manuais.",
                    "impacto": "Reduz eficiência e rastreabilidade.",
                },
            ],
            "recomendacao": (
                "Homogeneizar a governança por níveis de contrato, conectando fóruns operacionais e estratégicos "
                "e automatizando fluxos críticos."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A governança está consolidada. O desafio passa a ser manter agilidade, integração ecossistêmica "
                "e melhoria contínua."
            ),
            "lacunas": [
                {
                    "lacuna": "Agilidade decisória em estrutura complexa",
                    "evidencia": "Governanças robustas podem criar camadas excessivas de decisão.",
                    "impacto": "Pode reduzir velocidade de resposta.",
                },
                {
                    "lacuna": "Integração com parceiros externos",
                    "evidencia": "A governança pode não incluir plenamente atores externos relevantes.",
                    "impacto": "Reduz visão sistêmica de riscos e responsabilidades.",
                },
                {
                    "lacuna": "Avaliação contínua da governança",
                    "evidencia": "Ritos existentes podem não ser avaliados quanto à efetividade.",
                    "impacto": "Pode manter fóruns pouco produtivos ou redundantes.",
                },
            ],
            "recomendacao": (
                "Aprimorar governança ágil, com revisão periódica da efetividade dos fóruns, integração de parceiros "
                "e indicadores de tempo decisório."
            ),
        },
    },

    "acao_estrategica": {
        "Incipiente": {
            "diagnostico": (
                "As ações decorrentes do pós-venda são pouco estruturadas e nem sempre se convertem em melhoria, "
                "aprendizagem ou decisão estratégica."
            ),
            "lacunas": [
                {
                    "lacuna": "Ações sem gestão formal",
                    "evidencia": "Planos de ação podem não apresentar responsável, prazo e indicador.",
                    "impacto": "Dificulta acompanhamento e responsabilização.",
                },
                {
                    "lacuna": "Correção de sintomas",
                    "evidencia": "As ações podem focar na resolução imediata, sem análise de causa raiz.",
                    "impacto": "Aumenta risco de recorrência.",
                },
                {
                    "lacuna": "Baixa aprendizagem organizacional",
                    "evidencia": "Melhorias ficam restritas a casos específicos ou pessoas envolvidas.",
                    "impacto": "Reduz capacidade de replicação e evolução institucional.",
                },
            ],
            "recomendacao": (
                "Criar rotina de gestão de ações com responsável, prazo, causa raiz, indicador de efetividade "
                "e registro de aprendizagem."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Há ações geradas pelo acompanhamento, mas sua efetividade ainda não é medida de forma consistente "
                "e o aprendizado não é plenamente disseminado."
            ),
            "lacunas": [
                {
                    "lacuna": "Baixa rastreabilidade das ações",
                    "evidencia": "Nem todas as ações possuem status, responsável e evidência de conclusão.",
                    "impacto": "Dificulta comprovar melhoria e prestar contas ao cliente.",
                },
                {
                    "lacuna": "Indicadores de resultado insuficientes",
                    "evidencia": "A ação é encerrada pela execução, não necessariamente pelo efeito gerado.",
                    "impacto": "Reduz a capacidade de avaliar impacto real.",
                },
                {
                    "lacuna": "Aprendizado pouco disseminado",
                    "evidencia": "Lições extraídas de contratos não são sistematicamente compartilhadas.",
                    "impacto": "A organização perde oportunidade de melhoria transversal.",
                },
            ],
            "recomendacao": (
                "Vincular cada ação a indicador de resultado, evidência de conclusão e mecanismo de disseminação "
                "do aprendizado."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A organização gera ações e acompanha parte dos resultados, mas pode avançar em inteligência, "
                "priorização e conexão com retenção, expansão e inovação."
            ),
            "lacunas": [
                {
                    "lacuna": "Priorização estratégica limitada",
                    "evidencia": "As ações podem ser priorizadas por urgência, sem ponderação de impacto.",
                    "impacto": "Pode deslocar energia para problemas de menor relevância estratégica.",
                },
                {
                    "lacuna": "Baixa conexão com renovação e expansão",
                    "evidencia": "As ações nem sempre se vinculam a objetivos de retenção, crescimento ou valor.",
                    "impacto": "Reduz contribuição estratégica do pós-venda.",
                },
                {
                    "lacuna": "Inovação pouco alimentada pelo pós-venda",
                    "evidencia": "Os achados do relacionamento podem não chegar ao desenvolvimento de serviços.",
                    "impacto": "Limita melhoria de portfólio e diferenciação competitiva.",
                },
            ],
            "recomendacao": (
                "Criar matriz de priorização de ações por impacto, risco e valor, conectando pós-venda a retenção, "
                "expansão e inovação em serviços."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A ação estratégica está consolidada. O foco passa a ser escala, inovação contínua e mensuração "
                "avançada de impacto."
            ),
            "lacunas": [
                {
                    "lacuna": "Mensuração avançada de impacto",
                    "evidencia": "Pode haver oportunidade de isolar melhor efeitos das ações sobre indicadores de negócio.",
                    "impacto": "Limita precisão da avaliação estratégica.",
                },
                {
                    "lacuna": "Escala da aprendizagem",
                    "evidencia": "Aprendizados podem ser sistematizados com maior velocidade entre unidades e contratos.",
                    "impacto": "Reduz velocidade de difusão de boas práticas.",
                },
                {
                    "lacuna": "Portfólio de inovação orientado pelo cliente",
                    "evidencia": "A base de pós-venda pode alimentar ainda mais a agenda de inovação.",
                    "impacto": "Pode limitar potencial de diferenciação.",
                },
            ],
            "recomendacao": (
                "Implantar governança de aprendizagem e inovação orientada pelo pós-venda, com indicadores de "
                "impacto, replicação e evolução de portfólio."
            ),
        },
    },

    "qualificacao": {
        "Incipiente": {
            "diagnostico": (
                "O feedback ainda não é qualificado de forma consistente. Reclamações, dúvidas, sugestões e riscos "
                "podem ser tratados sem diferenciação suficiente."
            ),
            "lacunas": [
                {
                    "lacuna": "Ausência de taxonomia formal",
                    "evidencia": "Não há categorias padronizadas para classificar manifestações.",
                    "impacto": "Dificulta análise, priorização e tratamento adequado.",
                },
                {
                    "lacuna": "Classificação subjetiva",
                    "evidencia": "A interpretação depende de quem registra o feedback.",
                    "impacto": "Gera inconsistência e reduz comparabilidade dos dados.",
                },
                {
                    "lacuna": "Baixa identificação de causa",
                    "evidencia": "A manifestação pode ser registrada sem análise de origem ou causa raiz.",
                    "impacto": "Aumenta risco de tratar sintomas e não problemas estruturais.",
                },
            ],
            "recomendacao": (
                "Criar taxonomia formal de feedback, com categorias, critérios de classificação, criticidade "
                "e campos mínimos obrigatórios."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Existem categorias básicas, mas os critérios de classificação ainda são pouco objetivos "
                "e podem variar entre equipes."
            ),
            "lacunas": [
                {
                    "lacuna": "Critérios de classificação insuficientes",
                    "evidencia": "As categorias existem, mas não possuem definições operacionais claras.",
                    "impacto": "Pode gerar registros inconsistentes.",
                },
                {
                    "lacuna": "Campos mínimos incompletos",
                    "evidencia": "Nem todo feedback contém origem, canal, serviço, etapa, impacto e criticidade.",
                    "impacto": "Limita análise gerencial e priorização.",
                },
                {
                    "lacuna": "Baixa diferenciação entre demanda e risco",
                    "evidencia": "Manifestações com potencial crítico podem ser tratadas como demandas comuns.",
                    "impacto": "Pode atrasar escalonamento e resposta preventiva.",
                },
            ],
            "recomendacao": (
                "Padronizar critérios de classificação e tornar obrigatórios os campos mínimos para registro "
                "e análise gerencial do feedback."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A qualificação do feedback apresenta estrutura reconhecível, mas pode evoluir em automação, "
                "consistência e análise de causa."
            ),
            "lacunas": [
                {
                    "lacuna": "Validação de consistência limitada",
                    "evidencia": "Classificações podem não ser auditadas periodicamente.",
                    "impacto": "Mantém risco de distorções na base de feedbacks.",
                },
                {
                    "lacuna": "Análise de causa ainda parcial",
                    "evidencia": "Nem todos os feedbacks críticos passam por método estruturado de causa raiz.",
                    "impacto": "Reduz efetividade das ações corretivas.",
                },
                {
                    "lacuna": "Automação inicial insuficiente",
                    "evidencia": "A classificação pode depender de operação manual.",
                    "impacto": "Limita escala e velocidade da análise.",
                },
            ],
            "recomendacao": (
                "Implementar auditoria de classificação, análise de causa raiz para feedbacks críticos "
                "e apoio automatizado à categorização."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A qualificação do feedback está consolidada. A evolução está na inteligência preditiva "
                "e na análise avançada de padrões."
            ),
            "lacunas": [
                {
                    "lacuna": "Classificação preditiva expansível",
                    "evidencia": "A taxonomia pode ser apoiada por modelos de recomendação e detecção automática.",
                    "impacto": "Pode aumentar velocidade e precisão da triagem.",
                },
                {
                    "lacuna": "Análise avançada de sentimento e risco",
                    "evidencia": "Feedbacks textuais podem conter sinais não capturados por categorias tradicionais.",
                    "impacto": "Pode limitar antecipação de riscos reputacionais ou relacionais.",
                },
                {
                    "lacuna": "Aprendizado contínuo da taxonomia",
                    "evidencia": "Categorias podem exigir atualização conforme novos padrões aparecem.",
                    "impacto": "Risco de defasagem do modelo de classificação.",
                },
            ],
            "recomendacao": (
                "Evoluir para classificação assistida por IA, análise de sentimento, detecção de risco "
                "e atualização contínua da taxonomia."
            ),
        },
    },

    "ecossistema_fb": {
        "Incipiente": {
            "diagnostico": (
                "O feedback é tratado sem consideração suficiente sobre a posição do emissor, o público destinatário "
                "da devolutiva e os cuidados institucionais necessários."
            ),
            "lacunas": [
                {
                    "lacuna": "Origem do feedback não estruturada",
                    "evidencia": "O registro pode não diferenciar RH, trabalhador, decisor, liderança ou área técnica.",
                    "impacto": "Dificulta interpretar peso, impacto e natureza da manifestação.",
                },
                {
                    "lacuna": "Devolutiva não segmentada",
                    "evidencia": "O retorno pode ser dado sem adequação ao perfil do interlocutor.",
                    "impacto": "Pode reduzir efetividade relacional e gerar ruído de comunicação.",
                },
                {
                    "lacuna": "Cuidados de confidencialidade pouco definidos",
                    "evidencia": "Feedbacks de saúde exigem critérios claros de proteção de informações sensíveis.",
                    "impacto": "Pode gerar risco ético, jurídico e reputacional.",
                },
            ],
            "recomendacao": (
                "Incluir campos obrigatórios de origem, papel do emissor, público da devolutiva e critérios "
                "de confidencialidade para feedbacks sensíveis."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "A origem do feedback é reconhecida, mas ainda não há gestão sistemática do ecossistema relacional "
                "envolvido na manifestação."
            ),
            "lacunas": [
                {
                    "lacuna": "Baixa diferenciação do papel de quem fala",
                    "evidencia": "O feedback pode ser registrado sem distinguir emissor formal, usuário final ou influenciador.",
                    "impacto": "Dificulta calibrar prioridade e devolutiva.",
                },
                {
                    "lacuna": "Destinatário da resposta pouco definido",
                    "evidencia": "Nem sempre há clareza sobre quem deve receber o retorno.",
                    "impacto": "Pode gerar fechamento incompleto do loop.",
                },
                {
                    "lacuna": "Baixa leitura do impacto ecossistêmico",
                    "evidencia": "O feedback é tratado como manifestação isolada.",
                    "impacto": "Pode ocultar efeitos sobre adesão, confiança e renovação.",
                },
            ],
            "recomendacao": (
                "Mapear a cadeia de emissão e devolutiva do feedback, definindo quem registra, quem trata, "
                "quem responde e quem precisa ser informado."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "Há reconhecimento das origens do feedback, mas a gestão pode avançar em segmentação, "
                "devolutiva e análise de influência."
            ),
            "lacunas": [
                {
                    "lacuna": "Segmentação de devolutiva ainda parcial",
                    "evidencia": "O tipo de retorno nem sempre varia conforme público e criticidade.",
                    "impacto": "Reduz efetividade da comunicação.",
                },
                {
                    "lacuna": "Influenciadores pouco monitorados",
                    "evidencia": "Atores que amplificam percepções podem não ser acompanhados.",
                    "impacto": "Pode aumentar risco relacional.",
                },
                {
                    "lacuna": "Baixa conexão com mapa de stakeholders",
                    "evidencia": "Feedbacks nem sempre atualizam a leitura do ecossistema contratual.",
                    "impacto": "Perde-se oportunidade de inteligência relacional.",
                },
            ],
            "recomendacao": (
                "Integrar o feedback ao mapa de stakeholders, diferenciando devolutiva técnica, relacional "
                "e executiva conforme origem, impacto e criticidade."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "O ecossistema do feedback está bem gerido. A evolução recomendada envolve inteligência relacional "
                "e monitoramento de padrões entre atores."
            ),
            "lacunas": [
                {
                    "lacuna": "Análise de redes de influência",
                    "evidencia": "Os padrões de emissão e impacto podem ser analisados de forma mais avançada.",
                    "impacto": "Permite antecipar riscos e mobilizar atores-chave.",
                },
                {
                    "lacuna": "Benchmark relacional pouco explorado",
                    "evidencia": "Padrões de feedback por perfil de ator podem ser comparados entre contratos.",
                    "impacto": "Limita aprendizado entre contextos similares.",
                },
                {
                    "lacuna": "Automação de recomendações de devolutiva",
                    "evidencia": "A definição do tipo de resposta pode depender de julgamento manual.",
                    "impacto": "Reduz consistência em escala.",
                },
            ],
            "recomendacao": (
                "Evoluir para inteligência relacional do feedback, com análise de redes de influência, "
                "padrões por ator e recomendação automatizada de devolutiva."
            ),
        },
    },

    "evidencias_fb": {
        "Incipiente": {
            "diagnostico": (
                "Os feedbacks ainda não se consolidam como base gerencial. O registro é insuficiente, disperso "
                "ou pouco utilizável para análise."
            ),
            "lacunas": [
                {
                    "lacuna": "Registro descentralizado",
                    "evidencia": "Feedbacks podem permanecer em e-mails, planilhas, mensagens ou memória das equipes.",
                    "impacto": "Dificulta rastreabilidade e análise institucional.",
                },
                {
                    "lacuna": "Campos mínimos ausentes",
                    "evidencia": "Informações como origem, canal, serviço, etapa, criticidade e impacto podem não ser registradas.",
                    "impacto": "Reduz qualidade analítica da base.",
                },
                {
                    "lacuna": "Ausência de análise de recorrência",
                    "evidencia": "Manifestações semelhantes podem ser tratadas como casos isolados.",
                    "impacto": "Aumenta risco de reincidência e desperdício de aprendizagem.",
                },
            ],
            "recomendacao": (
                "Centralizar os feedbacks em base estruturada com campos mínimos obrigatórios e rotina de análise "
                "de recorrência."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "O registro existe, mas ainda não produz evidência gerencial suficiente para priorização, "
                "prevenção e decisão."
            ),
            "lacunas": [
                {
                    "lacuna": "Base de feedback incompleta",
                    "evidencia": "Registros podem não conter dados suficientes para análise comparável.",
                    "impacto": "Dificulta identificar padrões e priorizar ações.",
                },
                {
                    "lacuna": "Análise manual e reativa",
                    "evidencia": "A leitura dos feedbacks depende de esforço pontual das equipes.",
                    "impacto": "Reduz velocidade de detecção de problemas recorrentes.",
                },
                {
                    "lacuna": "Pouca conexão com impacto contratual",
                    "evidencia": "O feedback nem sempre é associado a risco, adesão, satisfação ou renovação.",
                    "impacto": "Enfraquece o uso estratégico da informação.",
                },
            ],
            "recomendacao": (
                "Aprimorar a base de feedbacks com campos obrigatórios, análise periódica de recorrência "
                "e vínculo com indicadores contratuais."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "Há base de registros e evidências, mas a análise pode avançar em automação, cruzamento de dados "
                "e identificação de padrões."
            ),
            "lacunas": [
                {
                    "lacuna": "Recorrência pouco automatizada",
                    "evidencia": "A identificação de padrões pode depender de análise manual.",
                    "impacto": "Reduz capacidade preventiva.",
                },
                {
                    "lacuna": "Cruzamento limitado com outros indicadores",
                    "evidencia": "Feedbacks nem sempre são analisados junto a satisfação, uso e renovação.",
                    "impacto": "Dificulta compreender impacto real no contrato.",
                },
                {
                    "lacuna": "Baixa visualização gerencial",
                    "evidencia": "A base pode existir sem painel específico de tendências e criticidade.",
                    "impacto": "Limita decisão rápida e priorização.",
                },
            ],
            "recomendacao": (
                "Implementar painel gerencial de feedbacks com recorrência, criticidade, causa, tendência "
                "e vínculo com indicadores de contrato."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "As evidências do feedback estão consolidadas. A evolução envolve análise preditiva e integração "
                "com inteligência de melhoria contínua."
            ),
            "lacunas": [
                {
                    "lacuna": "Predição de reincidência",
                    "evidencia": "A base pode ser explorada para antecipar problemas antes da manifestação explícita.",
                    "impacto": "Aumenta capacidade preventiva.",
                },
                {
                    "lacuna": "Análise semântica avançada",
                    "evidencia": "Feedbacks textuais podem conter padrões não capturados por campos estruturados.",
                    "impacto": "Pode limitar profundidade analítica.",
                },
                {
                    "lacuna": "Benchmark entre contratos",
                    "evidencia": "Padrões de feedback podem ser comparados entre serviços, unidades e segmentos.",
                    "impacto": "Amplia aprendizagem e priorização estratégica.",
                },
            ],
            "recomendacao": (
                "Evoluir para análise preditiva e semântica dos feedbacks, com benchmarking entre contratos "
                "e alertas de reincidência."
            ),
        },
    },

    "jornada_fb": {
        "Incipiente": {
            "diagnostico": (
                "O feedback não está conectado de forma suficiente à etapa da jornada em que surgiu, dificultando "
                "a identificação de fricções e causas sistêmicas."
            ),
            "lacunas": [
                {
                    "lacuna": "Feedback sem etapa de origem",
                    "evidencia": "O registro não indica claramente em que momento da jornada a manifestação ocorreu.",
                    "impacto": "Dificulta localizar o ponto de fricção.",
                },
                {
                    "lacuna": "Baixa análise preventiva",
                    "evidencia": "Feedbacks são tratados como episódios isolados.",
                    "impacto": "Reduz capacidade de prevenir recorrências em etapas críticas.",
                },
                {
                    "lacuna": "Pouca conexão com redesenho de processo",
                    "evidencia": "A manifestação não alimenta sistematicamente melhorias na jornada.",
                    "impacto": "Mantém problemas estruturais sem correção.",
                },
            ],
            "recomendacao": (
                "Tornar obrigatória a vinculação do feedback à etapa da jornada e usar essa informação "
                "para priorizar melhorias de processo."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Há alguma menção à etapa de origem, mas o uso gerencial dessa informação ainda é inconsistente."
            ),
            "lacunas": [
                {
                    "lacuna": "Registro irregular da etapa",
                    "evidencia": "A etapa da jornada pode ser preenchida de modo incompleto ou não padronizado.",
                    "impacto": "Reduz confiabilidade da análise.",
                },
                {
                    "lacuna": "Fricções pouco agrupadas por fase",
                    "evidencia": "Feedbacks semelhantes em uma mesma etapa podem não ser analisados conjuntamente.",
                    "impacto": "Dificulta priorização de melhorias estruturais.",
                },
                {
                    "lacuna": "Baixa retroalimentação da jornada",
                    "evidencia": "A análise do feedback nem sempre altera a régua de comunicação ou os processos.",
                    "impacto": "Reduz aprendizagem e prevenção.",
                },
            ],
            "recomendacao": (
                "Padronizar o campo de etapa da jornada e instituir análise periódica de fricções por fase, "
                "com plano de melhoria associado."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "O feedback é associado à jornada, mas a organização pode avançar na análise de padrões, "
                "priorização e redesenho preventivo."
            ),
            "lacunas": [
                {
                    "lacuna": "Análise por etapa ainda pouco aprofundada",
                    "evidencia": "Há vínculo com a jornada, mas nem sempre há leitura de causa por fase.",
                    "impacto": "Limita correção sistêmica.",
                },
                {
                    "lacuna": "Priorização de fricções insuficiente",
                    "evidencia": "Problemas por etapa podem não ser priorizados por impacto e recorrência.",
                    "impacto": "Pode direcionar esforços para pontos menos críticos.",
                },
                {
                    "lacuna": "Integração parcial com experiência do cliente",
                    "evidencia": "Feedbacks por etapa nem sempre alimentam indicadores de experiência.",
                    "impacto": "Reduz visão integrada da jornada.",
                },
            ],
            "recomendacao": (
                "Criar painel de fricções por etapa da jornada, com criticidade, recorrência, causa raiz "
                "e plano de melhoria."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A jornada do feedback está consolidada. A evolução envolve antecipação de fricções e orquestração "
                "de respostas por etapa."
            ),
            "lacunas": [
                {
                    "lacuna": "Predição de fricções por etapa",
                    "evidencia": "A base pode permitir antecipação de problemas recorrentes.",
                    "impacto": "Amplia a capacidade preventiva.",
                },
                {
                    "lacuna": "Orquestração automática de respostas",
                    "evidencia": "A resposta pode ser calibrada automaticamente conforme etapa e criticidade.",
                    "impacto": "Aumenta consistência e velocidade de tratamento.",
                },
                {
                    "lacuna": "Benchmark de jornada",
                    "evidencia": "Fricções por etapa podem ser comparadas entre contratos e serviços.",
                    "impacto": "Aprimora aprendizado e priorização institucional.",
                },
            ],
            "recomendacao": (
                "Evoluir para monitoramento preditivo de fricções por etapa, com resposta orientada por dados "
                "e benchmarking entre jornadas."
            ),
        },
    },

    "governanca_fb": {
        "Incipiente": {
            "diagnostico": (
                "A governança do feedback é pouco formalizada. Não há fluxo suficientemente claro para registro, "
                "priorização, tratativa, escalonamento e fechamento."
            ),
            "lacunas": [
                {
                    "lacuna": "Ausência de fluxo institucional de tratativa",
                    "evidencia": "O feedback pode ser encaminhado de modo informal.",
                    "impacto": "Aumenta risco de perda, atraso ou resposta inconsistente.",
                },
                {
                    "lacuna": "Prazos e responsáveis indefinidos",
                    "evidencia": "Nem todo feedback possui dono, prazo e status.",
                    "impacto": "Compromete rastreabilidade e responsabilização.",
                },
                {
                    "lacuna": "Criticidade não padronizada",
                    "evidencia": "A priorização depende de julgamento individual.",
                    "impacto": "Pode atrasar tratamento de feedbacks críticos.",
                },
            ],
            "recomendacao": (
                "Definir fluxo institucional de feedback com responsável, prazo, status, criticidade, "
                "escalonamento e fechamento de loop."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Existe fluxo básico de tratativa, mas ainda há fragilidades em prazos, critérios de criticidade, "
                "responsabilização e devolutiva."
            ),
            "lacunas": [
                {
                    "lacuna": "SLAs pouco formalizados",
                    "evidencia": "O tempo de resposta pode variar conforme equipe, canal ou tipo de manifestação.",
                    "impacto": "Gera inconsistência e risco de insatisfação.",
                },
                {
                    "lacuna": "Escalonamento insuficiente",
                    "evidencia": "Feedbacks críticos podem não ter rota clara para decisão superior.",
                    "impacto": "Pode atrasar resolução de problemas sensíveis.",
                },
                {
                    "lacuna": "Fechamento de loop inconsistente",
                    "evidencia": "Nem sempre há registro de devolutiva e encerramento formal.",
                    "impacto": "Reduz confiança e transparência perante o cliente.",
                },
            ],
            "recomendacao": (
                "Formalizar SLAs, matriz de criticidade, responsáveis por etapa, regra de escalonamento "
                "e registro obrigatório de devolutiva."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A governança do feedback está parcialmente estruturada, mas pode evoluir em consistência, "
                "monitoramento e integração com decisões gerenciais."
            ),
            "lacunas": [
                {
                    "lacuna": "Monitoramento parcial dos prazos",
                    "evidencia": "SLAs podem existir, mas nem sempre são acompanhados por indicador.",
                    "impacto": "Dificulta gestão de desempenho da tratativa.",
                },
                {
                    "lacuna": "Comitê de feedback pouco sistemático",
                    "evidencia": "Feedbacks críticos podem não ser discutidos em fórum recorrente.",
                    "impacto": "Reduz aprendizagem e priorização institucional.",
                },
                {
                    "lacuna": "Baixa integração com governança contratual",
                    "evidencia": "Feedbacks tratados nem sempre alimentam a gestão do contrato.",
                    "impacto": "Perde-se oportunidade de antecipar riscos e melhorar valor percebido.",
                },
            ],
            "recomendacao": (
                "Criar rotina de governança do feedback com indicadores de SLA, comitê de casos críticos "
                "e integração com a gestão contratual."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A governança do feedback está consolidada. O foco passa a ser automação, eficiência e "
                "aprendizagem institucional em escala."
            ),
            "lacunas": [
                {
                    "lacuna": "Automação de fluxos críticos",
                    "evidencia": "Parte das decisões pode ser apoiada por alertas e regras automáticas.",
                    "impacto": "Aumenta velocidade e consistência.",
                },
                {
                    "lacuna": "Avaliação de qualidade da devolutiva",
                    "evidencia": "A resposta pode ser monitorada não apenas por prazo, mas por qualidade percebida.",
                    "impacto": "Aprimora confiança e satisfação.",
                },
                {
                    "lacuna": "Integração com aprendizagem organizacional",
                    "evidencia": "A governança pode alimentar melhor a revisão de processos e serviços.",
                    "impacto": "Amplia melhoria contínua.",
                },
            ],
            "recomendacao": (
                "Automatizar fluxos críticos, monitorar qualidade da devolutiva e integrar feedbacks tratados "
                "à governança de aprendizagem."
            ),
        },
    },

    "acao_fb": {
        "Incipiente": {
            "diagnostico": (
                "O feedback ainda gera poucas ações rastreáveis e sua contribuição para aprendizagem e melhoria "
                "não está institucionalizada."
            ),
            "lacunas": [
                {
                    "lacuna": "Ação sem vínculo claro com feedback",
                    "evidencia": "Nem toda manifestação gera registro de providência adotada.",
                    "impacto": "Dificulta comprovar consequência e fechamento do ciclo.",
                },
                {
                    "lacuna": "Ausência de validação de impacto",
                    "evidencia": "A ação pode ser considerada concluída sem verificar resultado.",
                    "impacto": "Reduz efetividade da melhoria.",
                },
                {
                    "lacuna": "Aprendizagem retida em indivíduos",
                    "evidencia": "As lições aprendidas não são sistematizadas.",
                    "impacto": "Aumenta risco de reincidência.",
                },
            ],
            "recomendacao": (
                "Vincular cada feedback tratado a uma ação, responsável, prazo, evidência de conclusão "
                "e validação de impacto."
            ),
        },
        "Inicial": {
            "diagnostico": (
                "Há ações derivadas de feedbacks, mas a avaliação de eficácia, reincidência e disseminação "
                "do aprendizado ainda é limitada."
            ),
            "lacunas": [
                {
                    "lacuna": "Baixa mensuração da efetividade",
                    "evidencia": "A conclusão da ação não necessariamente confirma resolução do problema.",
                    "impacto": "Pode manter causas estruturais sem tratamento adequado.",
                },
                {
                    "lacuna": "Reincidência pouco analisada",
                    "evidencia": "Feedbacks semelhantes podem voltar a ocorrer sem investigação sistêmica.",
                    "impacto": "Gera retrabalho e perda de confiança.",
                },
                {
                    "lacuna": "Melhorias pouco replicadas",
                    "evidencia": "Soluções aplicadas em um contrato nem sempre são disseminadas.",
                    "impacto": "Reduz aprendizagem organizacional.",
                },
            ],
            "recomendacao": (
                "Criar índice de eficácia das ações derivadas de feedback, com análise de reincidência "
                "e mecanismo de replicação de melhorias."
            ),
        },
        "Organizado": {
            "diagnostico": (
                "A ação baseada em feedback está presente, mas pode avançar em priorização estratégica, "
                "mensuração de impacto e retroalimentação do modelo de pós-venda."
            ),
            "lacunas": [
                {
                    "lacuna": "Priorização por impacto ainda parcial",
                    "evidencia": "As ações podem ser tratadas por ordem de chegada e não por impacto estratégico.",
                    "impacto": "Pode reduzir efetividade do esforço institucional.",
                },
                {
                    "lacuna": "Retroalimentação limitada do pós-venda",
                    "evidencia": "O aprendizado do feedback nem sempre altera processos, jornada ou governança.",
                    "impacto": "Reduz capacidade de melhoria sistêmica.",
                },
                {
                    "lacuna": "Baixa visibilidade executiva",
                    "evidencia": "Ações geradas por feedback podem não chegar aos fóruns estratégicos.",
                    "impacto": "Limita tomada de decisão baseada na voz do cliente.",
                },
            ],
            "recomendacao": (
                "Integrar ações derivadas de feedback ao roadmap de melhoria, com priorização por impacto, "
                "reincidência e valor contratual."
            ),
        },
        "Estruturado": {
            "diagnostico": (
                "A organização transforma feedbacks em melhoria de forma consistente. A evolução envolve "
                "inteligência preditiva, inovação e disseminação em escala."
            ),
            "lacunas": [
                {
                    "lacuna": "Predição de impacto das ações",
                    "evidencia": "A base histórica pode apoiar estimativas sobre quais ações geram maior efeito.",
                    "impacto": "Aumenta eficiência da priorização.",
                },
                {
                    "lacuna": "Inovação orientada por feedback",
                    "evidencia": "Feedbacks tratados podem alimentar ainda mais o redesenho de serviços.",
                    "impacto": "Amplia diferenciação e valor percebido.",
                },
                {
                    "lacuna": "Escala da aprendizagem",
                    "evidencia": "Boas práticas podem ser disseminadas com maior velocidade entre unidades.",
                    "impacto": "Reduz reincidência e aumenta maturidade institucional.",
                },
            ],
            "recomendacao": (
                "Evoluir para governança de inovação orientada por feedback, com predição de impacto, "
                "replicação de boas práticas e atualização contínua do modelo de serviço."
            ),
        },
    },
}


# ==========================================================
# FUNÇÕES DE APOIO
# ==========================================================

def get_dimension_name(dimension_key: str) -> str:
    return DIMENSION_NAMES.get(dimension_key, dimension_key.replace("_", " ").title())


def get_dimension_objective(dimension_key: str) -> str:
    return DIMENSION_OBJECTIVES.get(
        dimension_key,
        "Avaliar a maturidade da dimensão no contexto do Framework AVALIA.",
    )


def get_context_rule(dimension_key: str, maturity_label: str) -> dict:
    dimension_rules = CONTEXT_RULES.get(dimension_key, {})

    if maturity_label in dimension_rules:
        return dimension_rules[maturity_label]

    return {
        "diagnostico": (
            f"A dimensão {get_dimension_name(dimension_key)} apresenta maturidade "
            f"{maturity_label}, exigindo análise específica conforme as evidências coletadas."
        ),
        "lacunas": [
            {
                "lacuna": "Lacuna específica não parametrizada",
                "evidencia": "A dimensão requer validação complementar das evidências disponíveis.",
                "impacto": "Pode limitar a precisão do diagnóstico e da intervenção."
            }
        ],
        "recomendacao": (
            f"Revisar a parametrização da dimensão {get_dimension_name(dimension_key)} "
            f"para ampliar a precisão diagnóstica."
        ),
    }


def build_texto_diagnostico(
    dimension_key: str,
    score: float,
    maturity_label: str,
    evidencias_usuario: str,
) -> str:
    objective = get_dimension_objective(dimension_key)
    rule = get_context_rule(dimension_key, maturity_label)
    maturity_description = get_maturity_description(score)

    if evidencias_usuario and evidencias_usuario.strip():
        base_evidence = evidencias_usuario.strip()
    else:
        base_evidence = rule["diagnostico"]

    return (
        f"Objetivo da dimensão: {objective}\n\n"
        f"Interpretação do índice: o resultado de {score:.2f} situa a dimensão no patamar "
        f"{maturity_label}. {maturity_description}\n\n"
        f"Análise qualitativa: {base_evidence}"
    )


def parse_lacunas(rule: dict) -> List[LacunaItem]:
    lacunas = []

    for item in rule.get("lacunas", []):
        lacunas.append(
            LacunaItem(
                lacuna=item.get("lacuna", "Lacuna não especificada"),
                evidencia=item.get("evidencia", "Evidência não especificada"),
                impacto=item.get("impacto", "Impacto não especificado"),
            )
        )

    return lacunas


def process_dimension(dimension_key: str, data: DimensionData) -> AssessmentResult:
    score = normalize_score(data.score)
    maturity_label = get_maturity_label(score)
    rule = get_context_rule(dimension_key, maturity_label)

    texto_diagnostico = build_texto_diagnostico(
        dimension_key=dimension_key,
        score=score,
        maturity_label=maturity_label,
        evidencias_usuario=data.evidencias,
    )

    recommendation = data.recomendacoes.strip() if data.recomendacoes else rule["recomendacao"]

    impacto = data.impacto_estrategico

    if not impacto or impacto == "Automático":
        impacto = sugerir_impacto_estrategico(
            score=score,
            dimension_key=dimension_key,
        )

    prioridade_intervencao = get_priority_label(score, impacto)

    return AssessmentResult(
        dimension_key=dimension_key,
        camada=DIMENSION_LAYER.get(dimension_key, 0),
        dimensao=get_dimension_name(dimension_key),
        score_final=score,
        nivel_maturidade=maturity_label,
        impacto_estrategico_aplicado=impacto,
        prioridade_intervencao=prioridade_intervencao,
        texto_diagnostico=texto_diagnostico,
        recomendacao_estrategica=recommendation,
        lacunas=parse_lacunas(rule),
    )

    return AssessmentResult(
        dimension_key=dimension_key,
        camada=DIMENSION_LAYER.get(dimension_key, 0),
        dimensao=get_dimension_name(dimension_key),
        score_final=score,
        nivel_maturidade=maturity_label,
        prioridade_intervencao=get_priority_label(score, data.impacto_estrategico),
        texto_diagnostico=texto_diagnostico,
        recomendacao_estrategica=recommendation,
        lacunas=parse_lacunas(rule),
    )


# ==========================================================
# FUNÇÃO PRINCIPAL USADA PELO APP
# ==========================================================

def process_assessment(
    layer1: Dict[str, DimensionData],
    layer2: Dict[str, DimensionData],
) -> List[AssessmentResult]:
    results: List[AssessmentResult] = []

    for dimension_key in DIMENSIONS_C1:
        data = layer1.get(dimension_key, DimensionData(score=0.0))
        results.append(process_dimension(dimension_key, data))

    for dimension_key in DIMENSIONS_C2:
        data = layer2.get(dimension_key, DimensionData(score=0.0))
        results.append(process_dimension(dimension_key, data))

    return results


# ==========================================================
# RESUMO GERENCIAL DO DIAGNÓSTICO
# ==========================================================

def calculate_average(results: List[AssessmentResult], layer: Optional[int] = None) -> float:
    filtered_results = results

    if layer is not None:
        filtered_results = [result for result in results if result.camada == layer]

    if not filtered_results:
        return 0.0

    return round(
        sum(result.score_final for result in filtered_results) / len(filtered_results),
        2,
    )


def summarize_assessment(results: List[AssessmentResult]) -> AssessmentSummary:
    if not results:
        return AssessmentSummary(
            indice_geral=0.0,
            nivel_geral="Incipiente",
            indice_camada_1=0.0,
            nivel_camada_1="Incipiente",
            indice_camada_2=0.0,
            nivel_camada_2="Incipiente",
            principal_forca="Não identificada",
            principal_lacuna="Não identificada",
            dimensoes_criticas=[],
            dimensoes_maior_maturidade=[],
            dimensoes_em_evolucao=[],
        )

    indice_geral = calculate_average(results)
    indice_camada_1 = calculate_average(results, layer=1)
    indice_camada_2 = calculate_average(results, layer=2)

    max_score = max(result.score_final for result in results)
    min_score = min(result.score_final for result in results)

    dimensoes_maior_maturidade = [
        result.dimensao
        for result in results
        if result.score_final == max_score
    ]

    dimensoes_menor_maturidade = [
        result.dimensao
        for result in results
        if result.score_final == min_score
    ]

    dimensoes_criticas = [
        result.dimensao
        for result in results
        if result.score_final < 1.75
    ]

    dimensoes_em_evolucao = [
        result.dimensao
        for result in results
        if 1.75 <= result.score_final < 2.50
    ]

    return AssessmentSummary(
        indice_geral=indice_geral,
        nivel_geral=get_maturity_label(indice_geral),
        indice_camada_1=indice_camada_1,
        nivel_camada_1=get_maturity_label(indice_camada_1),
        indice_camada_2=indice_camada_2,
        nivel_camada_2=get_maturity_label(indice_camada_2),
        principal_forca=", ".join(dimensoes_maior_maturidade),
        principal_lacuna=", ".join(dimensoes_menor_maturidade),
        dimensoes_criticas=dimensoes_criticas,
        dimensoes_maior_maturidade=dimensoes_maior_maturidade,
        dimensoes_em_evolucao=dimensoes_em_evolucao,
    )

def get_maturity_ruler_rows() -> List[List[str]]:
    rows = []

    for item in MATURITY_RULER:
        intervalo = f'{item["min"]:.2f} a {item["max"]:.2f}'
        rows.append([intervalo, item["nivel"], item["descricao"]])

    return rows