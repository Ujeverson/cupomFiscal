# Sistema de Extração e Análise de Cupons Fiscais

## 📋 Descrição

Sistema automatizado para extração, armazenamento e análise de dados de cupons fiscais eletrônicos (NFC-e) do portal SEFAZ-GO. O projeto foi desenvolvido como parte da disciplina de **Extração Automática de Dados** da Especialização em Sistemas e Agentes Inteligentes da UFG.

## 🎯 Objetivo

Automatizar a coleta de dados de notas fiscais eletrônicas, permitindo análise detalhada de produtos, valores, datas e formas de pagamento através de uma interface web interativa.

## 👥 Autores

- **Marcu Loreto**
- **Rafael Fideles** 
- **Ricardo Kerr**
- **Ujeverson Tavares**

## 🏗️ Arquitetura do Sistema

O sistema é composto por quatro módulos principais:

### 1. **scraper.py** - Extração de Dados
- Função central: `scraper_function(chave_de_acesso: str)`
- Utiliza Selenium para acessar notas fiscais no portal SEFAZ-GO
- Extrai produtos, valores, datas e formas de pagamento
- Salva dados em formato JSONL no arquivo `dados/notas.txt`
- Verifica duplicidade antes de processar

### 2. **app.py** - Interface Web (Streamlit)
- Dashboard interativo para análise de dados
- Funcionalidades de inserção manual e em lote
- Filtros por produto, data e forma de pagamento
- Visualizações gráficas com Plotly
- Extração automática de IDs de links

### 3. **feed_db.py** - Processamento em Lote
- Processa múltiplos IDs de notas fiscais automaticamente
- Lê IDs do arquivo `dados/ids_extraidos.csv`
- Executa extração em lote via scraper

### 4. **extrator_wpp.py** - Extração de IDs
- Extrai IDs de notas fiscais de links (ex: WhatsApp)
- Aplica regex para identificar chaves de acesso
- Salva IDs em `dados/ids_extraidos.csv`

## 📁 Estrutura do Projeto

```
cupomFiscal/
├── app.py                 # Interface web principal
├── scraper.py            # Módulo de extração de dados
├── feed_db.py            # Processamento em lote
├── extrator_wpp.py       # Extração de IDs de links
├── mongo.py              # Módulo obsoleto (não utilizado)
├── requirements.txt      # Dependências Python
├── chromedriver.exe      # Driver do Chrome
├── dados/
│   ├── notas.txt         # Dados extraídos (JSONL)
│   ├── ids_extraidos.csv # IDs das notas fiscais
│   ├── links.txt         # Links de notas fiscais
│   └── relatorio.md      # Relatório técnico detalhado
└── arquivos de documentação
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.x
- Google Chrome instalado

### Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd cupomFiscal
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
streamlit run app.py
```

## 💻 Como Usar

### 1. Extração de IDs de Links
- Cole links de notas fiscais em `dados/links.txt`
- Execute `python extrator_wpp.py` para extrair IDs
- Os IDs serão salvos em `dados/ids_extraidos.csv`

### 2. Processamento em Lote
- Execute `python feed_db.py` para processar todos os IDs
- Os dados serão extraídos e salvos automaticamente

### 3. Interface Web
- Acesse `http://localhost:8501` após executar `streamlit run app.py`
- Use a interface para:
  - Extrair IDs de links manualmente
  - Adicionar notas individuais
  - Processar notas em lote
  - Visualizar análises e gráficos

## 📊 Funcionalidades da Interface

### Extração e Inserção
- **Extrair ID de link**: Cole um link de nota fiscal e extraia o ID
- **Adicionar nota manual**: Insira o código da nota fiscal
- **Processamento automático**: Adicione o próximo ID do CSV
- **Processamento em lote**: Adicione todas as notas do CSV

### Análise e Visualização
- **Produtos mais comprados**: Top 15 produtos por quantidade
- **Produtos menos comprados**: 15 produtos com menor volume
- **Total de compras por período**: Análise por dia/mês
- **Formas de pagamento**: Comparativo entre métodos
- **Valor médio**: Média de valores por compra
- **Tabela completa**: Todos os produtos ordenados

### Filtros
- **Por produto**: Busca por nome do produto
- **Por data**: Filtro por período específico
- **Por forma de pagamento**: Filtro por método de pagamento

## 🔧 Tecnologias Utilizadas

- **Python 3.x**: Linguagem principal
- **Selenium**: Web scraping automatizado
- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações gráficas interativas
- **webdriver-manager**: Gerenciamento automático do ChromeDriver

## 📈 Fluxo de Dados

1. **Coleta de Links** → `dados/links.txt`
2. **Extração de IDs** → `dados/ids_extraidos.csv`
3. **Processamento** → `dados/notas.txt` (JSONL)
4. **Análise** → Interface Streamlit com gráficos

## 🛡️ Características de Robustez

- **Verificação de duplicidade**: Evita processamento duplicado
- **Tratamento de erros**: Sistema não trava com dados ausentes
- **Feedback visual**: Mensagens claras para o usuário
- **Compatibilidade automática**: ChromeDriver gerenciado automaticamente
- **Persistência local**: Dados salvos em arquivos locais

## 📝 Formato dos Dados

### Arquivo `dados/notas.txt` (JSONL)
```json
{
  "produto": "Nome do Produto",
  "quantidade": "1",
  "unidade": "UN",
  "valor_unitario": "10,50",
  "total_da_venda": 10.5,
  "forma_de_pagamento": "Cartão de Crédito",
  "data_hora": "2024-01-15T10:30:00",
  "chave_nota": "12345678901234567890123456789012345678901234"
}
```

### Arquivo `dados/ids_extraidos.csv`
```csv
id
12345678901234567890123456789012345678901234
```

## 🔍 Exemplos de Uso

### Processamento de Links do WhatsApp
1. Cole links de notas fiscais em `dados/links.txt`
2. Execute `python extrator_wpp.py`
3. Execute `python feed_db.py` para processar todos os IDs
4. Acesse a interface web para análise

### Análise Manual
1. Execute `streamlit run app.py`
2. Cole um link de nota fiscal na interface
3. Clique em "Extrair e Salvar ID"
4. Clique em "Adicionar Nota" para processar
5. Visualize os gráficos e análises

## 📋 Relatório Técnico

Para informações técnicas detalhadas, consulte o arquivo `dados/relatorio.md` que contém:
- Arquitetura detalhada do sistema
- Fluxo de dados completo
- Funcionalidades específicas
- Considerações de implementação

## 🤝 Contribuição

Este projeto foi desenvolvido como trabalho acadêmico. Para contribuições:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos na disciplina de Extração Automática de Dados da UFG.

---

**Disciplina:** Extração Automática de Dados  
**Instituição:** Universidade Federal de Goiás (UFG)  
**Especialização:** Sistemas e Agentes Inteligentes  
**Ano:** 2025 