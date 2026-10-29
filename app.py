from datetime import date, datetime
from io import StringIO
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = "financeiro.db"
CATEGORIAS = {
    "Receita": ["Vendas", "Serviços", "Salário", "Investimentos", "Outras receitas"],
    "Despesa": ["Aluguel", "Folha de pagamento", "Fornecedores", "Impostos", "Marketing",
                "Transporte", "Software", "Energia e água", "Alimentação", "Outras despesas"],
}

st.set_page_config(page_title="Controle Financeiro Inteligente", page_icon="📊", layout="wide")


def conectar():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('Receita', 'Despesa')),
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL CHECK(valor > 0),
            forma_pagamento TEXT NOT NULL DEFAULT 'Não informado'
        )
    """)
    conn.commit()
    return conn


def carregar_dados(conn):
    df = pd.read_sql_query("SELECT * FROM lancamentos ORDER BY data DESC, id DESC", conn)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df["mes"] = df["data"].dt.to_period("M").astype(str)
    return df


def brl(valor):
    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def inserir_lancamento(conn, data_lanc, tipo, categoria, descricao, valor, forma):
    conn.execute(
        "INSERT INTO lancamentos (data, tipo, categoria, descricao, valor, forma_pagamento) VALUES (?, ?, ?, ?, ?, ?)",
        (data_lanc.isoformat(), tipo, categoria, descricao.strip(), float(valor), forma)
    )
    conn.commit()


def carregar_exemplos(conn):
    existente = conn.execute("SELECT COUNT(*) FROM lancamentos").fetchone()[0]
    if existente:
        return False
    exemplos = [
        ("2026-10-02", "Receita", "Vendas", "Venda de produtos", 12500.00, "Pix"),
        ("2026-10-05", "Receita", "Serviços", "Serviços prestados", 3200.00, "Transferência"),
        ("2026-10-06", "Despesa", "Fornecedores", "Compra de mercadorias", 4800.00, "Boleto"),
        ("2026-10-08", "Despesa", "Aluguel", "Aluguel do escritório", 1800.00, "Transferência"),
        ("2026-10-10", "Despesa", "Marketing", "Campanha digital", 650.00, "Cartão"),
        ("2026-10-14", "Receita", "Vendas", "Venda de produtos", 7900.00, "Pix"),
        ("2026-10-16", "Despesa", "Impostos", "Impostos simulados", 970.00, "Boleto"),
        ("2026-10-18", "Despesa", "Software", "Licenças de software", 290.00, "Cartão"),
        ("2026-10-21", "Receita", "Serviços", "Consultoria", 2100.00, "Transferência"),
    ]
    conn.executemany(
        "INSERT INTO lancamentos (data, tipo, categoria, descricao, valor, forma_pagamento) VALUES (?, ?, ?, ?, ?, ?)",
        exemplos
    )
    conn.commit()
    return True


conn = conectar()

with st.sidebar:
    st.title("📊 Controle Financeiro")
    st.caption("Projeto de portfólio • ADS + Contabilidade")
    pagina = st.radio("Navegação", ["Visão geral", "Lançamentos", "Relatórios", "Sobre o projeto"])
    st.divider()
    st.subheader("Dados de demonstração")
    if st.button("Carregar exemplos", use_container_width=True):
        if carregar_exemplos(conn):
            st.success("Lançamentos fictícios adicionados.")
        else:
            st.info("A base já contém dados. Para evitar duplicação, os exemplos não foram adicionados.")
        st.rerun()
    st.caption("Os dados ficam salvos localmente em financeiro.db.")

df = carregar_dados(conn)

if pagina == "Visão geral":
    st.title("Visão geral financeira")
    st.write("Acompanhe receitas, despesas e resultado do período selecionado.")

    if df.empty:
        st.info("Ainda não há lançamentos. Acesse **Lançamentos** para cadastrar dados ou use **Carregar exemplos** na barra lateral.")
        st.stop()

    min_data = df["data"].min().date()
    max_data = df["data"].max().date()
    c1, c2 = st.columns(2)
    inicio = c1.date_input("Data inicial", value=min_data, key="overview_start")
    fim = c2.date_input("Data final", value=max_data, key="overview_end")
    if inicio > fim:
        st.error("A data inicial deve ser anterior à data final.")
        st.stop()

    periodo = df[(df["data"].dt.date >= inicio) & (df["data"].dt.date <= fim)].copy()
    receitas = periodo.loc[periodo["tipo"] == "Receita", "valor"].sum()
    despesas = periodo.loc[periodo["tipo"] == "Despesa", "valor"].sum()
    resultado = receitas - despesas
    margem = (resultado / receitas * 100) if receitas else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Receitas", brl(receitas))
    k2.metric("Despesas", brl(despesas))
    k3.metric("Resultado do período", brl(resultado), delta=f"{margem:.1f}% de margem")
    k4.metric("Lançamentos", f"{len(periodo)}")

    if periodo.empty:
        st.warning("Não existem lançamentos nesse intervalo.")
        st.stop()

    left, right = st.columns(2)
    with left:
        st.subheader("Receitas x despesas por mês")
        mensal = periodo.assign(mes=periodo["data"].dt.to_period("M").astype(str)).pivot_table(
            index="mes", columns="tipo", values="valor", aggfunc="sum", fill_value=0
        ).reset_index()
        for col in ["Receita", "Despesa"]:
            if col not in mensal.columns:
                mensal[col] = 0
        long_mensal = mensal.melt(id_vars="mes", value_vars=["Receita", "Despesa"],
                                  var_name="Tipo", value_name="Valor")
        fig = px.bar(long_mensal, x="mes", y="Valor", color="Tipo", barmode="group",
                     labels={"mes": "Mês", "Valor": "Valor (R$)", "Tipo": "Movimentação"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Despesas por categoria")
        gastos = periodo[periodo["tipo"] == "Despesa"].groupby("categoria", as_index=False)["valor"].sum()
        if gastos.empty:
            st.info("Não há despesas no período.")
        else:
            fig = px.pie(gastos, names="categoria", values="valor", hole=0.45,
                         labels={"categoria": "Categoria", "valor": "Valor (R$)"})
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Movimentações recentes")
    recentes = periodo.sort_values(["data", "id"], ascending=False).head(8)
    recentes = recentes[["data", "tipo", "categoria", "descricao", "valor", "forma_pagamento"]].copy()
    recentes["data"] = recentes["data"].dt.strftime("%d/%m/%Y")
    recentes["valor"] = recentes["valor"].map(brl)
    st.dataframe(recentes, use_container_width=True, hide_index=True)

elif pagina == "Lançamentos":
    st.title("Lançamentos financeiros")
    st.write("Cadastre receitas e despesas. Use valores positivos; o tipo define como entram no resultado.")
    with st.form("novo_lancamento", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        data_lanc = col1.date_input("Data", value=date.today())
        tipo = col2.selectbox("Tipo", ["Receita", "Despesa"])
        categoria = col3.selectbox("Categoria", CATEGORIAS[tipo])
        descricao = st.text_input("Descrição", placeholder="Ex.: venda de mercadorias")
        col4, col5 = st.columns(2)
        valor = col4.number_input("Valor (R$)", min_value=0.01, value=100.00, step=10.0, format="%.2f")
        forma = col5.selectbox("Forma de pagamento", ["Pix", "Dinheiro", "Cartão", "Boleto", "Transferência", "Débito automático", "Não informado"])
        enviado = st.form_submit_button("Salvar lançamento", type="primary")
        if enviado:
            if not descricao.strip():
                st.error("Informe uma descrição.")
            else:
                inserir_lancamento(conn, data_lanc, tipo, categoria, descricao, valor, forma)
                st.success("Lançamento salvo com sucesso.")
                st.rerun()

    st.divider()
    st.subheader("Lançamentos cadastrados")
    df = carregar_dados(conn)
    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
    else:
        f1, f2 = st.columns(2)
        filtro_tipo = f1.selectbox("Filtrar por tipo", ["Todos", "Receita", "Despesa"])
        categorias_existentes = ["Todas"] + sorted(df["categoria"].dropna().unique().tolist())
        filtro_categoria = f2.selectbox("Filtrar por categoria", categorias_existentes)
        vis = df.copy()
        if filtro_tipo != "Todos":
            vis = vis[vis["tipo"] == filtro_tipo]
        if filtro_categoria != "Todas":
            vis = vis[vis["categoria"] == filtro_categoria]
        tabela = vis[["id", "data", "tipo", "categoria", "descricao", "valor", "forma_pagamento"]].copy()
        tabela["data"] = tabela["data"].dt.strftime("%d/%m/%Y")
        tabela["valor"] = tabela["valor"].map(brl)
        st.dataframe(tabela, use_container_width=True, hide_index=True)
        with st.expander("Excluir lançamento"):
            ids = vis["id"].tolist()
            if ids:
                selecionado = st.selectbox("Escolha o ID", ids)
                confirmar = st.checkbox("Confirmo que desejo excluir este lançamento.")
                if st.button("Excluir selecionado", disabled=not confirmar):
                    conn.execute("DELETE FROM lancamentos WHERE id = ?", (int(selecionado),))
                    conn.commit()
                    st.success(f"Lançamento {selecionado} excluído.")
                    st.rerun()

elif pagina == "Relatórios":
    st.title("Relatórios financeiros")
    st.write("Filtre os dados e exporte um arquivo CSV para análise em Excel ou outra ferramenta.")
    df = carregar_dados(conn)
    if df.empty:
        st.info("Cadastre lançamentos ou carregue os dados de demonstração para gerar relatórios.")
        st.stop()

    min_data = df["data"].min().date()
    max_data = df["data"].max().date()
    c1, c2, c3 = st.columns(3)
    inicio = c1.date_input("Data inicial", value=min_data, key="report_start")
    fim = c2.date_input("Data final", value=max_data, key="report_end")
    tipo_rel = c3.selectbox("Tipo de movimentação", ["Todos", "Receita", "Despesa"])
    if inicio > fim:
        st.error("A data inicial deve ser anterior à data final.")
        st.stop()
    rel = df[(df["data"].dt.date >= inicio) & (df["data"].dt.date <= fim)].copy()
    if tipo_rel != "Todos":
        rel = rel[rel["tipo"] == tipo_rel]

    total_receitas = rel.loc[rel["tipo"] == "Receita", "valor"].sum()
    total_despesas = rel.loc[rel["tipo"] == "Despesa", "valor"].sum()
    r1, r2, r3 = st.columns(3)
    r1.metric("Total de receitas", brl(total_receitas))
    r2.metric("Total de despesas", brl(total_despesas))
    r3.metric("Saldo (receitas - despesas)", brl(total_receitas - total_despesas))

    st.subheader("Resumo por categoria")
    resumo = rel.groupby(["tipo", "categoria"], as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    if resumo.empty:
        st.info("Nenhum registro encontrado para os filtros.")
    else:
        resumo["valor_formatado"] = resumo["valor"].map(brl)
        st.dataframe(resumo[["tipo", "categoria", "valor_formatado"]].rename(columns={"valor_formatado": "Total"}),
                     use_container_width=True, hide_index=True)

    exportar = rel[["id", "data", "tipo", "categoria", "descricao", "valor", "forma_pagamento"]].copy()
    exportar["data"] = exportar["data"].dt.strftime("%Y-%m-%d")
    csv = exportar.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    st.download_button("⬇️ Baixar relatório CSV", data=csv, file_name="relatorio_financeiro.csv",
                       mime="text/csv", use_container_width=True)
    st.caption("Observação: este relatório é gerencial e educacional; não substitui escrituração contábil, apuração fiscal ou orientação profissional.")

else:
    st.title("Sobre o projeto")
    st.markdown("""
    ### Controle Financeiro Inteligente

    Aplicação de portfólio que conecta **Análise e Desenvolvimento de Sistemas** com **conceitos de Contabilidade e gestão financeira**.

    **Funcionalidades**
    - Cadastro e exclusão de receitas e despesas.
    - Persistência local com SQLite.
    - Indicadores de receitas, despesas, resultado e margem.
    - Gráficos mensais e despesas por categoria.
    - Filtros por período, tipo e categoria.
    - Exportação de relatórios em CSV.

    **Tecnologias**
    - Python
    - Streamlit
    - SQLite
    - Pandas
    - Plotly

    **Conceitos demonstrados**
    - CRUD (criar, consultar e excluir lançamentos).
    - Consultas SQL com parâmetros.
    - Tratamento e agregação de dados.
    - Indicadores financeiros básicos.
    - Visualização de dados e exportação.

    **Limitações**
    Este é um protótipo educacional. Não implementa login, controle de acesso, backup automático, integração bancária ou regras fiscais oficiais. Os dados ficam em um arquivo local `financeiro.db`.
    """)

st.sidebar.divider()
st.sidebar.caption("Projeto educacional • Não substitui sistema contábil profissional.")
