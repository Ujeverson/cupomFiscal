# Relatório Técnico: Sistema de Extração e Análise de Dados de Cupons Fiscais

## 1. Introdução

Este relatório descreve o funcionamento do sistema de extração, armazenamento e análise de cupons fiscais eletrônicos (NFC-e), atualizado para operar totalmente sem dependências de banco de dados externos, utilizando arquivos locais em formato JSONL e CSV. O sistema automatiza a coleta, processamento em lote e análise visual dos dados, com interface web amigável e recursos de automação.

## 2. Arquitetura Geral

O sistema é composto por quatro principais módulos:
- **scraper.py:** Extração automatizada dos dados das notas fiscais diretamente do portal SEFAZ-GO usando Selenium.
- **feed_db.py:** Processamento em lote de múltiplos IDs de notas fiscais, acionando o scraper para cada um.
- **app.py:** Interface web interativa (Streamlit) para inserção, automação e análise dos dados extraídos.
- **extrator_wpp.py:** Utilitário para extrair IDs de notas fiscais a partir de links coletados (ex: via WhatsApp) e salvar em CSV.

Todos os dados extraídos são armazenados localmente em arquivos `.txt` (formato JSONL) e `.csv`, eliminando a necessidade de MongoDB.

## 3. Fluxo de Dados
1. **Extração de IDs:**
   - O script `extrator_wpp.py` lê o arquivo `dados/links.txt`, aplica regex para extrair as chaves de acesso das notas e salva em `dados/ids_extraidos.csv`.
2. **Raspagem e Armazenamento:**
   - O script `feed_db.py` lê as chaves extraídas, utiliza a função `scraper_function` (em `scraper.py`) para coletar os dados de cada nota e armazena em `dados/notas.txt` (JSONL).
   - O usuário pode também adicionar notas manualmente ou processar todas as notas do CSV pela interface web.
3. **Análise e Visualização:**
   - O aplicativo principal (`app.py`) carrega os dados do arquivo JSONL, permite a inserção de novas notas, aplicação de filtros (produto, data, forma de pagamento) e apresenta gráficos e tabelas interativas.

## 4. Principais Componentes

### 4.1. `scraper.py`
- Função central: `scraper_function(chave_de_acesso: str)`
- Utiliza Selenium para acessar a nota, extrair produtos, valores, datas e forma de pagamento.
- O ChromeDriver é gerenciado automaticamente pelo webdriver-manager, garantindo compatibilidade.
- Os dados de cada produto extraído são salvos em `dados/notas.txt` no formato JSONL (um JSON por linha).
- Antes de salvar, verifica se a nota já foi processada para evitar duplicidade.

### 4.2. `feed_db.py`
- Lê uma lista de IDs de notas fiscais do arquivo `dados/ids_extraidos.csv`.
- Para cada ID, chama o `scraper_function` para extrair e salvar os dados.
- Exibe mensagens de status no terminal para acompanhamento do processamento em lote.

### 4.3. `app.py` (Streamlit)
- Interface web para interação com o usuário, composta por diversas funcionalidades:

#### a) Extração e Salvamento de IDs
- Campo para inserir manualmente um link de nota fiscal e botão para extrair e salvar o ID em `dados/ids_extraidos.csv`.
- Verificação robusta de duplicidade: antes de salvar um novo ID, todos os IDs existentes são carregados e o novo só é salvo se for único.
- Feedback visual ao usuário sobre sucesso, erro ou duplicidade.

#### b) Adição de Notas Individuais e em Lote
- Campo para inserir manualmente o código da nota fiscal e botão para adicionar a nota (extrai e salva os dados automaticamente).
- Botão para adicionar automaticamente o próximo ID do CSV ao campo de nota, facilitando o processamento sequencial.
- Botão para adicionar todos os IDs do arquivo CSV de uma só vez, processando cada ID e salvando as notas correspondentes.
- Logs detalhados na barra lateral: para cada ID processado em lote, exibe se a nota foi adicionada, já estava presente ou houve erro.
- Resumo final do processamento em lote com contagem de sucessos, duplicidades e erros.

#### c) Visualização e Análise de Dados
- Carrega todos os dados de `dados/notas.txt` em um DataFrame pandas.
- Permite filtrar produtos pelo nome.
- Exibe tabelas e gráficos interativos para análise dos dados extraídos.
- Tratamento robusto para DataFrames vazios ou com colunas ausentes, evitando erros de execução.

### 4.4. `extrator_wpp.py`
- Lê links de notas fiscais de um arquivo de texto (`dados/links.txt`).
- Utiliza expressão regular para extrair o ID de cada link válido.
- Salva os IDs extraídos em `dados/ids_extraidos.csv` para posterior processamento.

## 5. Tecnologias Utilizadas
- Python 3.x
- Selenium (web scraping)
- Pandas (manipulação de dados)
- Streamlit (dashboard interativo)
- Plotly (visualização gráfica)
- webdriver-manager (gestão automática do ChromeDriver)

## 6. Funcionalidades da Aplicação

A aplicação oferece um conjunto completo de funções para automação, extração, inserção, análise e visualização de dados de cupons fiscais eletrônicos. Abaixo estão listadas todas as funcionalidades disponíveis, com breve explicação de cada uma e onde podem ser acessadas:

### 6.1 Extração de IDs de Notas Fiscais
- **Extrair IDs de links**: O script `extrator_wpp.py` lê links de notas fiscais de `dados/links.txt` e extrai automaticamente os IDs (chaves de acesso), salvando-os em `dados/ids_extraidos.csv`.
- **Extrair e salvar ID manualmente**: Na interface Streamlit (`app.py`), o usuário pode colar um link de nota fiscal e clicar em um botão para extrair e salvar o ID no CSV, com verificação de duplicidade.

### 6.2 Inserção e Adição de Notas
- **Inserir nota manualmente**: Campo na interface para digitar ou colar o código/ID da nota fiscal e adicionar seus dados ao sistema (extração via Selenium e salvamento em JSONL).
- **Adicionar próximo ID do CSV**: Botão na interface que insere automaticamente o próximo ID do arquivo CSV no campo de nota, facilitando o processamento sequencial.
- **Adicionar todas as notas do CSV**: Botão que processa todos os IDs do arquivo `dados/ids_extraidos.csv` de uma vez, extraindo e salvando todas as notas correspondentes.
- **Inserção em lote via script**: O script `feed_db.py` permite processar todos os IDs do CSV em lote, sem interface gráfica.

### 6.3 Processamento e Armazenamento
- **Processamento automatizado**: Toda nota adicionada (manual ou em lote) é processada pelo Selenium, extraída do portal SEFAZ-GO e salva em `dados/notas.txt` (formato JSONL).
- **Verificação de duplicidade**: Antes de salvar um novo ID ou nota, o sistema verifica se já existe, evitando registros duplicados.
- **Logs detalhados**: Ao processar em lote, a interface exibe logs detalhados para cada ID (adicionada, já existente, erro), além de um resumo final.

### 6.4 Visualização e Análise
- **Visualização tabular**: Exibe todos os dados extraídos em formato de tabela interativa na interface Streamlit.
- **Filtros de busca**: Permite filtrar produtos pelo nome diretamente na interface.
- **Visualização gráfica**: Geração de gráficos interativos para análise de produtos, datas, formas de pagamento, etc.

### 6.5 Robustez e Usabilidade
- **Feedback visual**: Mensagens de sucesso, erro e dicas são exibidas ao usuário durante todas as operações.
- **Tratamento de exceções**: O sistema lida com arquivos vazios, dados ausentes e erros de scraping sem travar a aplicação.
- **Compatibilidade automática do driver Selenium**: O ChromeDriver é gerenciado automaticamente, evitando erros de versão.

---

## 7. Considerações Finais


O sistema está pronto para uso em cenários de extração, armazenamento e análise de dados fiscais, sendo facilmente adaptável para diferentes fontes de dados ou requisitos de análise. Todo o fluxo é transparente ao usuário, com logs detalhados e mecanismos de proteção contra duplicidade.

---

**Autores:** Marcu Loreto, Rafael Fideles, Ricardo Kerr, Ujeverson Tavares

**Disciplina:** Extração Automática de Dados - Especialização em Sistemas e Agentes Inteligentes. UFG

**Ano:** 2025


## 1. Introdução
O sistema apresentado automatiza a extração, armazenamento e análise de dados de cupons fiscais eletrônicos (NFC-e), visando a Extração Automática de Dados. Utiliza técnicas de web scraping, persistência em banco de dados NoSQL (MongoDB) e visualização interativa de dados com Streamlit.

## 2. Arquitetura do Sistema
O sistema está dividido nos seguintes módulos principais:

- **Coleta de Dados (Web Scraping):** Utiliza Selenium para extrair informações de produtos, datas e formas de pagamento diretamente do portal da SEFAZ-GO, a partir de chaves de acesso extraídas de links.
- **Persistência:** Os dados extraídos são armazenados em coleções MongoDB, separando informações detalhadas de produtos e histórico de chaves processadas.
- **Processamento e Análise:** Dados são carregados e tratados com Pandas, permitindo filtragem, agregação e preparação para análise.
- **Visualização:** Uma interface web interativa (Streamlit) permite ao usuário explorar os dados, aplicar filtros, adicionar novas notas e visualizar gráficos dinâmicos e tabelas.

## 3. Fluxo de Dados
1. **Extração de IDs:**  
   O script `extrator_wpp.py` lê o arquivo `dados/links.txt`, aplica regex para extrair as chaves de acesso das notas e salva em `dados/ids_extraidos.csv`.
2. **Raspagem e Alimentação do Banco:**  
   O script `feed_db.py` lê as chaves extraídas, utiliza a função `scraper_function` (em `scraper.py`) para coletar os dados de cada nota e armazena no MongoDB.
3. **Análise e Visualização:**  
   O aplicativo principal (`app.py`) carrega os dados do MongoDB, permite a inserção de novas notas, aplicação de filtros (produto, data, forma de pagamento) e apresenta gráficos (produtos mais/menos vendidos, total de compras por período, comparativo de formas de pagamento, valor médio de compra).

## 4. Principais Componentes
### 4.1. `scraper.py`
- Função central: `scraper_function(chave_de_acesso: str)`
- Utiliza Selenium para acessar a nota, extrair produtos, valores, datas e forma de pagamento.
- Insere produtos e chaves processadas no MongoDB.

### 4.2. `mongo.py`
- Conexão e operações com MongoDB.
- Funções utilitárias para conversão dos dados em DataFrame e agregações.

### 4.3. `app.py`
- Interface Streamlit.
- Permite inserção manual de notas, filtragem, visualização de gráficos e tabelas.

### 4.4. Scripts utilitários
- `extrator_wpp.py`: extrai chaves de acesso de links.
- `feed_db.py`: executa processamento em lote das chaves para alimentar o banco.

## 5. Tecnologias Utilizadas
- Python 3.x
- Selenium (web scraping)
- Pandas (manipulação de dados)
- MongoDB (persistência NoSQL)
- Streamlit (dashboard interativo)
- Plotly (visualização gráfica)

## 6. Funcionalidades da Aplicação

A aplicação oferece um conjunto completo de funções para automação, extração, inserção, análise e visualização de dados de cupons fiscais eletrônicos. Abaixo estão listadas todas as funcionalidades disponíveis, com breve explicação de cada uma e onde podem ser acessadas:

### 6.1 Extração de IDs de Notas Fiscais
- **Extrair IDs de links**: O script `extrator_wpp.py` lê links de notas fiscais de `dados/links.txt` e extrai automaticamente os IDs (chaves de acesso), salvando-os em `dados/ids_extraidos.csv`.
- **Extrair e salvar ID manualmente**: Na interface Streamlit (`app.py`), o usuário pode colar um link de nota fiscal e clicar em um botão para extrair e salvar o ID no CSV, com verificação de duplicidade.

### 6.2 Inserção e Adição de Notas
- **Inserir nota manualmente**: Campo na interface para digitar ou colar o código/ID da nota fiscal e adicionar seus dados ao sistema (extração via Selenium e salvamento em JSONL).
- **Adicionar próximo ID do CSV**: Botão na interface que insere automaticamente o próximo ID do arquivo CSV no campo de nota, facilitando o processamento sequencial.
- **Adicionar todas as notas do CSV**: Botão que processa todos os IDs do arquivo `dados/ids_extraidos.csv` de uma vez, extraindo e salvando todas as notas correspondentes.
- **Inserção em lote via script**: O script `feed_db.py` permite processar todos os IDs do CSV em lote, sem interface gráfica.

### 6.3 Processamento e Armazenamento
- **Processamento automatizado**: Toda nota adicionada (manual ou em lote) é processada pelo Selenium, extraída do portal SEFAZ-GO e salva em `dados/notas.txt` (formato JSONL).
- **Verificação de duplicidade**: Antes de salvar um novo ID ou nota, o sistema verifica se já existe, evitando registros duplicados.
- **Logs detalhados**: Ao processar em lote, a interface exibe logs detalhados para cada ID (adicionada, já existente, erro), além de um resumo final.

### 6.4 Visualização e Análise
- **Visualização tabular**: Exibe todos os dados extraídos em formato de tabela interativa na interface Streamlit.
- **Filtros de busca**: Permite filtrar produtos pelo nome diretamente na interface.
- **Visualização gráfica**: Geração de gráficos interativos para análise de produtos, datas, formas de pagamento, etc.

### 6.5 Robustez e Usabilidade
- **Feedback visual**: Mensagens de sucesso, erro e dicas são exibidas ao usuário durante todas as operações.
- **Tratamento de exceções**: O sistema lida com arquivos vazios, dados ausentes e erros de scraping sem travar a aplicação.
- **Compatibilidade automática do driver Selenium**: O ChromeDriver é gerenciado automaticamente, evitando erros de versão.

---

## 7. Considerações Finais

O sistema oferece uma solução robusta para automação da coleta, armazenamento e análise de dados de cupons fiscais, facilitando a geração de insights para tomada de decisão. A modularidade permite fácil manutenção e expansão para novos tipos de análises ou fontes de dados.
