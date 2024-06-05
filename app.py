import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO, BytesIO

st.set_page_config(page_title="Painel de Consultas Processuais", layout="wide")  # configuração da página
st.title("Consulta Processos")  # título da página

# Dicionário de tribunais e URLs
tribunais = {
    "Tribunal Superior do Trabalho": "https://api-publica.datajud.cnj.jus.br/api_publica_tst/_search",
    "Tribunal Superior Eleitoral": "https://api-publica.datajud.cnj.jus.br/api_publica_tse/_search",
    "Tribunal Superior de Justiça": "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search",
    "Tribunal Superior Militar": "https://api-publica.datajud.cnj.jus.br/api_publica_stm/_search",
    "Tribunal Regional Federal da 1ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf1/_search",
    "Tribunal Regional Federal da 2ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf2/_search",
    "Tribunal Regional Federal da 3ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf3/_search",
    "Tribunal Regional Federal da 4ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf4/_search",
    "Tribunal Regional Federal da 5ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf5/_search",
    "Tribunal Regional Federal da 6ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trf6/_search",
    "Tribunal de Justiça do Acre": "https://api-publica.datajud.cnj.jus.br/api_publica_tjac/_search",
    "Tribunal de Justiça de Alagoas": "https://api-publica.datajud.cnj.jus.br/api_publica_tjal/_search",
    "Tribunal de Justiça do Amazonas": "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search",
    "Tribunal de Justiça do Amapá": "https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search",
    "Tribunal de Justiça da Bahia": "https://api-publica.datajud.cnj.jus.br/api_publica_tjba/_search",
    "Tribunal de Justiça do Ceará": "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search",
    "TJ do Distrito Federal e Territórios": "https://api-publica.datajud.cnj.jus.br/api_publica_tjdft/_search",
    "Tribunal de Justiça do Espírito Santo": "https://api-publica.datajud.cnj.jus.br/api_publica_tjes/_search",
    "Tribunal de Justiça do Goiás": "https://api-publica.datajud.cnj.jus.br/api_publica_tjgo/_search",
    "Tribunal de Justiça do Maranhão": "https://api-publica.datajud.cnj.jus.br/api_publica_tjma/_search",
    "Tribunal de Justiça de Minas Gerais": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search",
    "TJ do Mato Grosso de Sul": "https://api-publica.datajud.cnj.jus.br/api_publica_tjms/_search",
    "Tribunal de Justiça do Mato Grosso": "https://api-publica.datajud.cnj.jus.br/api_publica_tjmt/_search",
    "Tribunal de Justiça do Pará": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpa/_search",
    "Tribunal de Justiça da Paraíba": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpb/_search",
    "Tribunal de Justiça de Pernambuco": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpe/_search",
    "Tribunal de Justiça do Piauí": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpi/_search",
    "Tribunal de Justiça do Paraná": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search",
    "Tribunal de Justiça do Rio de Janeiro": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrj/_search",
    "TJ do Rio Grande do Norte": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrn/_search",
    "Tribunal de Justiça de Rondônia": "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search",
    "Tribunal de Justiça de Roraima": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrr/_search",
    "Tribunal de Justiça do Rio Grande do Sul": "https://api-publica.datajud.cnj.jus.br/api_publica_tjrs/_search",
    "Tribunal de Justiça de Santa Catarina": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsc/_search",
    "Tribunal de Justiça de Sergipe": "https://api-publica.datajud.cnj.jus.br/api_publica_tjse/_search",
    "Tribunal de Justiça de São Paulo": "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search",
    "Tribunal de Justiça do Tocantins": "https://api-publica.datajud.cnj.jus.br/api_publica_tjto/_search",
    "Tribunal Regional do Trabalho da 1ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt1/_search",
    "Tribunal Regional do Trabalho da 2ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt2/_search",
    "Tribunal Regional do Trabalho da 3ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt3/_search",
    "Tribunal Regional do Trabalho da 4ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt4/_search",
    "Tribunal Regional do Trabalho da 5ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt5/_search",
    "Tribunal Regional do Trabalho da 6ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt6/_search",
    "Tribunal Regional do Trabalho da 7ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt7/_search",
    "Tribunal Regional do Trabalho da 8ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt8/_search",
    "Tribunal Regional do Trabalho da 9ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt9/_search",
    "Tribunal Regional do Trabalho da 10ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt10/_search",
    "Tribunal Regional do Trabalho da 11ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt11/_search",
    "Tribunal Regional do Trabalho da 12ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt12/_search",
    "Tribunal Regional do Trabalho da 13ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt13/_search",
    "Tribunal Regional do Trabalho da 14ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt14/_search",
    "Tribunal Regional do Trabalho da 15ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt15/_search",
    "Tribunal Regional do Trabalho da 16ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt16/_search",
    "Tribunal Regional do Trabalho da 17ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt17/_search",
    "Tribunal Regional do Trabalho da 18ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt18/_search",
    "Tribunal Regional do Trabalho da 19ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt19/_search",
    "Tribunal Regional do Trabalho da 20ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt20/_search",
    "Tribunal Regional do Trabalho da 21ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt21/_search",
    "Tribunal Regional do Trabalho da 22ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt22/_search",
    "Tribunal Regional do Trabalho da 23ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt23/_search",
    "Tribunal Regional do Trabalho da 24ª Região": "https://api-publica.datajud.cnj.jus.br/api_publica_trt24/_search"
}
chavepublica = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='

# Função para realizar a consulta processual
def consulta_processual(numero_processo):
    with open('dadosJSON', 'r') as arquivo_json:
        dados = json.load(arquivo_json)

    payload = json.dumps({
        "query": {
            "match": {
                "numeroProcesso": numero_processo
            }
        }
    })
    # Iterando sobre as URLs dos tribunais
    for tribunal, url in tribunais.items():
        headers = {
            'Authorization': f'APIKey {chavepublica}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            total_hits = data.get('hits', {}).get('total', {}).get('value', 0)  # Corrigindo aqui
            if total_hits > 0:
                return(json.dumps(data, indent=4))
                break
        else:
            return(f"Não foi possível acessar o tribunal: {tribunal}")


# Inicializar o estado da sessão para armazenar o número do processo e o arquivo
if 'process_number' not in st.session_state:
    st.session_state.process_number = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# Criar um campo para inserir um número de processo
number = st.number_input("Digite um número de processo", value=st.session_state.process_number or 0, placeholder="Nº Processo...")
if number:
    st.session_state.process_number = number
st.write("Faremos a consulta utilizando o número do processo: ", st.session_state.process_number)

# Carregar arquivo
uploaded_file = st.file_uploader("Carregue um arquivo Excel", type=["xlsx", "xls"])
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file

# Função para processar um número de processo
def processa_numero_processo(numero_processo):
    tribunal, data = consulta_processual(numero_processo)
    if data:
        return pd.json_normalize(data['hits']['hits'])
    else:
        st.write(f"Processo {numero_processo} não encontrado.")
        return pd.DataFrame()

# Processar arquivo ou número de processo
result_df = pd.DataFrame()
if st.session_state.uploaded_file is not None:
    df = pd.read_excel(st.session_state.uploaded_file)
    numeros_processos = df['NumeroProcesso'].tolist()  # Ajuste conforme o nome da coluna
    dataframes = [processa_numero_processo(num) for num in numeros_processos]
    result_df = pd.concat(dataframes, ignore_index=True)
elif st.session_state.process_number:
    result_df = processa_numero_processo(st.session_state.process_number)

if not result_df.empty:
    st.write(result_df)

    # Botão para download
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(result_df)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='consulta_processos.csv',
        mime='text/csv',
    )

    
