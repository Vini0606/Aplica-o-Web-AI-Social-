# Gerador de Relatório de Análise de Concorrentes do Instagram com IA

[cite_start]Este projeto é uma ferramenta de automação que gera um relatório de análise de concorrentes para o Instagram.  [cite_start]Utilizando a plataforma Apify para extração de dados, LangChain e modelos de linguagem (LLMs) para análise, e python-docx para a criação de relatórios, esta aplicação transforma um simples briefing em um documento .docx profissional e personalizado. 

## Funcionalidades

- [cite_start]**Análise de Briefing em Linguagem Natural**: Extrai o nome do cliente e a lista de concorrentes de um texto simples. 
- [cite_start]**Extração de Dados Abrangente**: Coleta dados de perfil (seguidores, posts, etc.) e dados de posts individuais (curtidas, comentários, legendas) usando a Apify. 
- [cite_start]**Análise Quantitativa (KPIs)**: Calcula automaticamente os principais indicadores de desempenho, como taxa de engajamento média. 
- [cite_start]**Análise Qualitativa com IA**: Utiliza um LLM para identificar os pilares de conteúdo e o tom de voz dos concorrentes. 
- [cite_start]**Geração de Relatório Profissional**: Cria um documento .docx com design personalizado, incluindo texto, tabelas formatadas e visualizações de dados. 

## Configuração e Instalação

[cite_start]Siga estes passos para configurar e executar o projeto em sua máquina local. 

### 1. Clone o Repositório

```bash

git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio

```

### 2. Rodar o Projeto

```bash

python -m venv venv

# Ativar AV No Windows:
venv\Scripts\activate

# Intalar Dependências:
pip install -r requirements.txt

# Preencher arquivo .env com API Keys na Raiz do Projeto:
APIFY_API_TOKEN="seu_token_da_apify"
OPENAI_API_KEY="seu_token_da_openai"

# Rodar Sistema
python main.py

```

Seguindo todos esses passos, você terá uma implementação funcional e completa do sistema descrito no seu documento.