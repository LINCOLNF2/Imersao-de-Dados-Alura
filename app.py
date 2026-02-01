import streamlit as st
import pandas as pd
import plotly.express as px

# ---Configuração da Página---
# Definindo o título e o ícone e o layout para ocupar toda a largura da página
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)
# ---Carregamento dos Dados---
df_salarios = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
 
# --Barra Lateral---
st.sidebar.header("🔍 Filtros")

# Filtro do Ano
anos_disponiveis = sorted(df_salarios["ano"].unique()) #Sorted para ordenar os anos e unique para trazer apenas valores únicos
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis) #Default para selecionar todos os anos inicialmente

# Filtro Senioridade
senioridades_disponiveis = sorted(df_salarios["senioridade"].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por tipo de contrato
contratos_disponiveis = sorted(df_salarios["contrato"].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro Tamanho da Empresa
tamanhos_disponiveis = sorted (df_salarios["tamanho_empresa"].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --Filtragem do DataFrame---
# O DataFram é filtrado com base na seleção dos usuário na barra latreral
df_salarios_filtrado = df_salarios[
    (df_salarios["ano"].isin(anos_selecionados)) & # .isin verifica se o valor está dentro da lista selecionada
    (df_salarios["senioridade"].isin(senioridades_selecionadas)) &
    (df_salarios["contrato"].isin(contratos_selecionados)) &
    (df_salarios["tamanho_empresa"].isin(tamanhos_selecionados))
]

# ---Título do Dashboard---
st.title("📊 Dashboard de Analise de Salários na Área de Dados")
st.markdown("Análise interativa dos salários na área de dados no últimos anos. Ultilize os filtros à esqueda para refinar a visualização.")

# Métricas Principais (KPI's)
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_salarios_filtrado.empty: # Verifica se o DataFrame filtrado não está vazio
    salario_medio = df_salarios_filtrado['usd'].mean() #Cálculo do salário médio usando mean()
    salario_maximo = df_salarios_filtrado['usd'].max() #Cálculo do salário máximo usando max()
    total_registros = df_salarios_filtrado.shape[0] #Número total de registros no DataFrame filtrado usando shape[0]
    cargo_mais_frequente = df_salarios_filtrado['cargo'].mode()[0] #Cálculo do cargo mais frequente usando mode()
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, "N/A"

col1, col2, col3, col4, = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}") #metric é usado para mostrar métricas principais
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}") #:,.0f formata o número com vírgulas como separadores de milhar e sem casas decimais
col3.metric("Total de Registros", f"{total_registros}")
col4.metric("Cargo Mais Frequente", f"{cargo_mais_frequente}")

st.markdown("---") #Linha divisória

# Análise Visual com plotly
st.subheader("Gráficos") #Subtítulo para a seção de gráficos

col1, col2 = st.columns(2) #Duas colunas para os gráficos
with col1: #with é usado para agrupar elementos dentro da coluna
    if not df_salarios_filtrado.empty: # Verifica se o DataFrame filtrado não está vazio
        top_cargos = df_salarios_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index() #Agrupa por cargo, calcula a média salarial, seleciona os 10 maiores e ordena
        grafico_cargos = px.bar(
           top_cargos, # DataFrame com os dados
           x='usd', # Eixo X representa o salário médio
           y='cargo', # Eixo Y representa os cargos
           orientation='h', # Gráfico horizontal
           title="Top 10 Cargos com Maior Salário Médio", # Título do gráfico
           labels={'usd': 'Média Salárial anual (USD)', 'cargo': ''} # Rótulos dos eixos
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}) # Centraliza o título do gráfico
        st.plotly_chart(grafico_cargos, use_container_width=True) # Exibe o gráfico com largura ajustada ao contêiner
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.") # Mensagem de aviso se não houver dados
with col2:
    if not df_salarios_filtrado.empty:
        grafico_histograma = px.histogram( 
            df_salarios_filtrado, 
            x='usd', # Eixo X representa os salários
            nbins=30, # Número de bins no histograma
            title="Distribuição dos Salários Anuais", # Título do gráfico
            labels={'usd': 'Salário Anual (USD)', 'cont': ''} # Rótulos dos eixos
        )
        grafico_histograma.update_layout(title_x=0.1) # Centraliza o título do gráfico
        st.plotly_chart(grafico_histograma, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

col3, col4 = st.columns(2)
with col3:
    if not df_salarios_filtrado.empty:
        remoto_contagem = df_salarios_filtrado['remoto'].value_counts().reset_index() #Conta a quantidade de cada categoria em 'remoto'
        remoto_contagem.columns = ['Tipos de Trabalho', 'Quantidade'] #Renomeia as colunas para melhor clareza
        grafico_remoto = px.pie( #Gráfico de pizza
            remoto_contagem, 
            names='Tipos de Trabalho', # Nomes para o gráfico
            values='Quantidade', # Valores para o gráfico
            title="Proporção dos Tipos de Trabalho", # Título do gráfico
           hole=0.5 # Cria um gráfico de pizza com buraco no meio (doughnut)
        )
        grafico_remoto.update_traces(textinfo='percent+label') # Exibe percentual e rótulo nas fatias do gráfico
        grafico_remoto.update_layout(title_x=0.1) # Centraliza o título do gráfico
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col4:
    if not df_salarios_filtrado.empty:
        df_ds = df_salarios_filtrado[df_salarios_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientistas de Dados por país',
            labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# Tabela de Dados Detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_salarios_filtrado)