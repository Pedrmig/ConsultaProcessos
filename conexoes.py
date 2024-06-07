import datetime
import os
import pyodbc
import sensiveis as senha
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import auxiliares as aux
import sys
import requests
import base64
import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import time

codentrada = 'ANSI'


class Gradus:
    def __init__(self, usuario, tipo='P'):
        self.clientid = ''
        self.accesscode = ''
        self.clientsecret = ''
        self.refreshcode = ''
        self.dataultimoacesso = None
        self.expiracao = None
        self.usuario = usuario
        self.acessoutil = ''
        self.erro = ''
        self.tipo = tipo
        self.listaconta = None
        self.listacontaOM = None
        match tipo.upper():
            case 'P':
                self.url = senha.siteproducao
            case 'H':
                self.url = senha.sitehomologacao
            case 'T':
                self.url = senha.sitetreinamento

        self.urlapi = self.url + senha.extensaoapi
        self.retornacredenciaisiniciais()
        self.defineconexao()

    def verificastatusconexao(self):
        try:
            if self.dataultimoacesso and self.expiracao:
                return time.time() - self.dataultimoacesso > self.expiracao
            else:
                resposta = 0

            return resposta

        except pyodbc.Error as e:
            self.erro = str(e)

    def defineconexao(self, forcaratualizacao=False):
        dados_json = None
        if len(self.usuario) > 0:
            if not self.verificastatusconexao() and not forcaratualizacao:
                tipochave = 'acesso'
                if self.accesscode:
                    # Dados para o corpo JSON
                    dados_json = {
                        'grantType': 'authorization_code',
                        'accessCode': self.accesscode
                    }
            else:
                tipochave = 'atualização'
                if self.refreshcode:
                    # A sessão expirou, é necessário renovar o token
                    dados_json = {
                        'grantType': 'refresh_token',
                        'refreshToken': self.refreshcode
                    }
            if dados_json is not None:
                # Passo 1: Codificar a string 'clienteid:clientsecret' em Base64
                client_credentials = f'{self.clientid}:{self.clientsecret}'
                client_credentials_base64 = base64.b64encode(client_credentials.encode()).decode()

                # Passo 2: Concatenar com o prefixo 'Basic'
                authorization_header = f'Basic {client_credentials_base64}'

                # Cabeçalho da requisição POST
                headers = {
                    'Authorization': authorization_header,
                    'Content-Type': 'application/json'
                }

                # Realize a requisição POST com o corpo JSON
                response = requests.post(self.urlapi, headers=headers, json=dados_json)

                # Verifique o status da resposta
                if response.status_code == 200:
                    print(f'Requisição de {tipochave.capitalize()} bem-sucedida!')
                    dadosconexao = response.json()
                    self.renovachaves(dadosconexao)
                    self.accesscode = dadosconexao['accessToken']
                    self.refreshcode = dadosconexao['refreshToken']
                    self.expiracao = dadosconexao['expiresIn']
                else:
                    if tipochave == 'atualização':
                        print('Erro na requisição. Código de status:', response.status_code)
                    else:
                        self.defineconexao(True)
            else:
                print(f'Falta a chave de {tipochave}!')

    def retornacredenciaisiniciais(self):
        chave = chaveacesso(self.tipo)
        self.accesscode = chave.retornachave(f'{self.usuario}-accessToken')
        self.refreshcode = chave.retornachave(f'{self.usuario}-refreshToken')
        self.expiracao = chave.retornachave(f'{self.usuario}-expiresIn')
        self.clientid = chave.retornachave(f'{self.usuario}-clientid')
        self.clientsecret = chave.retornachave(f'{self.usuario}-clientsecret')

        # chaves = self.conec.consultar(
        #     f"SELECT * FROM [Acesso API GRADUS] WHERE usuario = '{self.usuario}' AND Tipo = '{self.tipo}'")
        # if chaves is not None:
        #     chaves = chaves.iloc[0]
        #     self.clientid = chaves['clientid']
        #     self.clientsecret = chaves['clientsecret']
        # self.refreshcode = chaves['refreshcode']
        # self.accesscode = chaves['accesscode']
        # self.expiracao = chaves['timeout']

    def renovachaves(self, dadosconexao):
        chave = chaveacesso(self.tipo)
        chave.definechave(f'{self.usuario}-accessToken', dadosconexao['accessToken'])
        chave.definechave(f'{self.usuario}-refreshToken', dadosconexao['refreshToken'])
        chave.definechave(f'{self.usuario}-expiresIn', dadosconexao['expiresIn'])
        self.dataultimoacesso = time.time()
        # chave.definechave(f'{self.usuario}-clientid', self.clientid)
        # chave.definechave(f'{self.usuario}-clientsecret', self.clientsecret)

        # if dadosconexao is not None:
        #     self.conec.executarsql(f"""
        #                             UPDATE [Acesso API GRADUS]
        #                             SET accesscode = '{dadosconexao['accessToken']}',
        #                             refreshcode = '{dadosconexao['refreshToken']}',
        #                             timeout = '{dadosconexao['expiresIn']}',
        #                             dataacesso = GETDATE()
        #                             WHERE Usuario = '{self.usuario}' AND Tipo = '{self.tipo}'""")

    def multifuncoes(self, op, codop='get', *args, **kwargs):
        nome_operacao = ''
        if self.accesscode:
            operacao_link = ''
            argumentos = {}

            # Argumentos comuns
            common_args = [
                ('limit', int, 'optional'),
                ('page', int, 'optional')
            ]

            tendencia_args = common_args + [
                ('year', int, 'mandatory')
            ]

            # Argumentos específicos
            orcado_args = common_args + [
                ('treatmentMethod', ['EXPENSES', 'INCOME'], 'optional'),
                ('year', int, 'mandatory')
            ]

            realizado_args = orcado_args + [
                ('month', ['JANUARY', 'FEBRUARY',
                           'MARCH', 'APRIL',
                           'MAY', 'JUNE',
                           'JULY', 'AUGUST',
                           'SEPTEMBER', 'OCTOBER',
                           'NOVEMBER', 'DECEMBER'], 'mandatory'),
                ('includeNotOm', bool, 'optional')
            ]

            # Argumentos específicos para operações POST
            post_args_centro = [
                ('id', int, 'optional'),
                ('name', str, 'mandatory'),
                ('code', str, 'mandatory'),
                ('company', str, 'mandatory'),
                ('entity', str, 'mandatory')
            ]
            post_args_conta_contabil = [
                ('id', int, 'optional'),
                ('accountingAccount', str, 'mandatory'),
                ('accountingAccountDescription', str, 'mandatory'),
                ('account', str, 'mandatory'),
                ('classificationOne', str, 'mandatory'),
                ('classificationTwo', str, 'mandatory')
            ]
            match codop.upper():
                case 'GET':
                    operacoes_e_argumentos = [
                        (1, 'Iniciativas', '/api/gradus_api/v1/gi/initiatives', common_args),
                        (2, 'Impactos', '/api/gradus_api/v1/gi/impacts', common_args),
                        (3, 'Ações', '/api/gradus_api/v1/gi/actions', common_args),
                        (4, 'Comentários', '/api/gradus_api/v1/gi/chats', common_args),
                        (5, 'Orçado desdobrado', '/api/gradus_api/v1/om/analytic_budget_items/proposal', orcado_args),
                        (6, 'Orçado Aprovado', '/api/gradus_api/v1/om/analytic_budget_items/approved', orcado_args),
                        (7, 'Realizado', '/api/gradus_api/v1/om/analytic_actual_budgets', realizado_args),
                        (8, 'Conta OM', '/api/gradus_api/v1/accounts', common_args),
                        (9, 'Tendência', '/api/gradus_api/v1/om/tendency/client_accounts', tendencia_args),
                        (10, 'Conta', '/api/gradus_api/v1/client_accounts', common_args),
                        (11, 'Centro de Custo', '/api/gradus_api/v1/cost_centers', common_args)
                        # Adicione mais operações, nomes e argumentos conforme necessário
                    ]
                case 'POST':
                    if self.listacontaOM is None:
                        nome, contas, _ = self.multifuncoes(10, 'get', limit=5000000, page=1)
                        self.listacontaOM = contas['accountingAccount'].drop_duplicates().tolist()
                    # if self.listacontaOM is not None:
                    #     aux.valores_nao_encontrados(self.listacontaOM, 'account', itemabuscar=kwargs['account'])
                    operacoes_e_argumentos = [
                        (10, 'Conta', '/api/gradus_api/v1/client_accounts', post_args_conta_contabil),
                        (11, 'Centro de Custo', '/api/gradus_api/v1/cost_centers', post_args_centro)
                        # Adicione mais operações, nomes e argumentos conforme necessário
                    ]
            argumentos_esperados = None

            for operacao_numero, operacao_nome, operacao_link, argumentostemp in operacoes_e_argumentos:
                if isinstance(op, str):
                    for numero, nome, _, _ in operacoes_e_argumentos:
                        if nome.lower() == op.lower():
                            op = numero
                            break

                if op == operacao_numero:
                    nome_operacao = operacao_nome
                    argumentos_esperados = argumentostemp
                    print(f'Executando a operação {aux.start_bold}{operacao_nome}{aux.reset_bold}!')
                    break

            if argumentos_esperados is not None:
                for nome_parametro, tipo_esperado, valor_padrao in argumentos_esperados:
                    if nome_parametro in kwargs:
                        valor = kwargs[nome_parametro]
                    elif args:
                        valor = args[0]
                        args = args[1:]
                    else:
                        if valor_padrao == 'mandatory':
                            raise ValueError(
                                f"Para a operação {op}, é necessário fornecer o argumento '{nome_parametro}'.")
                        elif valor_padrao == 'optional':
                            continue  # Pula para o próximo parâmetro se for opcional e não fornecido
                        else:
                            valor = valor_padrao  # Preencher com valor padrão se fornecido

                    # Validação para tipos básicos (não lista)
                    if isinstance(tipo_esperado, type):
                        # Permite que o valor None passe pela validação
                        if (valor is not None and not isinstance(valor, tipo_esperado)) or (
                                valor is None and valor_padrao == 'mandatory'):
                            raise TypeError(
                                f"Valor inválido para {nome_parametro}: {valor}. Tipo esperado: {tipo_esperado.__name__}")

                    # Validação de valor numa lista de valores permitidos, não sensível a maiúsculas/minúsculas
                    if isinstance(tipo_esperado, list):
                        if isinstance(valor, str):
                            # Converte tanto o valor recebido quanto os valores esperados para minúsculas antes de comparar
                            valor = valor.upper()
                            tipo_esperado = [item.upper() for item in tipo_esperado]
                        if valor not in tipo_esperado:
                            raise ValueError(
                                f"Valor inválido para {nome_parametro}: {valor}. Valores esperados: {tipo_esperado}")

                    # Se passar pelas validações, adiciona aos argumentos
                    argumentos[nome_parametro] = valor

                if len(argumentos) > 0:
                    print(f'Parâmetros Utilizados: {argumentos}')

                if len(operacao_link) > 0:
                    url = self.url + operacao_link
                    headers = {
                        'Authorization': f'Bearer {self.accesscode}'
                    }
                    match codop.upper():
                        case 'GET':
                            if len(argumentos) > 0:
                                response = requests.get(url, headers=headers, params=argumentos)
                            else:
                                response = requests.get(url, headers=headers)

                            match response.status_code:
                                case 200:
                                    iniciativas = response.json()
                                    if len(iniciativas["result"]) > 0:
                                        # Crie um DataFrame para o cabeçalho (ou os dados que não estão em "result")
                                        dfdadoscabecalho = pd.DataFrame(
                                            {k: [v] for k, v in iniciativas.items() if k != "result"})

                                        # Converta a lista de resultados em um DataFrame
                                        dfresultado = pd.DataFrame(iniciativas["result"])
                                        # Lista as colunas com lista de dicionários para quebrar em colunas
                                        colunas_a_expandir = dfresultado.columns[
                                            dfresultado.apply(lambda col: col.apply(lambda x: isinstance(x, list))).any()]
                                        while len(colunas_a_expandir) > 0:
                                            # Looping para quebrar a lista de dicionários em colunas
                                            for coluna in colunas_a_expandir:
                                                # Nova estrutura de dados para os novos campos
                                                data_for_new_columns = []
                                                # Itera sobre cada linha do DataFrame
                                                for index, row in dfresultado.iterrows():
                                                    # Cria um dicionário para os novos campos
                                                    new_columns = {}
                                                    # Itera sobre cada dicionário na lista
                                                    for d in row[coluna]:
                                                        if isinstance(d, dict):
                                                            for numitem, (key, value) in enumerate(d.items()):
                                                                if numitem == 0:
                                                                    nomecoluna = '[' + coluna + '].[' + value + ']'
                                                                else:
                                                                    if isinstance(value, list):
                                                                        # Aqui você decide como lidar com a lista
                                                                        # Por exemplo, você pode querer juntar os elementos em uma string separada por vírgulas
                                                                        # Ou pode querer pegar apenas o primeiro elemento da lista
                                                                        new_columns[nomecoluna] = '/'.join(
                                                                            map(lambda x: str(x).zfill(2) if len(
                                                                                str(x)) < 2 else str(x), value))
                                                                    else:
                                                                        new_columns[nomecoluna] = value
                                                    # Adiciona o dicionário dos novos campos à lista
                                                    data_for_new_columns.append(new_columns)

                                                # Cria um novo DataFrame com os dados da nova estrutura
                                                new_columns_df = pd.DataFrame(data_for_new_columns)
                                                dfresultado = pd.concat([dfresultado.drop(coluna, axis=1), new_columns_df],
                                                                        axis=1)

                                            # colunas_a_expandir = dfresultado.columns[dfresultado.applymap(lambda x: isinstance(x, list)).any()]
                                            colunas_a_expandir = dfresultado.columns[
                                                dfresultado.apply(
                                                    lambda col: col.apply(lambda x: isinstance(x, list))).any()]

                                        # Lista as colunas que tem dicionario direto pra quebrar em colunas
                                        # dicionarios = dfresultado.columns[dfresultado.applymap(lambda x: isinstance(x, dict)).any()]
                                        dicionarios = dfresultado.columns[
                                            dfresultado.apply(lambda col: col.apply(lambda x: isinstance(x, dict))).any()]

                                        while len(dicionarios) > 0:
                                            # Looping para quebrar as colunas de dicionários
                                            for coluna in dicionarios:
                                                # Expande cada dicionário em uma série de colunas diretamente
                                                df_dicionarios_expandidos = dfresultado[coluna].apply(pd.Series)
                                                # Criando um dicionário para mapear todos os nomes de colunas para os novos nomes com o prefixo e colchetes
                                                mapeamento_renomeacao = {subcoluna: f'[{coluna}].[{subcoluna}]' for
                                                                         subcoluna in
                                                                         df_dicionarios_expandidos.columns}

                                                # Renomeando as colunas no DataFrame
                                                df_dicionarios_expandidos.rename(columns=mapeamento_renomeacao,
                                                                                 inplace=True)

                                                # Concatena com o DataFrame original e remove a coluna com os dicionários
                                                dfresultado = pd.concat([dfresultado, df_dicionarios_expandidos],
                                                                        axis=1).drop(
                                                    coluna, axis=1)

                                            # dicionarios = dfresultado.columns[dfresultado.applymap(lambda x: isinstance(x, dict)).any()]
                                            dicionarios = dfresultado.columns[
                                                dfresultado.apply(
                                                    lambda col: col.apply(lambda x: isinstance(x, dict))).any()]

                                        # Convertendo campos que terminam em "At" (sensível a maiúsculas/minúsculas) e são numéricos de milissegundos para datas com hora
                                        for column in dfresultado.columns:
                                            if len(str(column)) > 2:
                                                if (column[-2:] == "At" or column[-4:] == "Date" or column[:4] == "date") and pd.api.types.is_numeric_dtype(dfresultado[column]):
                                                    dfresultado[column] = pd.to_datetime(dfresultado[column], unit='ms')
                                                    dfresultado[column] = dfresultado[column].apply(aux.formatar_data)

                                        dfresultado.fillna('', inplace=True)

                                        # Lista de Resultados
                                        if dfresultado is not None:
                                            # Limpar caracteres ilegais
                                            for coluna in dfresultado.columns:
                                                dfresultado[coluna] = dfresultado[coluna].apply(
                                                    lambda x: aux.remover_caracteres_ilegais(str(x)) if isinstance(x,
                                                                                                                   str) else x)

                                        # Lista de Cabeçalhos
                                        if dfdadoscabecalho is not None:
                                            # Limpar caracteres ilegais
                                            for coluna in dfdadoscabecalho.columns:
                                                dfdadoscabecalho[coluna] = dfdadoscabecalho[coluna].apply(
                                                    lambda x: aux.remover_caracteres_ilegais(str(x)) if isinstance(x,
                                                                                                                   str) else x)
                                        match op:
                                            case 8:
                                                self.listacontaOM = dfresultado['name'].drop_duplicates().tolist()

                                            case 10:
                                                self.listaconta = dfresultado[
                                                    'accountingAccount'].drop_duplicates().tolist()

                                        # Retorno da função
                                        dfresultado.columns = dfresultado.columns.str.replace('\n', ' ')
                                    else:
                                        dfresultado = None
                                        dfdadoscabecalho = None
                                    return nome_operacao, dfresultado, dfdadoscabecalho  # Retorne o DataFrame

                                case _:
                                    print('Erro na solicitação de iniciativas. Código de status:', response.status_code)
                                    return None

                        case 'POST':
                            if len(argumentos) > 0:
                                if self.listacontaOM is None:
                                    nome, contas, _ = self.multifuncoes(8, 'get', limit=5000000, page=1)
                                    self.listacontaOM = contas['name'].drop_duplicates().tolist()

                                if self.listaconta is None:
                                    nome, contas, _ = self.multifuncoes(10, 'get', limit=5000000, page=1)
                                    self.listaconta = contas['accountingAccount'].drop_duplicates().tolist()

                                response = requests.post(url, headers=headers, json=[argumentos])

                                match response.status_code:
                                    case 200:
                                        mensagem = 'Criação/alteração realizada com sucesso!'
                                        return mensagem

                                    case 400:
                                        data = json.loads(response.text)
                                        # resposta = response.text
                                        # Filtrando para obter itens únicos

                                        # Preparando conjuntos para armazenar itens únicos
                                        unique_elements = set()
                                        unique_errors = set()

                                        # Processando os "elements" e "errors" para extrair itens únicos
                                        for item in data:
                                            # Adicionando elementos únicos
                                            for value in item["element"].values():
                                                unique_elements.add(value)

                                            # Adicionando erros únicos
                                            for error in item["errors"]:
                                                unique_errors.add(error["error"])

                                        # Convertendo os conjuntos em strings formatadas para impressão
                                        unique_elements_output = "Unique Elements:\n" + "\n".join(
                                            str(e) for e in unique_elements) + "\n\n"
                                        unique_errors_output = "Unique Errors:\n" + "\n".join(
                                            str(e) for e in unique_errors)

                                        # Concatenando as strings para a saída final
                                        final_output = unique_elements_output + unique_errors_output

                                        return final_output

                                    case _:
                                        print('Erro na solicitação de iniciativas. Código de status:',
                                              response.status_code)
                                        return None

            else:
                raise ValueError(f"A operação {op} não é suportada.")


class chaveacesso:
    def __init__(self, tipoacesso='P'):
        self.refreshcode = ''
        self.acesscode = ''
        self.clientid = ''
        self.clientsecret = ''
        self.tipoacesso = tipoacesso
        keyVaultName = 'https://rg-dtan-ctro.vault.azure.net/'
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=keyVaultName, credential=credential)

    def definechave(self, nomechave, valor):
        self.client.set_secret(nomechave + '-' + self.tipoacesso, valor)

    def retornachave(self, nomechave):
        try:
            retorno = self.client.get_secret(nomechave + '-' + self.tipoacesso)
            if retorno:
                return retorno.value
        except:
            return ''
