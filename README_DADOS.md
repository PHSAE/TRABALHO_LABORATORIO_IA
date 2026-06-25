# Dados Utilizados no Projeto

Os arquivos de dados **não estão incluídos neste repositório** por questões de tamanho (os arquivos originais somam aproximadamente 250 MB). Esta página descreve como obter cada um deles e onde posicioná-los para que os scripts funcionem corretamente.

---

## Estrutura esperada de arquivos

Após o download, a pasta do projeto deve conter os seguintes arquivos:

```
TrabalhoIA/
├── etapa1_preparar_dados.py
├── etapa2_enriquecer.py
├── etapa3_modelagem.py
├── evasao_escolar.py
├── tx_rend_escolas_2024.xlsx        ← baixar conforme instruções abaixo
├── microdados_ed_basica_2024.csv    ← baixar conforme instruções abaixo
├── README.md
└── README_DADOS.md                  ← este arquivo
```

Os arquivos intermediários (`escolas_em_publicas_2024.csv` e `escolas_enriquecido_v1.csv`) são gerados automaticamente ao executar os scripts na ordem correta.

---

## Arquivo 1 — Taxas de Rendimento Escolar por Escola (2024)

**Nome esperado:** `tx_rend_escolas_2024.xlsx`  
**Tamanho aproximado:** 38 MB  
**Fonte:** INEP — Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira

### Como baixar

1. Acesse a página oficial:  
   https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar

2. Localize a aba ou seção referente ao ano **2024**.

3. Dentro dos arquivos disponíveis para 2024, procure pelo arquivo com granularidade **por escola** — o nome deve conter `escolas` e terminar em `.xlsx`. Evite os arquivos por Brasil/Regiões/UFs ou por Municípios, que têm granularidade menor.

4. Faça o download e salve o arquivo na pasta do projeto com o nome exato `tx_rend_escolas_2024.xlsx`.

### O que este arquivo contém

- Uma linha por escola brasileira (~128.000 escolas)
- Colunas de identificação: ano, região, UF, município, código e nome da escola, localização (Urbana/Rural), dependência administrativa (Federal/Estadual/Municipal/Privada)
- Taxas de aprovação, reprovação e abandono por etapa de ensino e por série
- A coluna utilizada como variável-alvo neste projeto é `3_CAT_MED` (Taxa de Abandono no Ensino Médio total)

---

## Arquivo 2 — Microdados da Educação Básica (2024)

**Nome esperado:** `microdados_ed_basica_2024.csv`  
**Tamanho aproximado:** 213 MB  
**Fonte:** INEP — Microdados do Censo Escolar da Educação Básica

### Como baixar

1. Acesse a página oficial:  
   https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar

2. Localize o pacote referente ao ano **2024** — o download é um arquivo `.zip` de aproximadamente 300–500 MB.

3. **Não descompacte o ZIP inteiro** — o pacote contém vários arquivos grandes (matrículas, docentes, turmas) que não são necessários para este projeto. Abra o ZIP e extraia **apenas** o arquivo:
   ```
   dados/microdados_ed_basica_2024.csv
   ```

4. Salve o arquivo extraído na pasta do projeto com o nome exato `microdados_ed_basica_2024.csv`.

### Atenção ao formato

Este arquivo usa convenções específicas do INEP que diferem do padrão comum:

| Propriedade | Valor |
|---|---|
| Separador de colunas | `;` (ponto e vírgula) |
| Codificação de caracteres | `latin-1` (não UTF-8) |
| Valores ausentes | `--` (dois traços) |

Os scripts do projeto já tratam essas convenções automaticamente — não é necessário converter o arquivo antes de usar.

### O que este arquivo contém

- Uma linha por escola brasileira (~215.000 escolas, todas as dependências)
- 476 colunas cobrindo infraestrutura física, saneamento, tecnologia, acessibilidade, equipamentos pedagógicos e profissionais de suporte
- As 22 colunas utilizadas neste projeto estão listadas na seção 3.2 do artigo e no código da Etapa 2 (`etapa2_enriquecer.py`)

---

## Como executar após o download

Com os dois arquivos na pasta do projeto, execute os scripts na seguinte ordem:

```bash
# Etapa 1: filtra escolas públicas com Ensino Médio
python etapa1_preparar_dados.py
# Gera: escolas_em_publicas_2024.csv (21.071 escolas)

# Etapa 2: enriquece com variáveis de infraestrutura
python etapa2_enriquecer.py
# Gera: escolas_enriquecido_v1.csv (21.071 escolas × 33 colunas)

# Etapa 3: treina modelos e gera visualizações
python etapa3_modelagem.py
# Gera: fig_distribuicao_abandono.png, fig_matriz_confusao.png,
#        fig_curvas_roc.png, fig_importancia_variaveis.png
```

### Dependências Python

```bash
pip install pandas numpy scikit-learn matplotlib openpyxl
```

Testado com Python 3.12+ e scikit-learn 1.8.0.

---

## Licença dos dados

Os dados do INEP são disponibilizados sob licença de dados abertos do Governo Federal Brasileiro, conforme a Lei de Acesso à Informação (Lei nº 12.527/2011). O uso é livre para fins educacionais e de pesquisa, com obrigação de citação da fonte.

**Citação recomendada:**

> INEP — Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira. *Taxas de Rendimento Escolar por Escola — 2024*. Brasília: INEP, 2025. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais. Acesso em: jun. 2026.

> INEP — Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira. *Microdados da Educação Básica 2024*. Brasília: INEP, 2025. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar. Acesso em: jun. 2026.
