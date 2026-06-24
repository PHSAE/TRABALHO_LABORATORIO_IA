# Classificação de Risco de Abandono Escolar no Ensino Médio Público Brasileiro

Este repositório contém o código-fonte, os dados processados e as visualizações geradas para um projeto aplicado de Inteligência Artificial voltado à classificação de escolas públicas brasileiras quanto ao risco de abandono escolar no Ensino Médio.

O trabalho utiliza dados reais do Censo Escolar 2024 e das Taxas de Rendimento Escolar disponibilizadas pelo INEP. A proposta inicial de predição individual de evasão foi reformulada para uma abordagem por escola, devido às limitações de acesso a dados individualizados de estudantes e às restrições associadas à LGPD.

## Objetivo

Desenvolver um pipeline reprodutível de aprendizado de máquina capaz de classificar escolas públicas com oferta de Ensino Médio em duas categorias:

* baixo abandono;
* alto abandono.

A classificação foi definida a partir da taxa de abandono escolar no Ensino Médio, considerando como alto abandono escolas com taxa igual ou superior a 5%.

## Dados utilizados

Foram utilizadas duas fontes principais:

* Taxas de Rendimento Escolar por Escola — INEP 2024;
* Microdados da Educação Básica — INEP 2024.

As bases foram integradas por meio do código da escola (`CO_ENTIDADE`), permitindo combinar informações de abandono escolar com variáveis de infraestrutura, localização, dependência administrativa, recursos tecnológicos, saneamento e profissionais de suporte.

## Estrutura do repositório

```text
.
├── codigo/
│   ├── etapa1_preparar_dados.py
│   ├── etapa2_enriquecer.py
│   └── etapa3_modelagem.py
│
├── dados/
│   └── README_DADOS.md
│
├── figuras/
│   ├── fig_distribuicao_abandono.png
│   ├── fig_matriz_confusao.png
│   ├── fig_curvas_roc.png
│   └── fig_importancia_variaveis.png
│
├── requirements.txt
└── README.md
```

## Pipeline desenvolvido

O projeto foi organizado em três etapas principais:

1. Preparação da base de rendimento escolar;
2. Enriquecimento da base com variáveis dos microdados do Censo Escolar;
3. Treinamento, avaliação e interpretação dos modelos de aprendizado de máquina.

Foram aplicadas etapas de filtragem, tratamento de valores ausentes, tratamento de outliers, codificação de variáveis categóricas, padronização dos dados, divisão treino/teste e avaliação por métricas objetivas.

## Modelos avaliados

Foram comparados dois modelos supervisionados:

* Regressão Logística, utilizada como baseline interpretável;
* Rede Neural Artificial do tipo Perceptron Multicamadas (MLP), utilizada como modelo principal.

## Métricas e visualizações

Os modelos foram avaliados por meio das seguintes métricas:

* acurácia;
* precisão;
* recall;
* F1-score;
* AUC-ROC;
* matriz de confusão.

Também foram geradas visualizações para análise dos resultados, incluindo distribuição da taxa de abandono, curvas ROC, matrizes de confusão e importância das variáveis por permutação.

## Como executar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute os scripts na seguinte ordem:

```bash
python etapa1_preparar_dados.py
python etapa2_enriquecer.py
python etapa3_modelagem.py
```

## Observações éticas

Este projeto não realiza predição individual de estudantes. A análise é feita no nível da escola, utilizando dados públicos e agregados. Ainda assim, os resultados devem ser interpretados com cautela, pois modelos treinados sobre dados educacionais podem refletir desigualdades regionais, socioeconômicas e estruturais já existentes.

O modelo deve ser compreendido como ferramenta de apoio à decisão para gestores públicos, e não como mecanismo automático de classificação ou punição de escolas.

## Autor

Pedro Henrique Greco Motta
CEFET-MG — Engenharia Elétrica
Laboratório de Inteligência Artificial — Tópicos Especiais em Computação Aplicada
