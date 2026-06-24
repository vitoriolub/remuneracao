import streamlit as st
import pandas as pd

# ==================================================
# CONFIGURAÇÃO
# ==================================================

st.set_page_config(
    page_title="Remuneração Comercial",
    layout="wide"
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("Configurações")

cor_principal = st.sidebar.color_picker(
    "Cor Principal",
    "#1E88E5"
)

arquivo = st.sidebar.file_uploader(
    "Selecione o Excel",
    type=["xlsx", "xls"]
)

# ==================================================
# CSS
# ==================================================

st.markdown(
    f"""
    <style>

    /* Cabeçalho das colunas */
    .ag-header {{
        background-color: #003366 !important;
    }}

    .ag-header-cell {{
        background-color: #003366 !important;
    }}

    .ag-header-cell-text {{
        color: white !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="titulo">Remuneração Comercial</div>',
    unsafe_allow_html=True
)

# ==================================================
# FUNÇÃO DE NORMALIZAÇÃO
# ==================================================

def normalizar_colunas(df):

    mapa = {}

    for col in df.columns:

        nome = (
            str(col)
            .strip()
            .upper()
            .replace("Ç", "C")
            .replace("Ã", "A")
            .replace("Á", "A")
        )

        if "SUPERV" in nome:
            mapa[col] = "Supervisor"

        elif nome in ["VENDEDOR", "CONSULTOR"]:
            mapa[col] = "Vendedor"

        elif "TOTAL FINAL" in nome:
            mapa[col] = "TOTAL FINAL"

    return df.rename(columns=mapa)

# ==================================================
# LEITURA
# ==================================================

if arquivo:

    try:

        df = pd.read_excel(arquivo)

        df = normalizar_colunas(df)

        st.subheader("Tabela Original")

        st.dataframe(
            df,
            use_container_width=True
        )

        # ==========================================
        # FILTROS
        # ==========================================

        st.subheader("Tabela Personalizada")

        col1, col2 = st.columns(2)

        with col1:

            if "Supervisor" in df.columns:

                supervisores = st.multiselect(
                    "Supervisor",
                    sorted(
                        df["Supervisor"]
                        .dropna()
                        .unique()
                    ),
                    default=sorted(
                        df["Supervisor"]
                        .dropna()
                        .unique()
                    )
                )

            else:
                supervisores = []

        with col2:

            if "Vendedor" in df.columns:

                vendedores = st.multiselect(
                    "Consultores",
                    sorted(
                        df["Vendedor"]
                        .dropna()
                        .unique()
                    ),
                    default=sorted(
                        df["Vendedor"]
                        .dropna()
                        .unique()
                    )
                )

            else:
                vendedores = []

        # ==========================================
        # FILTRO
        # ==========================================

        df_filtrado = df.copy()

        if supervisores:

            df_filtrado = df_filtrado[
                df_filtrado["Supervisor"]
                .isin(supervisores)
            ]

        if vendedores:

            df_filtrado = df_filtrado[
                df_filtrado["Vendedor"]
                .isin(vendedores)
            ]

        # ==========================================
        # ESCOLHER COLUNAS
        # ==========================================

        colunas = st.multiselect(
            "Escolha as colunas",
            df_filtrado.columns.tolist(),
            default=df_filtrado.columns.tolist()[:5]
        )

        # ==========================================
        # RENOMEAR COLUNAS
        # ==========================================

        st.markdown("---")
        st.subheader("Renomear Colunas")

        novos_nomes = {}

        for coluna in colunas:

            novo_nome = st.text_input(
                f"Nome para '{coluna}'",
                value=coluna
            )

            novos_nomes[coluna] = novo_nome

        tabela_final = (
            df_filtrado[colunas]
            .rename(columns=novos_nomes)
        )

        st.dataframe(
            tabela_final,
            use_container_width=True
        )

        # ==========================================
        # DOWNLOAD
        # ==========================================

        excel = tabela_final.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Baixar Resultado",
            excel,
            "resultado.csv",
            "text/csv"
        )

    except Exception as erro:

        st.error(
            f"Erro ao ler arquivo: {erro}"
        )

else:

    st.info(
        "Selecione um arquivo Excel para iniciar."
    )