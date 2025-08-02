
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from scraper import scraper_function
import datetime
from datetime import datetime, timedelta


# Função para ler todos os produtos do arquivo JSONL e montar DataFrame
NOTAS_PATH = os.path.join('dados', 'notas.txt')
def read_notas_to_df():
    if not os.path.exists(NOTAS_PATH):
        return pd.DataFrame([])
    with open(NOTAS_PATH, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f if line.strip()]
    df = pd.DataFrame(data)
    df.rename(columns={'produto': 'produto', 'data_hora':'data', 'forma_de_pagamento':'forma_pagamento'}, inplace=True)
    return df

df = read_notas_to_df()

if not df.empty and 'forma_pagamento' in df.columns:
    df.loc[df['forma_pagamento'] == '', 'forma_pagamento'] = 'Outros'

def by_periodo(df, periodo_start, periodo_end):
    filtered_df = df[(df['data'] >= periodo_start) & (df['data'] <= periodo_end)]
    return filtered_df

def by_produto(df, produto):
    filtered_df = df[df['produto'] == produto]
    return filtered_df

def by_forma_pagamento(df, forma_pagamento):
    filtered_df = df[df['forma_pagamento'] == forma_pagamento]
    return filtered_df


st.title("Análise de Compras")
st.write("Disciplina de Extração Automática de Dados - Marcu Loreto, Rafael Fideles, Ricardo Kerr, Ujeverson Tavares")
# Função para ler os IDs do CSV
import csv
import re

def ler_ids_csv(path_csv='dados/ids_extraidos.csv'):
    if not os.path.exists(path_csv):
        return []
    with open(path_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row['id'] for row in reader if 'id' in row]

ids_csv = ler_ids_csv()

# --- Campo para inserir link de nota fiscal e botão para extrair e salvar ID ---
st.sidebar.title("Extrair ID de Nota Fiscal")
link_nf = st.sidebar.text_input("Cole o link da nota fiscal:", "")
if st.sidebar.button("Extrair e Salvar ID"):
    # Regex igual ao extrator_wpp.py
    link_pattern = re.compile(r'https?://nfe\.sefaz\.go\.gov\.br/nfeweb/sites/nfce/(?:d/)?danfeNFCe\?p=([0-9]+)')
    match = link_pattern.search(link_nf)
    if match:
        nota_id = match.group(1)
        # Salvar no CSV, sem sobrescrever
        path_csv = 'dados/ids_extraidos.csv'
        # Carrega todos os IDs existentes de forma robusta
        ids_existentes = set()
        if os.path.exists(path_csv):
            with open(path_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                ids_existentes = set(row['id'] for row in reader if 'id' in row)
        if nota_id not in ids_existentes:
            # Adiciona cabeçalho se arquivo novo
            write_header = not os.path.exists(path_csv) or os.stat(path_csv).st_size == 0
            with open(path_csv, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['id'])
                if write_header:
                    writer.writeheader()
                writer.writerow({'id': nota_id})
            st.sidebar.success(f"ID extraído e salvo: {nota_id}")
        else:
            st.sidebar.info(f"ID já existe no arquivo: {nota_id}")
    else:
        st.sidebar.error("Link inválido ou não reconhecido.")

st.sidebar.title("Adicionar Nota")
st.sidebar.write("Adicione uma nova nota de compra")

# Estado para indexação automática dos IDs
if 'auto_id_index' not in st.session_state:
    st.session_state.auto_id_index = 0

# Botão para inserir automaticamente o próximo ID
if st.sidebar.button("Inserir próximo ID do CSV"):
    if ids_csv and st.session_state.auto_id_index < len(ids_csv):
        st.session_state['produto_auto'] = ids_csv[st.session_state.auto_id_index]
        st.session_state.auto_id_index += 1
    else:
        st.sidebar.warning("Todos os IDs do CSV já foram utilizados.")

# Campo de texto que pode ser preenchido manualmente ou pelo botão automático
produto = st.sidebar.text_input(
    "Código da Nota Fiscal:",
    value=st.session_state.get('produto_auto', "")
)

if st.sidebar.button("Adicionar Nota"):
    if produto:
        produtos = scraper_function(produto)
        if produtos == None:
            st.sidebar.error("Nota já adicionada.")
        elif produtos == []:
            st.sidebar.error("Não foi possível adicionar produtos.")
        else:
            # Adiciona ao arquivo .txt (já feito pelo scraper_function), apenas recarrega o DataFrame
            df = read_notas_to_df()
            st.sidebar.success(f"Nota '{produto}' adicionada com sucesso!")
            # Limpa o campo automático após adicionar
            if 'produto_auto' in st.session_state:
                del st.session_state['produto_auto']
    else:
        st.sidebar.error("Por favor, insira uma chave para adicionar a nota.")

# --- Botão para inserir e processar todos os IDs do CSV ---
if st.sidebar.button("Adicionar TODOS os ids do arquivo"):
    if ids_csv:
        total = len(ids_csv)
        adicionadas = 0
        ja_processadas = 0
        erros = 0
        for id_ in ids_csv:
            produtos = scraper_function(id_)
            if produtos is None:
                ja_processadas += 1
            elif produtos == []:
                erros += 1
            else:
                adicionadas += 1
        df = read_notas_to_df()
        msg = f"Processamento concluído: {adicionadas} adicionadas, {ja_processadas} já processadas, {erros} com erro."
        st.sidebar.success(msg)
    else:
        st.sidebar.warning("Nenhum ID encontrado no arquivo CSV.")

# Filtro de produto na sidebar
st.sidebar.title("Filtrar Produtos")
produto_busca = st.sidebar.text_input("Buscar produto pelo produto (contém):")
if produto_busca:
    df = df[df['produto'].str.contains(produto_busca, case=False, na=False)]

# Certifique-se de que a coluna de data está no formato correto
if not df.empty and 'data' in df.columns:
    df['data'] = pd.to_datetime(df['data'], errors='coerce')

if df.empty or 'data' not in df.columns:
    st.warning("Nenhum dado encontrado. Verifique a conexão com o arquivo de dados ou filtros aplicados.")
else:
    # Filtro de data na sidebar
    st.sidebar.title("Filtrar por Data")

    # Definir limites com base nos dados reais
    data_min = df['data'].min().date()
    data_max = df['data'].max().date()

    periodo_start = st.sidebar.date_input("Data Inicial", value=data_min, min_value=data_min, max_value=data_max)
    periodo_end = st.sidebar.date_input("Data Final", value=data_max, min_value=data_min, max_value=data_max)

    if periodo_start > periodo_end:
        st.sidebar.error("A data inicial não pode ser maior que a data final.")
    else:
        # Converter para datetime completo para o filtro funcionar corretamente
        periodo_start = pd.to_datetime(periodo_start)
        periodo_end = pd.to_datetime(periodo_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        df = by_periodo(df, periodo_start, periodo_end)


if df.empty or 'data' not in df.columns:
    st.warning("Nenhum dado encontrado. Verifique a conexão com o arquivo de dados.")
else:
        # Gráfico de Produtos mais comprados
    st.subheader("Produtos mais comprados")

    produtos_mais_comprados = df['produto'].value_counts().head(15).reset_index()
    produtos_mais_comprados.columns = ['Produto', 'Quantidade']

    fig = px.bar(
        produtos_mais_comprados,
        x='Quantidade',
        y='Produto',
        orientation='h',
        color='Quantidade',
        color_continuous_scale='Viridis',
        labels={'Quantidade': 'Quantidade Comprada', 'Produto': 'Produto'},
        title='Top 15 Produtos Mais Comprados'
    )

    # Ordenar y pelo total
    fig.update_layout(yaxis={'categoryorder': 'total descending'})

    # Aplicar fonte Calibri negrito nos ticks e títulos dos eixos
    fig.update_layout(
        xaxis=dict(
            tickfont=dict(
                family='Calibri',
                size=12,
                color='black'
            ),
            title_font=dict(
                family='Calibri',
                size=14,
                color='black'
            )
        ),
        yaxis=dict(
            tickfont=dict(
                family='Calibri',
                size=12,
                color='black'
            ),
            title_font=dict(
                family='Calibri',
                size=14,
                color='black'
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    #Gráfico de Produtos menos comprados
    st.subheader("Produtos menos comprados")
    produtos_menos_comprados = df['produto'].value_counts().tail(15).reset_index()
    produtos_menos_comprados.columns = ['Produto', 'Quantidade']
    fig = px.bar(
        produtos_menos_comprados,
        x='Quantidade',
        y='Produto',
        orientation='h',
        color='Quantidade',
        color_continuous_scale='Viridis',
        labels={'Quantidade': 'Quantidade Comprada', 'Produto': 'Produto'},
        title='Top 15 Produtos Menos Comprados'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})

    # Aplicar fonte Calibri negrito nos ticks e títulos dos eixos
    fig.update_layout(
        xaxis=dict(
            tickfont=dict(
                family='Calibri',
                size=12,
                color='black'
            ),
            title_font=dict(
                family='Calibri',
                size=14,
                color='black'
            )
        ),
        yaxis=dict(
            tickfont=dict(
                family='Calibri',
                size=12,
                color='black'
            ),
            title_font=dict(
                family='Calibri',
                size=14,
                color='black'
            )
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de Total de compras por dia/semana/mês
    st.subheader("Total de Compras por dia/semana/mês")
    periodo = st.selectbox(
        "Selecione o período:",
        ["Dia", "Mês"]
    )
    if periodo == "Dia":
        total_compras = df.groupby(df['data'].dt.to_period('D')).agg({'total_da_venda': 'sum'}).reset_index()
    elif periodo == "Mês":
        total_compras = df.groupby(df['data'].dt.to_period('M')).agg({'total_da_venda': 'sum'}).reset_index()
    # Converter Period para string para o gráfico
    total_compras['data'] = total_compras['data'].astype(str)

    # Exibir o gráfico
    st.bar_chart(total_compras.set_index('data')['total_da_venda'])

    #Gráfico de Comparativo entre formas de pagamento
    st.subheader("Comparativo entre formas de pagamento")
    formas_pagamento = df['forma_pagamento'].value_counts()
    st.bar_chart(formas_pagamento)

    st.subheader("Valor médio por compra")
    valor_medio = df['total_da_venda'].mean()
    # Exibir texto com fonte Calibri negrito via HTML
    st.markdown(
        f"<p style='font-family:Calibri; font-weight:bold; font-size:20px;'>"
        f"Valor médio por compra: R$ {valor_medio:.2f}"
        f"</p>",
        unsafe_allow_html=True
    )


    tabela_produtos = (
        df.groupby('produto')
        .size()
        .reset_index(name='Quantidade')
        .sort_values(by='Quantidade', ascending=False)
    )

    # Exibe a tabela
    st.subheader("Todos os Produtos Vendidos (Ordenados por Quantidade)")

    st.dataframe(
        tabela_produtos.style.format({'Quantidade': '{:,}'}),
        use_container_width=True
    )
