# 🍽️ Fome Zero – Dashboard de Restaurantes (Zomato Dataset)

Este projeto foi desenvolvido para análise exploratória e visual das informações fornecidas no dataset público **Zomato**, apresentando insights sobre restaurantes ao redor do mundo e comportamento gastronômico regional.

> **Nota:**  
> Este dashboard é um modelo simplificado, criado exclusivamente para fins educacionais e de portfólio.  
> Não representa análises oficiais da empresa ou do mercado.

---

## 🎯 Objetivo Geral

Exibir uma visão clara e interativa do cenário global de restaurantes, permitindo:
- Entender o volume e distribuição geográfica de restaurantes
- Comparar avaliações médias por país e cidade
- Observar padrões de faixa de preço e diversidade culinária

---

## 🗂️ Estrutura do Dashboard

### 1. **Home**
Apresenta o panorama global com:
- Total de países no dataset
- Avaliação média geral
- Faixa de preço média
- Mapa mundial com distribuição dos restaurantes
- Filtro inicial por país

Função principal: **contexto macro** — onde o usuário visualiza o cenário mundial antes de aprofundar-se nas análises.

---

### 2. **Countries (Países)**

Comparativo entre países com:
- Quantidade de restaurantes registrados
- Avaliação média por país
- Faixa de preço predominante
- Diversidade de culinárias

Permite responder:
> “Quais países concentram maior presença gastronômica e qualidade média mais alta?”

---

### 3. **Cities (Cidades)**

Aprofunda a análise de forma progressiva:
- Ranking de cidades com mais restaurantes
- Avaliação média por cidade
- Distribuição de faixa de preço
- Diversidade culinária local

O filtro de cidades responde dinamicamente à seleção de país.

Responde:
> “Quais cidades são polos culinários dentro de cada país?”

---

### 4. **Cuisines (Culinárias)**

Nível final de detalhamento:
- Popularidade das principais culinárias
- Comparação Preço × Avaliação
- Distribuição regional de estilos gastronômicos

O filtro mostra apenas culinárias existentes dentro do país e cidade selecionados.

Responde:
> “Quais culinárias são mais competitivas, populares e bem avaliadas — e a que preço?”

---

## 🛠️ Tecnologias Utilizadas

| Ferramenta | Uso |
|------------|-----|
| Python 3.13 | Base do projeto |
| Streamlit | Interface do dashboard |
| Pandas | Manipulação e limpeza de dados |
| Plotly | Visualização de dados |
| Altair | Visualização adicional |
| Zomato Dataset | Base de dados analisada |

---

## 🔍 Metodologia e Lógica de Construção

1. **Carregamento e Padronização**
   - Correção de nomes e códigos de países
   - Remoção de duplicidades e nulos críticos

2. **Filtros Hierárquicos (Progressivos)**
   - País → Cidade → Culinária  
   - Cada nível só exibe valores possíveis após o filtro anterior

3. **KPIs Dinâmicos**
   - Avaliação média
   - Preço médio
   - Quantidade de restaurantes

4. **Visualização Inteligente**
   - Mapa para contexto global
   - Barras para comparativos
   - Boxplot/Dispersão para preço × avaliação

---

## 📈 Insights Observados

- Países com maior volume não necessariamente apresentam melhores avaliações.
- Cidades com forte densidade culinária tendem a exibir maior diversidade, mas avaliações variáveis.
- A faixa de preço não apresenta correlação direta com avaliação média: restaurantes mais caros não garantem melhor nota.
- A culinária dominante varia fortemente por contexto cultural, turístico e socioeconômico.

---

## 🚀 Acesse o Dashboard

Sem download e sem instalação:

👉 **Streamlit App:**  
https://fomezero-llewfxvsb9yte2xpkmuaud.streamlit.app/

---

## 👤 Autor

**Pedro Oliveira**

Projeto desenvolvido como peça de portfólio com foco em:
- Visualização de dados
- Interpretação de métricas
- Storytelling com dashboards
- Experiência inicial com dados reais

---

## 📌 Observação Final

Este dashboard não tem fins comerciais e não representa análises oficiais do mercado.  
Foi construído **exclusivamente para desenvolvimento de competências analíticas e apresentação em portfólio**.

