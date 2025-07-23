# AI Social - Automação de Estratégia e Análise de Instagram com IA

Este projeto é um sistema avançado projetado para automatizar a análise de perfis do Instagram e a geração de relatórios estratégicos de marketing de conteúdo. Utilizando Modelos de Linguagem Grandes (LLMs) e extração de dados, a ferramenta é capaz de realizar um briefing com o usuário, analisar concorrentes e gerar um plano de marketing completo, um relatório de análise de concorrência e um calendário de publicações.

## ✨ Funcionalidades

*   **Briefing Interativo:** Um formulário permite coletar informações essenciais sobre o cliente e seus objetivos. (Implementado em `src/chatbot/briefing_chat.py` e `api/v1/endpoints/brief_routes.py`)
*   **Análise de Briefing com LLM:** Interpreta as respostas do briefing para extrair e estruturar automaticamente os objetivos (principais e secundários), o público-alvo e os pilares de conteúdo iniciais.
*   **Ingestão de Dados do Instagram:** Utiliza a API da Apify para extrair dados públicos de perfis e publicações de concorrentes. (Implementado em `src/data_ingestion/extractInstagram.py`)
*   **Análise Aprofundada de Concorrentes:**
    *   Processa e enriquece os dados brutos, calculando métricas de engajamento, frequência e recência. (Implementado em `src/analysis/engine.py`)
    *   Gera visualizações de dados (gráficos e nuvens de palavras) para comparar o desempenho dos concorrentes.
    *   Utiliza um LLM para analisar os gráficos e textos, gerando insights e recomendações estratégicas.
*   **Geração Automática de Relatórios:** Cria documentos profissionais e detalhados em formatos `.docx` e `.xlsx`:
    1.  **Plano de Marketing de Conteúdo (`Estrategia.docx`):** Um documento completo com objetivos, persona, pilares de conteúdo, formatos recomendados e KPIs. (Gerado por `src/reporting/generator_report_estrategia.py`)
    2.  **Análise de Concorrentes (`Concorrentes.docx`):** Um relatório detalhado com análises de perfil, engajamento, formatos e frequência, incluindo gráficos e textos analíticos gerados por IA. (Gerado por `src/reporting/generator_report_concorrentes.py`)
    3.  **Calendário de Publicações (`publicações.xlsx`):** Uma planilha com ideias de conteúdo para Reels, Carrosséis, Imagens e Stories, alinhadas aos pilares de conteúdo definidos. (Gerado por `src/reporting/generator_report_publicacoes.py`)

## 🚀 Tecnologias e Bibliotecas

*   **Linguagem:** Python 3
*   **IA e LLMs:**
    *   `langchain`: Para orquestrar as interações com os modelos de linguagem.
    *   `langchain_groq`: Para acesso a LLMs de alta velocidade (Gemma, Llama).
    *   `pydantic`: Para estruturar e validar as saídas dos LLMs.
*   **Análise e Manipulação de Dados:**
    *   `pandas`: Para manipulação e análise dos dados extraídos.
    *   `scikit-learn`: Para análises estatísticas como PCA.
*   **Visualização de Dados:**
    *   `matplotlib` & `seaborn`: Para a criação de gráficos estáticos.
    *   `wordcloud`: Para gerar nuvens de hashtags.
*   **Extração de Dados:**
    *   `apify_client`: Para interagir com a plataforma Apify e extrair dados do Instagram.
*   **Geração de Relatórios:**
    *   `python-docx`: Para criar e manipular documentos Word (`.docx`).
    *   `openpyxl`: Para criar planilhas Excel (`.xlsx`).
*   **Ambiente:**
    *   `dotenv`: Para gerenciar variáveis de ambiente (chaves de API).
*   **Framework Web:**
    *   `Streamlit`: Para a interface web interativa (em `streamlit_app/app.py` e `streamlit_app/master_app.py`).
*   **API Backend:**
    *   `FastAPI`: Para a construção da API RESTful (em `api/v1/`).
*   **Banco de Dados:**
    *   `SQLite`: Utilizado para o banco de dados local (`banco.db`).

## ⚙️ Instalação e Configuração

1.  **Clone o repositório:**
    
    ```shell
    git clone https://github.com/Vini0606/Aplica-o-Web-AI-Social-
    cd Aplica-o-Web-AI-Social-
    ```
    
2.  **Crie e ative um ambiente virtual:**
    
    ```shell
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
    
3.  **Instale as dependências:**
    
    ```shell
    pip install -r requirements.txt
    ```
    
4.  **Configure as variáveis de ambiente:**
    
    *   Crie um arquivo chamado `.env` na raiz do projeto.
    *   Adicione suas chaves de API. Você precisará de chaves para a Apify, Groq, OpenAI, SerpAPI, Zenserp e Nvidia.
    
    ```dotenv
    APIFY_API_TOKEN="seu_token"
    OPENAI_API_KEY="seu_token"
    GROQ_API_KEY="seu_token"
    SERPAPI_API_KEY="seu_token"
    ZENSERP_API_KEY="seu_token"
    NVIDIA_API_KEY="seu_token"
    GEMINI_API_KEY="seu_token"
    SECRET_KEY="seu_token"
    ```
    

## ▶️ Como Usar

O processo é executado em etapas, orquestradas principalmente pelo `main.py` e pela interface Streamlit.

### Via Script `main.py` (Processo Batch)

1.  **Etapa 1: Briefing (Opcional)**
    
    *   Para realizar um novo briefing, execute o script interativo:
        
        ```shell
        python src/reporting/generator_report_briefing.py
        ```
        
    *   Ao final, o script gera um resumo em formato Markdown. Copie esse resumo e salve-o no arquivo `reports/briefing.md`.
    *   Alternativamente, preencha o arquivo `reports/briefing.md` manualmente com as informações do cliente.
2.  **Etapa 2: Coleta de Dados**
    
    *   O sistema é projetado para ler os dados de arquivos JSON localizados em `data/raw/`. Certifique-se de que os arquivos `profile_data.json` e `post_data.json` estejam presentes.
    *   A função `extrairDadosApifyInstagram` em `main.py` (ou diretamente em `src/data_ingestion/extractInstagram.py`) pode ser utilizada para buscar e salvar esses dados automaticamente, desde que os nomes de usuário dos concorrentes estejam definidos.
3.  **Etapa 3: Execução Principal**
    
    *   Com o `briefing.md` e os arquivos de dados prontos, execute o script principal:
        
        ```shell
        python main.py
        ```
        
    *   O script irá:
        *   Criar as pastas de `data` e `reports` se não existirem.
        *   Ler e analisar o `briefing.md` usando o LLM.
        *   Carregar e processar os dados dos concorrentes.
        *   Gerar os três relatórios: `Estrategia.docx`, `Concorrentes.docx` e `publicações.xlsx`.
4.  **Etapa 4: Verifique os Resultados**
    
    *   Os relatórios gerados estarão disponíveis na pasta `reports/`.

### Via Aplicação Web Streamlit

1.  **Inicie a aplicação Streamlit:**
    
    ```shell
    streamlit run streamlit_app/app.py
    ```
    
2.  A aplicação será aberta no seu navegador, geralmente em `http://localhost:8501`.
3.  Siga as instruções na interface para realizar o briefing, coletar dados e gerar relatórios de forma interativa.

## 📂 Estrutura do Projeto

```
.gitignore
banco.db
create_initial_master_user.py
main.py
models.py
README_NOVO.md
requirements.txt
run_pipeline.py

api/
├── __init__.py
└── v1/
    ├── __init__.py
    ├── endpoints/
    │   ├── __init__.py
    │   ├── brief_routes.py
    │   ├── chat_routes.py
    │   ├── data_routes.py
    │   └── report_routes.py
    └── schemas/
        ├── briefing.py
        ├── chat.py
        └── user.py

auth/
├── auth_routes.py
├── auth_schemas.py
├── auth_utils.py
└── dependencies.py

config/
└── settings.py

notebooks/
├── AutoClusterHPO.py
└── conteúdo.ipynb

src/
├── analysis/
│   └── engine.py
├── chatbot/
│   └── briefing_chat.py
├── data_ingestion/
│   ├── data_ingestion.py
│   ├── extractInstagram.py
│   └── gdrive_uploader.py
└── reporting/
    ├── generator_report_briefing.py
    ├── generator_report_concorrentes.py
    ├── generator_report_estrategia.py
    └── generator_report_publicacoes.py

streamlit_app/
├── Logo.png
├── app.py
├── branded_app.py
└── master_app.py

templates/
└── template.docx
```

## 🤝 Contribuição

Contribuições são bem-vindas! Se você tiver sugestões de melhoria, novas funcionalidades ou encontrar algum bug, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. (Assumindo licença MIT, verificar no repositório original se existe um arquivo LICENSE)

## 📞 Contato

Para dúvidas ou suporte, entre em contato com Vini0606 através do GitHub.

