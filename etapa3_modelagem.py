"""
=============================================================================
 ETAPA 3 — Modelagem: Classificação de Escolas por Risco de Abandono
=============================================================================
 Predição binária: escola de "alto abandono" (>= 5%) vs "baixo abandono" (< 5%)
 Dados: escolas_enriquecido_v1.csv (saída da Etapa 2)
 Modelos: MLP (foco) + Regressão Logística (baseline para comparação)
=============================================================================
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve,
)
from sklearn.inspection import permutation_importance


CSV_ENTRADA = 'escolas_enriquecido_v1.csv'
LIMIAR_ABANDONO = 5.0  # escolas com taxa >= 5% são "alto abandono"

# Saídas de visualização
FIG_MATRIZ_CONFUSAO = 'fig_matriz_confusao.png'
FIG_ROC = 'fig_curvas_roc.png'
FIG_IMPORTANCIA = 'fig_importancia_variaveis.png'
FIG_DISTRIBUICAO = 'fig_distribuicao_abandono.png'


# =============================================================================
# 1. CARGA E LIMPEZA
# =============================================================================

def carregar_e_limpar():
    print('=' * 70)
    print(' ETAPA 3 — MODELAGEM')
    print('=' * 70)
    print(f'\n[1/6] Carregando {CSV_ENTRADA}...')
    df = pd.read_csv(CSV_ENTRADA, encoding='utf-8-sig')
    print(f'   {len(df):,} escolas carregadas, {len(df.columns)} colunas')

    # Tratamento de outliers nas quantitativas (winsorização no percentil 99)
    print('\n[2/6] Tratamento de outliers (winsorização no p99)...')
    for col in ['QT_SALAS_UTILIZADAS', 'QT_MAT_MED']:
        p99 = df[col].quantile(0.99)
        n_outliers = (df[col] > p99).sum()
        df[col] = df[col].clip(upper=p99)
        print(f'   {col}: {n_outliers} outliers limitados ao p99 ({p99:.0f})')

    # Construção da variável-alvo binária
    df['alto_abandono'] = (df['taxa_abandono_em'] >= LIMIAR_ABANDONO).astype(int)
    print(f'\n   Variável-alvo binária criada (limiar = {LIMIAR_ABANDONO}%)')
    n_alto = df['alto_abandono'].sum()
    print(f'   Alto abandono (>= {LIMIAR_ABANDONO}%): {n_alto:,} '
          f'({n_alto/len(df)*100:.1f}%)')
    print(f'   Baixo abandono (< {LIMIAR_ABANDONO}%): {len(df)-n_alto:,} '
          f'({(len(df)-n_alto)/len(df)*100:.1f}%)')
    return df


# =============================================================================
# 2. PREPARAÇÃO DAS FEATURES
# =============================================================================

def preparar_features(df):
    print('\n[3/6] Preparando features...')

    # Features binárias (IN_*) — usadas diretamente
    features_in = [c for c in df.columns if c.startswith('IN_')]

    # Features quantitativas
    features_qt = ['QT_SALAS_UTILIZADAS', 'QT_MAT_MED']

    # Features categóricas — one-hot encoding
    features_cat = ['regiao', 'dependencia', 'localizacao']
    df_dummies = pd.get_dummies(df[features_cat], drop_first=True).astype(int)

    # Monta a matriz X
    X = pd.concat(
        [df[features_in + features_qt].reset_index(drop=True),
         df_dummies.reset_index(drop=True)],
        axis=1,
    )
    y = df['alto_abandono'].values

    # Tratamento de valores ausentes (NaN)
    n_nan = X.isna().sum().sum()
    if n_nan > 0:
        print(f'   {n_nan:,} valores ausentes encontrados — preenchendo:')
        # Binárias (IN_*): NaN → 0 (ausência do recurso)
        for col in features_in:
            if X[col].isna().any():
                n = X[col].isna().sum()
                X[col] = X[col].fillna(0)
                print(f'     {col}: {n} NaN → 0')
        # Quantitativas: NaN → mediana
        for col in features_qt:
            if X[col].isna().any():
                med = X[col].median()
                n = X[col].isna().sum()
                X[col] = X[col].fillna(med)
                print(f'     {col}: {n} NaN → mediana ({med:.0f})')

    print(f'   {X.shape[1]} features no total ({len(features_in)} binárias + '
          f'{len(features_qt)} quantitativas + {df_dummies.shape[1]} categóricas)')
    return X, y, X.columns.tolist()


# =============================================================================
# 3. TREINAMENTO E AVALIAÇÃO
# =============================================================================

def treinar_e_avaliar(X, y, nomes_features):
    print('\n[4/6] Dividindo em treino (70%) e teste (30%)...')
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    print(f'   Treino: {len(X_train):,} | Teste: {len(X_test):,}')

    # Padronização
    scaler = StandardScaler()
    X_train_norm = scaler.fit_transform(X_train)
    X_test_norm = scaler.transform(X_test)

    # ---- Modelo A: Regressão Logística (baseline) ----
    print('\n[5/6] Treinando modelos...')
    print('   Modelo A — Regressão Logística (baseline)...')
    logreg = LogisticRegression(max_iter=2000, class_weight='balanced',
                                random_state=42)
    logreg.fit(X_train_norm, y_train)
    y_pred_lr = logreg.predict(X_test_norm)
    y_prob_lr = logreg.predict_proba(X_test_norm)[:, 1]

    # ---- Modelo B: MLP (principal) ----
    print('   Modelo B — Rede Neural MLP (principal)...')
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation='relu', solver='adam',
        max_iter=500, early_stopping=True,
        random_state=42,
    )
    mlp.fit(X_train_norm, y_train)
    y_pred_mlp = mlp.predict(X_test_norm)
    y_prob_mlp = mlp.predict_proba(X_test_norm)[:, 1]

    # ---- Avaliação ----
    print('\n[6/6] Avaliação no conjunto de teste:')
    print('\n' + '─' * 70)
    print(' REGRESSÃO LOGÍSTICA (baseline)')
    print('─' * 70)
    print(f' Acurácia: {accuracy_score(y_test, y_pred_lr) * 100:.2f}%')
    print(f' AUC-ROC:  {roc_auc_score(y_test, y_prob_lr):.3f}')
    print(classification_report(y_test, y_pred_lr,
                                target_names=['Baixo', 'Alto'], digits=3))

    print('─' * 70)
    print(' MLP (modelo principal)')
    print('─' * 70)
    print(f' Acurácia: {accuracy_score(y_test, y_pred_mlp) * 100:.2f}%')
    print(f' AUC-ROC:  {roc_auc_score(y_test, y_prob_mlp):.3f}')
    print(classification_report(y_test, y_pred_mlp,
                                target_names=['Baixo', 'Alto'], digits=3))

    return {
        'X_train': X_train, 'X_test': X_test,
        'X_test_norm': X_test_norm,
        'y_train': y_train, 'y_test': y_test,
        'logreg': logreg, 'mlp': mlp,
        'y_pred_lr': y_pred_lr, 'y_prob_lr': y_prob_lr,
        'y_pred_mlp': y_pred_mlp, 'y_prob_mlp': y_prob_mlp,
        'nomes_features': nomes_features,
    }


# =============================================================================
# 4. VISUALIZAÇÕES
# =============================================================================

def gerar_visualizacoes(df, r):
    print('\n[*] Gerando visualizações...')

    # --- Fig 1: Distribuição da taxa de abandono ---
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(df['taxa_abandono_em'], bins=50, color='steelblue', edgecolor='white')
    ax.axvline(LIMIAR_ABANDONO, color='red', linestyle='--', linewidth=2,
               label=f'Limiar de classificação ({LIMIAR_ABANDONO}%)')
    ax.set_xlabel('Taxa de Abandono no Ensino Médio (%)')
    ax.set_ylabel('Número de escolas')
    ax.set_title('Distribuição da taxa de abandono — escolas públicas EM (2024)')
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DISTRIBUICAO, dpi=120)
    plt.close()
    print(f'   ✓ {FIG_DISTRIBUICAO}')

    # --- Fig 2: Matrizes de confusão lado a lado ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, nome, y_pred in [
        (axes[0], 'Regressão Logística', r['y_pred_lr']),
        (axes[1], 'MLP', r['y_pred_mlp']),
    ]:
        cm = confusion_matrix(r['y_test'], y_pred)
        im = ax.imshow(cm, cmap='Blues')
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(['Baixo', 'Alto']); ax.set_yticklabels(['Baixo', 'Alto'])
        ax.set_xlabel('Predito'); ax.set_ylabel('Real')
        ax.set_title(f'Matriz de Confusão — {nome}')
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j] > cm.max() / 2 else 'black',
                        fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(FIG_MATRIZ_CONFUSAO, dpi=120)
    plt.close()
    print(f'   ✓ {FIG_MATRIZ_CONFUSAO}')

    # --- Fig 3: Curvas ROC ---
    fig, ax = plt.subplots(figsize=(7, 6))
    for nome, y_prob in [
        ('Regressão Logística', r['y_prob_lr']),
        ('MLP', r['y_prob_mlp']),
    ]:
        fpr, tpr, _ = roc_curve(r['y_test'], y_prob)
        auc = roc_auc_score(r['y_test'], y_prob)
        ax.plot(fpr, tpr, linewidth=2, label=f'{nome} (AUC = {auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Aleatório')
    ax.set_xlabel('Taxa de Falso Positivo')
    ax.set_ylabel('Taxa de Verdadeiro Positivo')
    ax.set_title('Curvas ROC — Comparação de Modelos')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_ROC, dpi=120)
    plt.close()
    print(f'   ✓ {FIG_ROC}')

    # --- Fig 4: Importância das variáveis (permutation, sobre MLP) ---
    print('   Calculando permutation importance (pode levar 30s)...')
    result = permutation_importance(
        r['mlp'], r['X_test_norm'], r['y_test'],
        n_repeats=5, random_state=42, n_jobs=-1,
    )
    importancias = pd.Series(result.importances_mean, index=r['nomes_features'])
    importancias = importancias.sort_values(ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(importancias.index, importancias.values, color='steelblue')
    ax.set_xlabel('Importância (queda na acurácia ao embaralhar a variável)')
    ax.set_title('Top 15 variáveis mais importantes — MLP')
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_IMPORTANCIA, dpi=120)
    plt.close()
    print(f'   ✓ {FIG_IMPORTANCIA}')


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = carregar_e_limpar()
    X, y, nomes_features = preparar_features(df)
    r = treinar_e_avaliar(X, y, nomes_features)
    gerar_visualizacoes(df, r)

    print('\n' + '=' * 70)
    print(' CONCLUÍDO')
    print('=' * 70)
    print(' Arquivos gerados:')
    print(f'   - {FIG_DISTRIBUICAO}')
    print(f'   - {FIG_MATRIZ_CONFUSAO}')
    print(f'   - {FIG_ROC}')
    print(f'   - {FIG_IMPORTANCIA}')


if __name__ == '__main__':
    main()