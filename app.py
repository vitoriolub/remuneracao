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
    """
    <style>

    div[data-testid="stDataFrame"] table {
        text-align: center;
    }

    div[data-testid="stDataFrame"] th {
        text-align: center !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Remuneração Comercial")

# ==================================================
# NORMALIZAÇÃO DE COLUNAS
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
            .replace("Â", "A")
            .replace("É", "E")
            .replace("Ê", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ô", "O")
            .replace("Õ", "O")
            .replace("Ú", "U")
        )

        if "SUPERV" in nome:
            mapa[col] = "Supervisor"

        elif nome in ["VENDEDOR", "CONSULTOR"]:
            mapa[col] = "Vendedor"

        elif "TOTAL FINAL" in nome:
            mapa[col] = "TOTAL FINAL"

    return df.rename(columns=mapa)

# ==================================================
# FORMATAÇÃO BRASILEIRA
# ==================================================

def formato_brasileiro(valor):

    if pd.isna(valor):
        return ""

    if isinstance(valor, (int, float)):
        return (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    return valor

# ==================================================
# FORMATAÇÃO CONDICIONAL
# ==================================================

def colorir_percentual(valor):

    try:

        if pd.isna(valor):
            return ""

        if isinstance(valor, str):

            valor = (
                valor
                .replace("%", "")
                .replace(".", "")
                .replace(",", ".")
            )

            valor = float(valor)

        if valor <= 1.5:
            valor = valor * 100

        if valor < 80:

            return """
            background-color:#F8D7DA;
            color:black;
            font-weight:bold;
            """

        elif valor < 100:

            return """
            background-color:#FFF3CD;
            color:black;
            font-weight:bold;
            """

        else:

            return """
            background-color:#D4EDDA;
            color:black;
            font-weight:bold;
            """

    except:
        return ""

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

        st.subheader("Filtros")

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
        # ESCOLHA DE COLUNAS
        # ==========================================

        st.markdown("---")

        colunas = st.multiselect(
            "Escolha as colunas",
            df_filtrado.columns.tolist(),
            default=df_filtrado.columns.tolist()
        )

        # ==========================================
        # RENOMEAR COLUNAS
        # ==========================================

        st.subheader("Renomear Colunas")

        novos_nomes = {}

        for coluna in colunas:

            novos_nomes[coluna] = st.text_input(
                f"Nome para '{coluna}'",
                value=coluna
            )

        tabela_final = (
            df_filtrado[colunas]
            .rename(columns=novos_nomes)
        )

        # ==========================================
        # SEMÁFORO
        # ==========================================

        st.subheader("Formatação Condicional")

        colunas_percentuais = st.multiselect(
            "Selecione as colunas para aplicar o semáforo",
            tabela_final.columns.tolist()
        )

        # ==========================================
        # FORMATAÇÃO
        # ==========================================

        formatacao = {}

        for col in tabela_final.columns:

            if pd.api.types.is_numeric_dtype(
                tabela_final[col]
            ):

                formatacao[col] = formato_brasileiro

        styler = (
            tabela_final.style
            .format(formatacao)
            .set_properties(**{
                "text-align": "center"
            })
            .set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("text-align", "center"),
                        ("font-weight", "bold")
                    ]
                }
            ])
        )

        for coluna in colunas_percentuais:

            styler = styler.map(
                colorir_percentual,
                subset=[coluna]
            )

        # ==========================================
        # TABELA FINAL
        # ==========================================

        st.subheader("Tabela Personalizada")

        st.dataframe(
            styler,
            use_container_width=True
        )

        # ==========================================
        # DOWNLOAD
        # ==========================================

        csv = (
            tabela_final
            .to_csv(
                index=False,
                sep=";",
                encoding="utf-8-sig"
            )
            .encode("utf-8-sig")
        )

        st.download_button(
            "📥 Baixar Resultado",
            csv,
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
