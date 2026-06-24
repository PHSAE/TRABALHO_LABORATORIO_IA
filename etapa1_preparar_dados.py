"""
=============================================================================
 ETAPA 1 — Preparação dos dados das escolas
=============================================================================
 Este script:
 1. Lê o arquivo tx_rend_escolas_2024.xlsx baixado do INEP
 2. Identifica corretamente o cabeçalho (linha 8, índice 7 em Python)
 3. Filtra apenas escolas PÚBLICAS com Ensino Médio (dado válido em 3_CAT_MED)
 4. Salva um CSV enxuto pronto para uso na Etapa 2
=============================================================================
"""

import pandas as pd

ARQUIVO_ENTRADA = 'tx_rend_escolas_2024.xlsx'
ARQUIVO_SAIDA = 'escolas_em_publicas_2024.csv'


def main():
    print(f'[1/4] Lendo {ARQUIVO_ENTRADA}...')

    # header=7 -> linha 8 do Excel (0-indexed). pandas ignora as 7 linhas anteriores.
    df = pd.read_excel(
        ARQUIVO_ENTRADA,
        header=8,      # linha 9 do Excel é o cabeçalho real (com NU_ANO_CENSO, etc.)
        engine='openpyxl',
    )
    print(f'   Total de linhas lidas: {len(df):,}')
    print(f'   Total de colunas: {len(df.columns)}')

    # Algumas linhas iniciais ainda podem ser cabeçalho residual (rótulos visuais).
    # Filtramos mantendo apenas linhas com NU_ANO_CENSO numérico válido.
    print(f'[2/4] Removendo linhas residuais de cabeçalho...')
    antes = len(df)
    df = df[pd.to_numeric(df['NU_ANO_CENSO'], errors='coerce').notna()].copy()
    df['NU_ANO_CENSO'] = df['NU_ANO_CENSO'].astype(int)
    print(f'   Removidas {antes - len(df):,} linhas residuais.')

    # Selecionamos as colunas que interessam para o estudo:
    # - Identificação: ano, região, UF, código/nome do município, código/nome da escola,
    #   localização (Urbana/Rural), dependência administrativa.
    # - Taxas do Ensino Médio total (1_CAT_MED = aprovação, 2_CAT_MED = reprovação,
    #   3_CAT_MED = abandono). Vamos usar 3_CAT_MED como variável-alvo.
    print('[3/4] Selecionando colunas relevantes e filtrando Ensino Médio público...')
    colunas_id = [
        'NU_ANO_CENSO', 'NO_REGIAO', 'SG_UF',
        'CO_MUNICIPIO', 'NO_MUNICIPIO',
        'CO_ENTIDADE', 'NO_ENTIDADE',
        'NO_CATEGORIA', 'NO_DEPENDENCIA',
    ]
    colunas_taxas = ['1_CAT_MED', '2_CAT_MED', '3_CAT_MED']
    df = df[colunas_id + colunas_taxas].copy()

    # Renomeia para nomes mais claros
    df = df.rename(columns={
        'NU_ANO_CENSO': 'ano',
        'NO_REGIAO': 'regiao',
        'SG_UF': 'uf',
        'CO_MUNICIPIO': 'cod_municipio',
        'NO_MUNICIPIO': 'nome_municipio',
        'CO_ENTIDADE': 'cod_escola',
        'NO_ENTIDADE': 'nome_escola',
        'NO_CATEGORIA': 'localizacao',
        'NO_DEPENDENCIA': 'dependencia',
        '1_CAT_MED': 'taxa_aprovacao_em',
        '2_CAT_MED': 'taxa_reprovacao_em',
        '3_CAT_MED': 'taxa_abandono_em',
    })

    # Converte taxas para numérico. Valores ausentes ou '--' viram NaN.
    for col in ['taxa_aprovacao_em', 'taxa_reprovacao_em', 'taxa_abandono_em']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtra: apenas escolas com dado válido de abandono no EM
    # (escolas sem EM aparecem com NaN nessas colunas).
    antes = len(df)
    df = df.dropna(subset=['taxa_abandono_em']).copy()
    print(f'   Escolas com EM válido: {len(df):,} (de {antes:,} totais)')

    # Filtra: apenas escolas públicas (Federal, Estadual, Municipal)
    df = df[df['dependencia'].isin(['Federal', 'Estadual', 'Municipal'])].copy()
    print(f'   Escolas públicas com EM: {len(df):,}')

    # Estatísticas rápidas
    print('\n[4/4] Estatísticas finais:')
    print(f'   Taxa média de abandono no EM público: {df["taxa_abandono_em"].mean():.2f}%')
    print(f'   Mediana: {df["taxa_abandono_em"].median():.2f}%')
    print(f'   Desvio padrão: {df["taxa_abandono_em"].std():.2f}%')
    print(f'\n   Distribuição por dependência administrativa:')
    print(df.groupby('dependencia')['taxa_abandono_em'].agg(['count', 'mean']).round(2))
    print(f'\n   Distribuição por localização:')
    print(df.groupby('localizacao')['taxa_abandono_em'].agg(['count', 'mean']).round(2))

    # Salva CSV enxuto
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding='utf-8-sig')
    print(f'\n[OK] Arquivo salvo: {ARQUIVO_SAIDA} ({len(df):,} linhas, {len(df.columns)} colunas)')


if __name__ == '__main__':
    main()