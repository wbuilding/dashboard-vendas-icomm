import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# CONFIGURAÇÃO INICIAL
# ============================
st.set_page_config(page_title="Dashboard de Vendas - Base Calçados", layout="wide")

st.title("📊 Dashboard de Vendas - Base Calçados")
st.write("Envie o arquivo Excel consolidado (.xlsx)")

# Upload do arquivo
uploaded_file = st.file_uploader("Drag and drop file here", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.success("✅ Base carregada com sucesso!")

    # Padroniza os nomes das colunas
    df.columns = df.columns.str.strip().str.lower()

    # Identifica as colunas relevantes automaticamente
    colunas_possiveis = {
        "produto": [c for c in df.columns if "prod" in c],
        "marca": [c for c in df.columns if "marc" in c],
        "vendedor": [c for c in df.columns if "vend" in c],
        "total": [c for c in df.columns if "total" in c],
        "quantidade": [c for c in df.columns if "qt" in c or "quant" in c],
        "preço": [c for c in df.columns if "pre" in c or "valor" in c],
        "frete": [c for c in df.columns if "frete" in c],
        "catálogo": [c for c in df.columns if "cata" in c or "catalog" in c]
    }

    col_produto = colunas_possiveis["produto"][0]
    col_marca = colunas_possiveis["marca"][0]
    col_vendedor = colunas_possiveis["vendedor"][0]
    col_total = colunas_possiveis["total"][0]
    col_qtde = colunas_possiveis["quantidade"][0]
    col_preco = colunas_possiveis["preço"][0]

    # Conversões numéricas
    df[col_total] = pd.to_numeric(df[col_total], errors="coerce").fillna(0)
    df[col_qtde] = pd.to_numeric(df[col_qtde], errors="coerce").fillna(0)
    df[col_preco] = pd.to_numeric(df[col_preco], errors="coerce").fillna(0)

    df["ticket_medio"] = df[col_total] / df[col_qtde].replace(0, 1)

    # ============================
    # FILTROS
    # ============================
    st.sidebar.header("🔎 Filtros")

    mostrar_rasteiras = st.sidebar.checkbox("Mostrar apenas Rasteiras")
    mostrar_papetes = st.sidebar.checkbox("Mostrar apenas Papetes")

    # Novo: filtro de marca
    search_marca = st.sidebar.text_input("Pesquisar por Marca")

    df_filtrado = df.copy()

    if mostrar_rasteiras:
        df_filtrado = df_filtrado[df_filtrado[col_produto].str.contains("rasteira", case=False, na=False)]

    if mostrar_papetes:
        df_filtrado = df_filtrado[df_filtrado[col_produto].str.contains("papete", case=False, na=False)]

    if search_marca:
        df_filtrado = df_filtrado[df_filtrado[col_marca].str.contains(search_marca, case=False, na=False)]

    st.info(f"Exibindo {len(df_filtrado)} registros filtrados")

    # ============================
    # MÉTRICAS GERAIS
    # ============================
    col1, col2 = st.columns(2)
    with col1:
        total_vendido = df_filtrado[col_total].sum()
        st.metric("💰 Total Vendido", f"R$ {total_vendido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with col2:
        total_qtde = df_filtrado[col_qtde].sum()
        st.metric("📦 Quantidade Vendida", f"{int(total_qtde):,}".replace(",", "."))

    # ============================
    # GRÁFICOS
    # ============================
    st.subheader("📅 Vendas por Mês")
    if "mês" in df_filtrado.columns or "mes" in df_filtrado.columns:
        col_mes = "mês" if "mês" in df_filtrado.columns else "mes"
        vendas_mes = df_filtrado.groupby(col_mes)[col_total].sum().reset_index()
        fig_mes = px.bar(vendas_mes, x=col_mes, y=col_total, text_auto=".2s",
                         color_discrete_sequence=["#7B2CBF"])
        fig_mes.update_layout(xaxis_title="Mês", yaxis_title="Total de Vendas (R$)")
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.warning("⚠️ Coluna de mês não encontrada na base.")

    # ============================
    # GRÁFICO: VENDAS POR MARCA
    # ============================
    st.subheader("🧴 Vendas por Marca")

    top_n_marcas = st.sidebar.slider("Top N Marcas", 5, 30, 10)

    vendas_marca = (
        df_filtrado.groupby(col_marca)[col_total].sum()
        .sort_values(ascending=False)  # ordem decrescente
        .head(top_n_marcas)
        .reset_index()
    )

    fig_marca = px.bar(
        vendas_marca,
        y=col_marca,
        x=col_total,
        orientation="h",
        text_auto=".2s",
        color_discrete_sequence=["#7B2CBF"]
    )
    fig_marca.update_layout(xaxis_title="Total de Vendas (R$)", yaxis_title="Marca")
    st.plotly_chart(fig_marca, use_container_width=True)

    # ============================
    # NOVOS GRÁFICOS: FRETE E CATÁLOGO
    # ============================
    colunas_existentes = [c for c in df_filtrado.columns]

    # 🚚 Frete Grátis
    col_frete = None
    if colunas_possiveis["frete"]:
        col_frete = colunas_possiveis["frete"][0]

    if col_frete:
        vendas_frete = df_filtrado.groupby(col_frete)[col_total].sum().reset_index()
        fig_frete = px.pie(
            vendas_frete,
            names=col_frete,
            values=col_total,
            title="🚚 Vendas por Frete Grátis",
            color_discrete_sequence=["#7B2CBF", "#A5E6BA"]
        )
        fig_frete.update_layout(title_x=0.5)
        st.plotly_chart(fig_frete, use_container_width=True)

    # 🛍️ Catálogo
    col_catalogo = None
    if colunas_possiveis["catálogo"]:
        col_catalogo = colunas_possiveis["catálogo"][0]

    if col_catalogo:
        vendas_catalogo = df_filtrado.groupby(col_catalogo)[col_total].sum().reset_index()
        fig_catalogo = px.pie(
            vendas_catalogo,
            names=col_catalogo,
            values=col_total,
            title="🛍️ Vendas por Catálogo",
            color_discrete_sequence=["#A5E6BA", "#7B2CBF"]
        )
        fig_catalogo.update_layout(title_x=0.5)
        st.plotly_chart(fig_catalogo, use_container_width=True)

    # ============================
    # GRÁFICO: VENDAS POR VENDEDOR
    # ============================
    st.subheader("🧑‍💼 Vendas por Vendedor")

    top_n_vendedores = st.sidebar.slider("Top N Vendedores", 5, 30, 10)

    vendas_vendedor = (
        df_filtrado.groupby(col_vendedor)[col_total].sum()
        .sort_values(ascending=False)
        .head(top_n_vendedores)
        .reset_index()
    )

    fig_vendedor = px.bar(
        vendas_vendedor,
        y=col_vendedor,
        x=col_total,
        orientation="h",
        text_auto=".2s",
        color_discrete_sequence=["#C77DFF"]
    )
    fig_vendedor.update_layout(xaxis_title="Total de Vendas (R$)", yaxis_title="Vendedor")
    st.plotly_chart(fig_vendedor, use_container_width=True)

    # ============================
    # TABELA DE ANÚNCIOS MAIS VENDIDOS
    # ============================
    st.subheader("🏆 Anúncios mais vendidos")

    top_produtos = (
        df_filtrado.groupby([col_produto, col_marca])
        .agg({
            col_qtde: "sum",
            col_total: "sum",
            col_preco: "mean",
            "ticket_medio": "mean"
        })
        .sort_values(by=col_total, ascending=False)
        .reset_index()
    )

    # Formatação em Real
    top_produtos[col_total] = top_produtos[col_total].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    top_produtos[col_preco] = top_produtos[col_preco].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    top_produtos["ticket_medio"] = top_produtos["ticket_medio"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(top_produtos, use_container_width=True, height=600)

else:
    st.warning("Por favor, envie um arquivo Excel (.xlsx) para visualizar o dashboard.")
