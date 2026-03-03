# -*- coding: utf-8 -*-

import pandas as pd
import requests
import datetime

today = datetime.date.today()

# Configuração para exibição limpa no console
pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# 1. Configuração e Mapeamento

BCB_SERIES = {
    'INCC-M Geral': 192,
    'INCC-M Materiais': 7462,
    'INCC-M Mão de Obra': 7464,
    'INCC-M Serviços': 7463,
    'INCC-M Equipamentos': 7462
}

DE_PARA_INDICES = {
    'Concreto Armado': 'INCC-M Materiais',
    'Revestimentos': 'INCC-M Materiais',
    'Instalações Hidra/Elé': 'INCC-M Materiais',
    'Esquadrias': 'INCC-M Materiais',
    'Elevadores': 'INCC-M Equipamentos',
    'Pintura': 'INCC-M Serviços',
    'Administração': 'INCC-M Mão de Obra',
    'Segurança': 'INCC-M Mão de Obra',
}

# 2. Funções Auxiliares (API)

def get_bcb_last_factor(series_code):

    url = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados/ultimos/1?formato=json'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            indice_percentual = float(data[0]['valor'])
            data_referencia = data[0]['data']
            # Retorna o fator (ex: 1.005), a data e o valor nominal
            return 1 + (indice_percentual / 100), data_referencia, indice_percentual
    except Exception as e:
        print(f"Erro ao buscar série {series_code}: {e}")
    # Em caso de erro, retorna fator neutro (1.0)
    return 1.0, "N/A", 0.0

# 3. Função Principal de Atualização

def atualizar_orcamento(df_input):
    
    df = df_input.copy()

    # Identificar a linha de Total (Assumindo que é a última linha)
    idx_total = df.index[-1]

    # Criar colunas novas se não existirem
    if 'Custo Atualizado' not in df.columns:
        df['Custo Atualizado'] = df['Custos']

    # Cache para evitar chamadas repetidas à API
    cache_indices = {}

    print("--- ETAPA 1: Atualizando custos unitários via API ---")

    # LOOP 1: Atualiza apenas os VALORES (ignora a linha de total)
    # Iteramos até o penúltimo item (df.index[:-1])
    for i in df.index[:-1]:
        row = df.loc[i]
        servico = row['Serviço']

        # Define qual índice usar
        nome_indice = DE_PARA_INDICES.get(servico, 'INCC-M Geral')
        codigo_serie = BCB_SERIES.get(nome_indice, 192)

        # Busca na API (ou no cache)
        if nome_indice not in cache_indices:
            fator, data_ref, valor_pct = get_bcb_last_factor(codigo_serie)
            cache_indices[nome_indice] = {
                'fator': fator,
                'data': data_ref,
                'valor': valor_pct
            }
            print(f"> Atualizando {nome_indice}: {valor_pct}% (Ref: {data_ref})")

        dados = cache_indices[nome_indice]

        # Aplica o aumento
        custo_atual = row['Custos']
        custo_novo = custo_atual * dados['fator']

        # Salva na planilha
        df.at[i, 'Custo Atualizado'] = custo_novo
        df.at[i, 'Data Ref. Índice'] = dados['data']
        df.at[i, 'Índice Aplicado'] = f"{nome_indice} ({dados['valor']}%)"

    print("\n--- ETAPA 2: Recalculando o Total Global ---")

    novo_total_global = df.loc[df.index[:-1], 'Custo Atualizado'].sum()

    df.at[idx_total, 'Custo Atualizado'] = novo_total_global
    df.at[idx_total, 'Serviço'] = 'TOTAL GERAL'

    print(f"Novo Custo Total da Obra: R$ {novo_total_global:,.2f}")

    print("\n--- ETAPA 3: Recalculando Porcentagens e Acumulados ---")

    itens_mask = df.index[:-1]

    # Calcula % individual: (Item / Novo Total)
    df.loc[itens_mask, 'Nova Porcentagem'] = df.loc[itens_mask, 'Custo Atualizado'] / novo_total_global

    # Calcula Acumulado: Soma progressiva das novas porcentagens
    df.loc[itens_mask, 'Novo Acumulado'] = df.loc[itens_mask, 'Nova Porcentagem'].cumsum()

    df.at[idx_total, 'Nova Porcentagem'] = 1.0
    df.at[idx_total, 'Novo Acumulado'] = 1.0 

    return df

# 4. Execução

caminho_arquivo = '/content/Curva-ABC.xlsx'
df_orcamento = pd.read_excel(caminho_arquivo)

df_final = atualizar_orcamento(df_orcamento)

# Exibir Resultado
colunas_visualizacao = ['Serviço', 'Custos', 'Custo Atualizado', 'Nova Porcentagem', 'Novo Acumulado', 'Índice Aplicado']
print("\nTABELA FINAL ATUALIZADA:")
print(df_final[colunas_visualizacao].tail().to_string(index=False))

# Salvar
df_final.to_excel(f"Orcamento_Atualizado_{today}_INCC.xlsx", index=False)