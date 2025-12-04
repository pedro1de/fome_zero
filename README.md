🍽️ Fome Zero – Dashboard de Restaurantes (Zomato Dataset)

Este projeto tem como objetivo analisar e apresentar informações sobre restaurantes ao redor do mundo, com base no dataset público Zomato.
A solução foi construída em Python + Streamlit, com visual limpo e filtragem progressiva (País → Cidade → Culinária).

Observação Importante:
Este é um modelo analítico simplificado. Não representa análises oficiais da empresa ou do mercado. Foi desenvolvido exclusivamente para fins educacionais e de portfólio.

🎯 Objetivo Geral

Fornecer uma visão estruturada e navegável sobre:

Distribuição global de restaurantes

Avaliações médias por região

Faixa de preços por país e culinária

Volume e diversidade gastronômica por cidade

A análise permite entender tendências, padrões de consumo e concentração de mercado no setor de alimentação.

🗂️ Estrutura do Dashboard
1. Home

Apresenta a visão global:

Total de países no dataset

Avaliação média global

Faixa de preço média

Distribuição de restaurantes no mapa

Filtro de País

Função da tela: contexto macro.

2. Countries (Visão por País)

Aba projetada para análise comparativa global entre países:

Quantidade de restaurantes por país

Média de avaliação

Distribuição de faixas de preço

Diversidade de culinárias

→ Ajuda a responder:
"Quais países possuem maior concentração gastronômica e qualidade média mais alta?"

3. Cities (Visão por Cidade)

Filtragem refinada (País → Cidade):

Ranking de cidades por número de restaurantes

Avaliação média por cidade

Faixa de preço típica

Distribuição de culinárias locais

→ Ajuda a responder:
"Quais cidades são polos culinários dentro de cada país?"

4. Cuisines (Visão por Culinária)

Filtragem final (País → Cidade → Culinária):

Top culinárias por volume

Relação Preço × Avaliação

Perfil de popularidade

Presença global/local

→ Responde:
"Quais culinárias são mais competitivas e bem avaliadas, e a que preço?"

🛠️ Tecnologias Utilizadas
Ferramenta	Finalidade
Python 3.13	Base do projeto
Streamlit	Interface interativa
Pandas	Tratamento de dados
Plotly	Visualização de gráficos
Altair	Gráficos complementares
Zomato Dataset	Dados de restaurantes
🔍 Lógica de Construção

ETL Simplificado

Leitura do dataset (zomato.csv)

Padronização de nomes de países e colunas

Remoção de duplicados e nulos essenciais

Progressão de Filtros

País → Cidade → Culinária

Sempre respeitando apenas valores disponíveis após o filtro anterior

KPIs Dinâmicos

Avaliação média

Preço médio

Quantidade de restaurantes

Visualização Multi-Nível

Mapa global (macro contexto)

Barras e ranking (comparação)

Boxplot e dispersão (qualidade vs custo)

📈 Insights Observados (opcionais)

Mercados muito populosos tendem a apresentar maior diversidade gastronômica, mas avaliações mais distribuídas (nem sempre altas).

Culinárias dominantes por país revelam padrões culturais e turísticos.

Cidades com maior concentração de restaurantes não são necessariamente as mais bem avaliadas.

Faixa de preço não guarda correlação forte com avaliação: restaurantes caros não garantem maior satisfação.

🚀 Como Executar

Sem instalar nada, acesse:

👉 Deploy Streamlit
https://fomezero-llewfxvsb9yte2xpkmuaud.streamlit.app/

👤 Autor

Pedro Oliveira
Dashboard construído como projeto analítico inicial para compor portfólio e validar competências em:

Visualização de dados

Tratamento e estruturação

Storytelling com dados

Construção de dashboards interativos
