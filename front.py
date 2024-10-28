import streamlit as st
import main as m
import database as db
import pandas as pd
import sqlite3 as sql

# estabelecendo uma conexão com o bando de dados
con = sql.connect("dados.db")
consultaSQL = "SELECT * FROM vendas"
dadosSQL = pd.read_sql_query(consultaSQL, con)

# Criando o banco de dados
db.criarBanco()

st.set_page_config(layout="wide")

st.title("🥪 Lanchonete do Amaro - Análise de Preços")
colunaE, colunaD = st.columns(2)
with colunaE:
    st.caption("Para a Lanchonete do Amaro, entender como os clientes respondem às mudanças nos preços dos salgados é essencial. Esta análise nos ajuda a encontrar o equilíbrio perfeito entre preços competitivos e lucratividade, mantendo nossos clientes satisfeitos.")

st.write("")
st.write("---")
st.write("")

with st.container():
    st.subheader("📊 Custos de Produção do Salgado:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        Custo = st.number_input("Custo dos ingredientes (por unidade): R$", min_value=1.0, step=0.01)
    with col2:
        somaDeSalarios = st.number_input("Custos com funcionários (mensal): R$", min_value=1.0, step=0.01)
    with col3:
        totalProducao = st.number_input("Produção de salgados por dia: ", min_value=1.0, step=1.0)
    with col4:
        Lucro = st.number_input("Margem de lucro desejada (%): ", min_value=0.0, max_value=100.0, step=1.0, format="%.1f")

    precoUnidade = m.preçoUnidade(Custo, somaDeSalarios, totalProducao)

    calcular_preco_final = st.button("Calcular Preço Sugerido")
    if calcular_preco_final:
        st.success(F"Preço SUGERIDO de venda: R${m.preçoFinal(precoUnidade, Lucro):.2f}")

st.write("")
st.write("")

with st.container():
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("🏷️ Definição do Preço de Venda:")
        precoFinal = st.number_input("Preço de venda do salgado: R$", min_value=1.0, step=0.01 )
    with col6:
        st.subheader("")
        VendasPorDia = st.number_input("Quantidade média de salgados vendidos por dia: ", min_value=1.0, step=1.0)
        VendasPorMesAprox = VendasPorDia * 30

    # Inserindo os dados no banco (elasticidade é None no início)
    inserir_dados = st.button("Registrar Dados")
    if inserir_dados:
        if precoUnidade is not None:
            db.inserirDados(
                data_adicionada=db.dataDado(),
                precoInicio=precoUnidade,
                precoFinal=precoFinal,
                quantidadeInicio=totalProducao,
                quantidadeFinal=VendasPorMesAprox,
                elasticidade=None
            )
            st.success("Dados inseridos com sucesso!")
        else:
            st.error("Calcule o preço sugerido antes de inserir os dados.")

st.write("")
st.write("")

dados = db.buscarUltimosDados()

with st.container():
    st.subheader("📈 Análise de Elasticidade:")
    calcular_elasticidade = st.button("Analisar Impacto")
    if calcular_elasticidade:
        if dados:
            precoInicio, precoFinal, quantidadeInicio, quantidadeFinal, _ = dados
            elasticidadePD = m.elasticidade(quantidadeInicio, quantidadeFinal, precoInicio, precoFinal)

            # Atualizando o campo 'elasticidade' no registro mais recente
            db.atualizarElasticidade(elasticidadePD)
            st.header(f"Elasticidade preço-demanda: {elasticidadePD:.2f}")
            if elasticidadePD < -1:
                st.warning("⚠️ Atenção! Seus clientes estão muito sensíveis ao preço. Um aumento pode reduzir significativamente as vendas. Considere manter os preços atuais ou fazer ajustes menores.")
            elif elasticidadePD == -1:
                st.info("📊 As vendas respondem proporcionalmente às mudanças de preço. Qualquer alteração deve ser bem planejada.")
            elif -1 < elasticidadePD < 0:
                st.success("✅ Boa notícia! Seus clientes são fiéis aos salgados. Você tem flexibilidade para ajustar os preços mantendo as vendas estáveis.")
            elif elasticidadePD == 0:
                st.info("🎯 Seus salgados têm demanda garantida! Os clientes compram independentemente do preço. Possível ajustar preços com segurança.")
            elif elasticidadePD > 0:
                st.success("🌟 Interessante! Seus salgados são vistos como produto premium. Os clientes associam maior preço com maior qualidade.")

        else:
            st.header("Nenhum dado encontrado para calcular elasticidade.")

st.write("")
st.write("")

st.subheader("📊 Desempenho do Negócio:")
st.caption("Analise as tendências por período.")
opcao = st.selectbox("Selecione o período de análise", ("Todos os registros", "Última semana", "Últimos 15 dias","Último mês", "Últimos 2 meses", "Últimos 3 meses", "Últimos 4 meses"))


if opcao == "Todos os registros":
    dados_filtrados = dadosSQL
else:
    periodo_map = {
        "Última semana": 7,
        "Últimos 15 dias": 15,
        "Último mês": 30,
        "Últimos 2 meses": 60,
        "Últimos 3 meses": 90,
        "Últimos 4 meses": 120
    }
    numDias = periodo_map[opcao]
    dados_filtrados = dadosSQL[-numDias:]

colg1, colg2 = st.columns(2)
with colg1:
    st.write("Tendência de Elasticidade:")
    st.line_chart(dados_filtrados, x="data_adicionada", y="elasticidade", x_label="Data", y_label="Elasticidade", color="#008000")

with colg2:
    st.write("Comparativo de Vendas:")
    st.bar_chart(dados_filtrados, x="data_adicionada", y=["quantidadeInicio", "quantidadeFinal"], x_label="Data", y_label="Quantidade", )


colg3, colg4 = st.columns(2)	
with colg3:
    st.write("Perfil de Sensibilidade dos Clientes:")
    # Criando um histograma simples da elasticidade
    hist_data = pd.DataFrame({
        'Elasticidade': dados_filtrados['elasticidade'].dropna()
    })
    st.bar_chart(hist_data)

with colg4:
    st.write("Evolução dos Preços:")
    st.bar_chart(dados_filtrados, x="data_adicionada", y=["precoInicio", "precoFinal"], x_label="Data", y_label="Preço", color=["#E63F1E", "#77210F"])
