import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configuração da página Streamlit
st.set_page_config(
    page_title="Análise ENEM (2014-2019)",
    page_icon="📊",
    layout="wide"
)

st.title("🗺️ Análise de desenpenho no ENEN")
st.markdown("Explore os dados de desempenho médio no ENEM com base na localização geográfica, densidade populacional e estrutura docente.")
st.markdown("---")

# ---------------------------------------------------------------------------------------#
#                   Funções de suporte e tratamento de dados
# ---------------------------------------------------------------------------------------#

@st.cache_data
def carregar_dados(file):
    return pd.read_csv(file)

def associateUf(df: pd.DataFrame):
    # Calcula a média da nota agrupando por UF e Ano
    return df.groupby(['SIGLA_UF', 'ANO'], as_index=False)['MEDIA_NOTAS'].mean()

def plotUfGraph(df: pd.DataFrame, uf: str):
    df_uf = df[df["SIGLA_UF"] == uf]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df_uf["ANO"], df_uf["MEDIA_NOTAS"], marker='o', color='#1f77b4', linewidth=2)
    ax.set_ylim([0, 1000])
    ax.set_title(f'{uf}: Desempenho médio no ENEM', fontsize=14)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Média das Notas")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig

def plotScatterGraph(df: pd.DataFrame, x_col: str, y_col: str, x_label: str, y_label: str, title: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df[x_col], df[y_col], alpha=0.5, color='#2ca02c')
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig

# ---------------------------------------------------------------------------------------#
#                                 Interface Streamlit
# ---------------------------------------------------------------------------------------#

#st.title("📊 Painel Interativo - Desempenho no ENEM")
#st.markdown("Análise temporal e relacional de indicadores educacionais e geográficos.")

# Sidebar - Upload do Arquivo
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Faça upload do arquivo CSV", type=["csv"])

if uploaded_file is not None:
    data = carregar_dados(uploaded_file)
    st.sidebar.success("Arquivo carregado com sucesso!")
else:
    st.info("👈 Por favor, faça o upload do seu arquivo CSV na barra lateral para começar.")
    st.stop()

# Processamento e renomeação de colunas por índice (mantendo a lógica do seu código)
try:
    medias_uf = data.iloc[:, [0, 1, 59]].copy()
    media_espaco = data.iloc[:, [0, 70, 69, 59]].copy()
    media_docentes = data.iloc[:, [0, 73, 59]].copy()

    # Ajuste de nomes de colunas
    medias_uf.columns = ['ANO', 'SIGLA_UF', 'MEDIA_NOTAS']
    media_espaco.columns = ['ANO', 'ESCOLA_KM2', 'HABITANTES_KM2', 'MEDIA_NOTAS']
    media_docentes.columns = ['ANO', 'DOCENTES_ESCOLA', 'MEDIA_NOTAS']

    # Tratamento/Ordenação dos DataFrames
    medias_uf = associateUf(medias_uf)
    media_espaco = media_espaco.sort_values(by=['ESCOLA_KM2', 'HABITANTES_KM2']).reset_index(drop=True)
    media_docentes = media_docentes.sort_values(by=['DOCENTES_ESCOLA'], ascending=True).reset_index(drop=True)

except IndexError:
    st.error("Erro no formato das colunas do arquivo CSV. Verifique se o arquivo possui as posições esperadas.")
    st.stop()

# ---------------------------------------------------------------------------------------#
#                                Exibição dos Gráficos em Abas
# ---------------------------------------------------------------------------------------#

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Desempenho por Estado (UF)", 
    "🗺️ Densidade Geográfica", 
    "👨‍🏫 Docentes por Escola",
    "📄 Dados Brutos"
])

with tab1:
    st.subheader("Desempenho Médio no ENEM por Estado ao Longo dos Anos")
    
    # Lista única de UFs para o selectbox
    lista_ufs = sorted(medias_uf['SIGLA_UF'].dropna().unique())
    uf_selecionada = st.selectbox("Selecione o Estado (UF):", options=lista_ufs, index=0 if 'BA' not in lista_ufs else lista_ufs.index('BA'))
    
    # Gera e exibe o gráfico para o estado selecionado
    fig_uf = plotUfGraph(medias_uf, uf_selecionada)
    st.pyplot(fig_uf)

with tab2:
    st.subheader("Relação entre Indicadores Geográficos/Populacionais e Notas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_area = plotScatterGraph(
            media_espaco, 
            x_col="ESCOLA_KM2", 
            y_col="MEDIA_NOTAS",
            x_label="Escolas por km²", 
            y_label="Média do ENEM",
            title="Escolas/km² vs Média no ENEM"
        )
        st.pyplot(fig_area)
        
    with col2:
        fig_hab = plotScatterGraph(
            media_espaco, 
            x_col="HABITANTES_KM2", 
            y_col="MEDIA_NOTAS",
            x_label="Habitantes por km²", 
            y_label="Média do ENEM",
            title="Habitantes/km² vs Média no ENEM"
        )
        st.pyplot(fig_hab)

with tab3:
    st.subheader("Relação entre Número de Docentes e Desempenho")
    
    fig_docentes = plotScatterGraph(
        media_docentes, 
        x_col="DOCENTES_ESCOLA", 
        y_col="MEDIA_NOTAS",
        x_label="Média de docentes por escola", 
        y_label="Média do ENEM",
        title="Docentes por Escola vs Média no ENEM"
    )
    st.pyplot(fig_docentes)

with tab4:
    st.subheader("Pré-visualização do Dataset")
    st.dataframe(data.head(100))
