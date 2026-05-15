# app.py

import os
import tempfile
import pandas as pd
import plotly.express as px


from datetime import date

import streamlit as st

from framework_engine import (
    DimensionData,
    process_assessment,
    DIMENSIONS_C1,
    DIMENSIONS_C2,
    DIMENSION_NAMES,
    get_priority_label,
    sugerir_impacto_estrategico,
)

from report_generator import generate_report
from doc_parser import DocumentParser
from excel_report_generator import generate_excel_report


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Framework AVALIA SESI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #F5F7FA;
    }

    .main-title {
        font-size: 2.35rem;
        font-weight: 900;
        color: #082B63;
        margin-bottom: 0.15rem;
    }

    .main-subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 1.2rem;
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 1.2rem;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #D9E2EC;
        border-left: 6px solid #0FA3B1;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        min-height: 105px;
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1F2937;
        line-height: 1.1;
    }

    .kpi-help {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 6px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #D9E2EC;
        padding: 10px;
        border-radius: 12px;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
        border: 1px solid #D9E2EC;
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# ESTADO DA SESSÃO
# ==========================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "document_analysis_done" not in st.session_state:
    st.session_state.document_analysis_done = False

if "uploaded_evidence_summary" not in st.session_state:
    st.session_state.uploaded_evidence_summary = {}

if "last_report_path" not in st.session_state:
    st.session_state.last_report_path = None

if "last_excel_bytes" not in st.session_state:
    st.session_state.last_excel_bytes = None


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def get_display_name(dimension_key: str) -> str:
    return DIMENSION_NAMES.get(
        dimension_key,
        dimension_key.replace("_", " ").title(),
    )


def initialize_dimension_fields(dimension_key: str):
    score_key = f"score_{dimension_key}"
    evidence_key = f"evid_{dimension_key}"
    impact_key = f"impact_{dimension_key}"

    if score_key not in st.session_state:
        st.session_state[score_key] = "Não avaliado"

    if evidence_key not in st.session_state:
        st.session_state[evidence_key] = ""

    if impact_key not in st.session_state:
        st.session_state[impact_key] = "Automático"


def score_to_float(selected_score):
    if selected_score == "Não avaliado":
        return None

    try:
        return float(selected_score)
    except (TypeError, ValueError):
        return None


def format_score_option(option):
    if option == "Não avaliado":
        return "Não avaliado"

    return f"{float(option):.1f}"


def extract_evidence_from_files(uploaded_files):
    parser = DocumentParser()
    evidence_by_dimension = {dim: [] for dim in DIMENSIONS_C1 + DIMENSIONS_C2}
    processed_files = []
    errors = []

    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            result = parser.parse_file(tmp_path)

            if "error" in result:
                errors.append(f"{uploaded_file.name}: {result['error']}")
                continue

            processed_files.append(uploaded_file.name)

            for mapping in result.get("mappings", []):
                dimension = mapping.get("dimensao")

                if dimension not in evidence_by_dimension:
                    continue

                evidences = mapping.get("evidencias_encontradas", [])

                for evidence in evidences:
                    if evidence and evidence not in evidence_by_dimension[dimension]:
                        evidence_by_dimension[dimension].append(evidence)

        except Exception as error:
            errors.append(f"{uploaded_file.name}: {error}")

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    return evidence_by_dimension, processed_files, errors


def apply_extracted_evidence_to_session(evidence_by_dimension):
    for dimension_key, evidences in evidence_by_dimension.items():
        if not evidences:
            continue

        evidence_key = f"evid_{dimension_key}"

        formatted_evidence = "\n".join(
            f"- {evidence}" for evidence in evidences[:8]
        )

        current_text = st.session_state.get(evidence_key, "").strip()

        if current_text:
            st.session_state[evidence_key] = (
                f"{current_text}\n\nEvidências extraídas dos documentos:\n{formatted_evidence}"
            )
        else:
            st.session_state[evidence_key] = (
                f"Evidências extraídas dos documentos:\n{formatted_evidence}"
            )


def build_dimension_data(dimension_keys):
    dimension_data = {}

    for dimension_key in dimension_keys:
        score_key = f"score_{dimension_key}"
        evidence_key = f"evid_{dimension_key}"
        impact_key = f"impact_{dimension_key}"

        score = score_to_float(st.session_state.get(score_key))
        evidence = st.session_state.get(evidence_key, "")
        impact = st.session_state.get(impact_key, "Automático")

        dimension_data[dimension_key] = DimensionData(
            score=score,
            evidencias=evidence,
            impacto_estrategico=impact,
        )

    return dimension_data


def get_missing_scores():
    missing = []

    for dimension_key in DIMENSIONS_C1 + DIMENSIONS_C2:
        score = score_to_float(st.session_state.get(f"score_{dimension_key}"))

        if score is None:
            missing.append(get_display_name(dimension_key))

    return missing


def render_dimension_form(dimension_key: str):
    initialize_dimension_fields(dimension_key)

    display_name = get_display_name(dimension_key)

    with st.expander(f"Dimensão: {display_name}", expanded=True):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.selectbox(
                "Índice de maturidade",
                options=[
                    "Não avaliado",
                    0.0,
                    0.5,
                    1.0,
                    1.5,
                    2.0,
                    2.5,
                    3.0,
                ],
                format_func=format_score_option,
                key=f"score_{dimension_key}",
                help=(
                    "Use a escala de 0 a 3. Não deixe como 'Não avaliado' "
                    "se quiser gerar o relatório."
                ),
            )

            selected_score = score_to_float(
                st.session_state.get(f"score_{dimension_key}")
            )

            if selected_score is None:
                impacto_sugerido = sugerir_impacto_estrategico(
                    score=None,
                    dimension_key=dimension_key,
                )
            else:
                impacto_sugerido = sugerir_impacto_estrategico(
                    score=selected_score,
                    dimension_key=dimension_key,
                )

            st.selectbox(
                "Impacto estratégico",
                options=[
                    "Automático",
                    "Baixo",
                    "Médio",
                    "Alto",
                ],
                key=f"impact_{dimension_key}",
                help=(
                    f"Sugestão automática para esta nota: {impacto_sugerido}. "
                    "Use Automático para o sistema aplicar a sugestão."
                ),
            )

            impacto_escolhido = st.session_state.get(
                f"impact_{dimension_key}",
                "Automático",
            )

            if impacto_escolhido == "Automático":
                impacto_para_prioridade = impacto_sugerido
            else:
                impacto_para_prioridade = impacto_escolhido

            if selected_score is not None:
                prioridade_esperada = get_priority_label(
                    selected_score,
                    impacto_para_prioridade,
                )

                st.caption(
                    f"Impacto aplicado: {impacto_para_prioridade} | "
                    f"Prioridade esperada: {prioridade_esperada}"
                )
            else:
                st.caption(
                    "Selecione uma nota para calcular impacto aplicado e prioridade esperada."
                )

        with col2:
            st.text_area(
                "Evidências / Achados qualitativos",
                key=f"evid_{dimension_key}",
                height=160,
                placeholder=(
                    "Descreva evidências, achados, práticas existentes, lacunas percebidas "
                    "ou observações do diagnóstico."
                ),
            )


def render_score_ruler():
    st.subheader("Régua de avaliação da maturidade")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(
            "**Incipiente**\n\n"
            "**0,00 a 0,99**\n\n"
            "Ausência de evidências suficientes, práticas não formalizadas "
            "ou baixa capacidade de gestão estruturada."
        )

    with col2:
        st.warning(
            "**Inicial**\n\n"
            "**1,00 a 1,74**\n\n"
            "Práticas pontuais, pouco formalizadas, dependentes de pessoas "
            "ou aplicadas de modo fragmentado."
        )

    with col3:
        st.success(
            "**Organizado**\n\n"
            "**1,75 a 2,49**\n\n"
            "Práticas reconhecíveis, com algum grau de consistência, "
            "ainda que parcialmente integradas."
        )

    with col4:
        st.success(
            "**Estruturado**\n\n"
            "**2,50 a 3,00**\n\n"
            "Práticas formalizadas, integradas, acompanhadas por indicadores "
            "e usadas para decisão e melhoria contínua."
        )



def render_assessment_status():
    total_dimensions = len(DIMENSIONS_C1 + DIMENSIONS_C2)
    missing_scores = get_missing_scores()
    completed = total_dimensions - len(missing_scores)

    completion_rate = completed / total_dimensions if total_dimensions else 0
    completion_percent = int(completion_rate * 100)

    st.subheader("Status do diagnóstico")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Dimensões avaliadas",
            value=f"{completed}/{total_dimensions}",
        )

    with col2:
        st.metric(
            label="Progresso",
            value=f"{completion_percent}%",
        )

    with col3:
        if missing_scores:
            st.metric(
                label="Situação",
                value="Em preenchimento",
            )
        else:
            st.metric(
                label="Situação",
                value="Pronto",
            )

    st.progress(completion_rate)

    if missing_scores:
        st.caption(
            "Finalize as notas das dimensões antes de gerar os arquivos."
        )
    else:
        st.success(
            "Todas as dimensões foram avaliadas. O relatório e o Excel podem ser gerados."
        )

        



def build_dashboard_dataframe():
    rows = []

    for dimension_key in DIMENSIONS_C1 + DIMENSIONS_C2:
        score = score_to_float(st.session_state.get(f"score_{dimension_key}"))
        impact = st.session_state.get(f"impact_{dimension_key}", "Automático")

        if score is None:
            continue

        if impact == "Automático":
            impact_applied = sugerir_impacto_estrategico(
                score=score,
                dimension_key=dimension_key,
            )
        else:
            impact_applied = impact

        prioridade = get_priority_label(score, impact_applied)
        camada = "Camada 1" if dimension_key in DIMENSIONS_C1 else "Camada 2"

        rows.append(
            {
                "Camada": camada,
                "Dimensão": get_display_name(dimension_key),
                "Nota": score,
                "Impacto": impact_applied,
                "Prioridade": prioridade,
            }
        )

    return pd.DataFrame(rows)


def render_dashboard():
    df = build_dashboard_dataframe()

    st.markdown(
        """
        <div class="dashboard-title">Dashboard AVALIA</div>
        <div class="dashboard-subtitle">
            Painel visual de maturidade, prioridades e distribuição das dimensões avaliadas.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Preencha as notas das dimensões para visualizar o dashboard.")
        return

    indice_geral = round(df["Nota"].mean(), 2)

    camada_1_df = df[df["Camada"] == "Camada 1"]
    camada_2_df = df[df["Camada"] == "Camada 2"]

    camada_1 = round(camada_1_df["Nota"].mean(), 2) if not camada_1_df.empty else 0
    camada_2 = round(camada_2_df["Nota"].mean(), 2) if not camada_2_df.empty else 0

    prioridades_altas = len(df[df["Prioridade"] == "Alta"])
    avaliadas = len(df)

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        (c1, "Índice Geral", indice_geral, "Média das dimensões"),
        (c2, "Camada 1", camada_1, "Gestão de Pós-Venda"),
        (c3, "Camada 2", camada_2, "Feedback Qualificado"),
        (c4, "Prioridades Altas", prioridades_altas, "Foco imediato"),
        (c5, "Dimensões Avaliadas", avaliadas, "Total com nota"),
    ]

    for column, label, value, help_text in cards:
        with column:
            value_text = str(value).replace(".", ",")
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value_text}</div>
                    <div class="kpi-help">{help_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("###")

    col_a, col_b = st.columns([1.6, 1])

    with col_a:
        fig_bar = px.bar(
            df,
            x="Nota",
            y="Dimensão",
            color="Camada",
            orientation="h",
            title="Maturidade por Dimensão",
            text="Nota",
            color_discrete_sequence=["#0FA3B1", "#59C3C3"],
        )
        fig_bar.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=480,
            xaxis_title="Nota",
            yaxis_title="",
            legend_title="",
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        prioridade_count = (
            df.groupby("Prioridade")
            .size()
            .reset_index(name="Quantidade")
        )

        fig_donut = px.pie(
            prioridade_count,
            names="Prioridade",
            values="Quantidade",
            hole=0.65,
            title="Distribuição das Prioridades",
            color="Prioridade",
            color_discrete_map={
                "Alta": "#E76F51",
                "Média": "#F4A261",
                "Monitoramento": "#0FA3B1",
                "Manutenção": "#2E8B57",
            },
        )
        fig_donut.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=480,
            legend_title="",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("### Quadro-resumo")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================================
# MODO ESCURO
# ==========================================================

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #262730;
            border-radius: 4px;
        }
        .stTextInput > div > div > input {
            color: #ffffff;
        }
        .stTextArea > div > div > textarea {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    theme_text = "Mudar para modo claro"
else:
    theme_text = "Ativar modo escuro"


# ==========================================================
# BARRA LATERAL
# ==========================================================

st.sidebar.title("Framework AVALIA")

if st.sidebar.button("Limpar avaliação e reiniciar"):
    for key in list(st.session_state.keys()):
        if (
            key.startswith("score_")
            or key.startswith("impact_")
            or key.startswith("evid_")
        ):
            del st.session_state[key]

    st.session_state.last_report_path = None
    st.session_state.document_analysis_done = False
    st.session_state.uploaded_evidence_summary = {}
    st.rerun()

if st.sidebar.button(theme_text):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("1. Dados da organização")

client_name = st.sidebar.text_input(
    "Nome do cliente / razão social",
    value="Indústria Exemplo LTDA",
)

client_id = st.sidebar.text_input(
    "ID do contrato",
    value="001",
)

unit = st.sidebar.text_input(
    "Área/unidade analisada",
    value="[Preencher]",
)

responsible = st.sidebar.text_input(
    "Responsável pela análise",
    value="Consultor Sênior",
)

period = st.sidebar.date_input(
    "Data da coleta",
    value=date.today(),
)

services = st.sidebar.text_area(
    "Serviços contemplados",
    value="Saúde ocupacional, segurança do trabalho, promoção da saúde",
    height=80,
)

st.sidebar.markdown("---")
st.sidebar.header("2. Upload de evidências")

uploaded_files = st.sidebar.file_uploader(
    "Envie documentos Word ou Excel",
    type=["docx", "xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.sidebar.button("Analisar documentos e preencher evidências"):
        with st.spinner("Processando documentos..."):
            evidence_by_dimension, processed_files, errors = extract_evidence_from_files(
                uploaded_files
            )

            st.session_state.uploaded_evidence_summary = evidence_by_dimension
            st.session_state.document_analysis_done = True

            apply_extracted_evidence_to_session(evidence_by_dimension)

        if processed_files:
            st.sidebar.success(
                f"{len(processed_files)} arquivo(s) processado(s) com sucesso."
            )

        if errors:
            for error in errors:
                st.sidebar.warning(error)

        st.rerun()


# ==========================================================
# CABEÇALHO
# ==========================================================

st.markdown(
    """
    <div class="main-title"> SISTEMA AVALIA: Diagnóstico e Intervenção</div>
    <div class="main-subtitle">
    Ferramenta de avaliação de maturidade para Gestão de Pós-Venda e Feedback Qualificado em Serviços de Saúde
    </div>
    """,
    unsafe_allow_html=True,
)

render_score_ruler()
render_assessment_status()

if st.session_state.document_analysis_done:
    st.success(
        "Evidências extraídas dos documentos foram inseridas nos campos correspondentes. "
        "Revise os textos e atribua as notas antes de gerar o relatório."
    )


# ==========================================================
# FORMULÁRIO PRINCIPAL
# ==========================================================

st.header("3. Avaliação de maturidade")

st.info(
    "Preencha as notas de cada dimensão. O relatório só será gerado quando todas as dimensões "
    "tiverem índice definido. Isso evita que o sistema atribua automaticamente 1,5 para tudo."
)

tabs = st.tabs([
    "Camada 1: Gestão de Pós-Venda",
    "Camada 2: Feedback Qualificado",
])

with tabs[0]:
    st.subheader("Camada 1 — Gestão de Pós-Venda para Serviços de Saúde")

    for dimension_key in DIMENSIONS_C1:
        render_dimension_form(dimension_key)

with tabs[1]:
    st.subheader("Camada 2 — Protocolo de Feedback Qualificado")

    for dimension_key in DIMENSIONS_C2:
        render_dimension_form(dimension_key)


# ==========================================================
# GERAÇÃO DO RELATÓRIO
# ==========================================================

st.markdown("---")
render_dashboard()

st.divider()

missing_scores = get_missing_scores()

if missing_scores:
    st.warning(
        f"Ainda há {len(missing_scores)} dimensão(ões) sem nota. "
        "Todas precisam ser avaliadas antes da geração do relatório."
    )

    with st.expander("Ver dimensões sem nota", expanded=False):
        for missing in missing_scores:
            st.write(f"- {missing}")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    generate_clicked = st.button(
        "Gerar relatório de intervenção",
        type="primary",
        use_container_width=True,
        disabled=bool(missing_scores),
    )

if generate_clicked:
    layer1 = build_dimension_data(DIMENSIONS_C1)
    layer2 = build_dimension_data(DIMENSIONS_C2)

    client_data = {
        "client_name": client_name,
        "client_id": client_id,
        "unit": unit,
        "period": period.strftime("%m/%Y"),
        "responsible": responsible,
        "services": services,
    }

    try:
        with st.spinner("Processando diagnóstico e gerando arquivos..."):
            results = process_assessment(layer1, layer2)
            report_path = generate_report(client_data, results)
            excel_stream = generate_excel_report(client_data, results)

        st.session_state.last_report_path = report_path
        st.session_state.last_excel_bytes = excel_stream.getvalue()
    

        st.success("Relatório Word e Excel analítico gerados com sucesso.")

    except Exception as error:
        st.error(f"Erro ao gerar arquivos: {error}")

if st.session_state.last_report_path or st.session_state.last_excel_bytes:
    st.markdown("### Arquivos gerados")

    download_col1, download_col2 = st.columns(2)

    with download_col1:
        if st.session_state.last_report_path:
            report_path = st.session_state.last_report_path

            if os.path.exists(report_path):
                with open(report_path, "rb") as file:
                    st.download_button(
                        label="Baixar relatório DOCX",
                        data=file,
                        file_name=os.path.basename(report_path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
            else:
                st.warning(
                    "O relatório foi gerado, mas o arquivo não foi localizado no diretório esperado."
                )

    with download_col2:
        if st.session_state.last_excel_bytes:
            st.download_button(
                label="Baixar Excel analítico",
                data=st.session_state.last_excel_bytes,
                file_name="Workbook_Analitico_AVALIA.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )