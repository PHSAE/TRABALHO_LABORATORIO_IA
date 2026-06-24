"""
=============================================================================
 ETAPA 2 — Enriquecimento com infraestrutura do Censo Escolar 2024
=============================================================================
 Este script:
 1. Lê o CSV de escolas com EM público gerado na Etapa 1
 2. Lê APENAS as colunas necessárias do microdados_ed_basica_2024.csv (gigante)
 3. Cruza as duas bases pela chave CO_ENTIDADE / cod_escola
 4. Salva um CSV enriquecido pronto para a Etapa 3 (dados socioeconômicos)
=============================================================================
"""

import pandas as pd

CSV_ETAPA1 = 'escolas_em_publicas_2024.csv'
CSV_MICRODADOS = 'microdados_ed_basica_2024.csv'
CSV_SAIDA = 'escolas_enriquecido_v1.csv'

# Variáveis selecionadas dos microdados (22 + chave de junção)
COLUNAS_MICRODADOS = [
    'CO_ENTIDADE',                  # chave de junção
    # Saneamento básico (4)
    'IN_AGUA_POTAVEL',
    'IN_ESGOTO_REDE_PUBLICA',
    'IN_ENERGIA_REDE_PUBLICA',
    'IN_LIXO_SERVICO_COLETA',
    # Infraestrutura pedagógica (7)
    'IN_BIBLIOTECA',
    'IN_LABORATORIO_INFORMATICA',
    'IN_LABORATORIO_CIENCIAS',
    'IN_QUADRA_ESPORTES',
    'IN_REFEITORIO',
    'IN_AUDITORIO',
    'IN_PATIO_COBERTO',
    # Tecnologia (3)
    'IN_INTERNET',
    'IN_BANDA_LARGA',
    'IN_INTERNET_ALUNOS',
    # Acessibilidade (1)
    'IN_BANHEIRO_PNE',
    # Profissionais de suporte (3)
    'IN_PROF_BIBLIOTECARIO',
    'IN_PROF_PSICOLOGO',
    'IN_PROF_NUTRICIONISTA',
    # Porte e recursos (3)
    'QT_SALAS_UTILIZADAS',
    'QT_MAT_MED',
    'IN_COMPUTADOR',
]


def main():
    print('=' * 70)
    print(' ETAPA 2 — Enriquecimento com microdados do Censo Escolar')
    print('=' * 70)

    # 1. Lê o CSV produzido na Etapa 1
    print(f'\n[1/4] Lendo {CSV_ETAPA1}...')
    df_taxas = pd.read_csv(CSV_ETAPA1, encoding='utf-8-sig')
    print(f'   {len(df_taxas):,} escolas públicas com EM (saída da Etapa 1)')

    # 2. Lê os microdados — APENAS as colunas necessárias para economia de memória
    #    Mesmo que o CSV tenha 476 colunas e centenas de MB, lendo só 22 fica leve.
    print(f'\n[2/4] Lendo colunas selecionadas de {CSV_MICRODADOS}...')
    print(f'      ({len(COLUNAS_MICRODADOS)} colunas de {476} totais)')
    df_micro = pd.read_csv(
        CSV_MICRODADOS,
        sep=';',                # separador padrão do INEP
        encoding='latin-1',     # codificação padrão do INEP
        usecols=COLUNAS_MICRODADOS,
        low_memory=False,
    )
    print(f'   {len(df_micro):,} escolas no Censo Escolar 2024 (total Brasil)')

    # 3. Cruzamento via merge (LEFT JOIN: mantém todas escolas com EM)
    print(f'\n[3/4] Cruzando bases pela chave CO_ENTIDADE...')
    df_final = df_taxas.merge(
        df_micro,
        left_on='cod_escola',
        right_on='CO_ENTIDADE',
        how='left',
    )
    # Remove a coluna duplicada (CO_ENTIDADE virou cópia de cod_escola)
    df_final = df_final.drop(columns=['CO_ENTIDADE'])

    # Estatísticas do cruzamento
    n_match = df_final[COLUNAS_MICRODADOS[1]].notna().sum()  # usa 1ª var IN_* como proxy
    n_no_match = len(df_final) - n_match
    print(f'   Escolas com match nos microdados: {n_match:,} ({n_match/len(df_final)*100:.1f}%)')
    if n_no_match > 0:
        print(f'   Escolas SEM match: {n_no_match:,} ({n_no_match/len(df_final)*100:.1f}%)')
        print(f'   (essas serão removidas — não há infraestrutura disponível para elas)')
        df_final = df_final.dropna(subset=[COLUNAS_MICRODADOS[1]]).copy()
        print(f'   Após remoção: {len(df_final):,} escolas com dados completos')

    # 4. Estatísticas exploratórias
    print('\n[4/4] Estatísticas exploratórias do dataset enriquecido:\n')
    print(f'   Total de colunas: {len(df_final.columns)}')
    print(f'   Total de escolas: {len(df_final):,}')

    # % de escolas com cada característica binária (IN_*)
    print('\n   Presença de infraestrutura (% das escolas públicas com EM):')
    cols_in = [c for c in df_final.columns if c.startswith('IN_')]
    for col in cols_in:
        pct = df_final[col].mean() * 100
        print(f'     {col:35s}: {pct:5.1f}%')

    # Estatísticas das quantitativas
    print('\n   Variáveis quantitativas (mediana | média | máximo):')
    for col in ['QT_SALAS_UTILIZADAS', 'QT_MAT_MED']:
        if col in df_final.columns:
            med = df_final[col].median()
            avg = df_final[col].mean()
            mx = df_final[col].max()
            print(f'     {col:35s}: {med:5.0f} | {avg:6.1f} | {mx:5.0f}')

    # Salva
    df_final.to_csv(CSV_SAIDA, index=False, encoding='utf-8-sig')
    print(f'\n[OK] Arquivo salvo: {CSV_SAIDA}')
    print(f'     {len(df_final):,} escolas x {len(df_final.columns)} colunas')


if __name__ == '__main__':
    main()