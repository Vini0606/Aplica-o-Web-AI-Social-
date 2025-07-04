# AI Social - Automação de Estratégia e Análise de Instagram com IA

Este projeto é um sistema avançado projetado para automatizar a análise de perfis do Instagram e a geração de relatórios estratégicos de marketing de conteúdo. Utilizando Modelos de Linguagem Grandes (LLMs) e extração de dados, a ferramenta é capaz de realizar um briefing com o usuário, analisar concorrentes e gerar um plano de marketing completo, um relatório de análise de concorrência e um calendário de publicações.

## ✨ Funcionalidades

- **Briefing Interativo com IA:** Um chatbot conduz uma entrevista de briefing completa para coletar informações essenciais sobre o cliente e seus objetivos.
- **Análise de Briefing com LLM:** Interpreta as respostas do briefing para extrair e estruturar automaticamente os objetivos (principais e secundários), o público-alvo e os pilares de conteúdo iniciais.
- **Ingestão de Dados do Instagram:** Utiliza a API da Apify para extrair dados públicos de perfis e publicações de concorrentes.
- **Análise Aprofundada de Concorrentes:**
    - Processa e enriquece os dados brutos, calculando métricas de engajamento, frequência e recência.
    - Gera visualizações de dados (gráficos e nuvens de palavras) para comparar o desempenho dos concorrentes.
    - Utiliza um LLM para analisar os gráficos e textos, gerando insights e recomendações estratégicas.
- **Geração Automática de Relatórios:** Cria documentos profissionais e detalhados em formatos `.docx` e `.xlsx`:
    1.  **Plano de Marketing de Conteúdo (`Estrategia.docx`):** Um documento completo com objetivos, persona, pilares de conteúdo, formatos recomendados e KPIs.
    2.  **Análise de Concorrentes (`Concorrentes.docx`):** Um relatório detalhado com análises de perfil, engajamento, formatos e frequência, incluindo gráficos e textos analíticos gerados por IA.
    3.  **Calendário de Publicações (`publicações.xlsx`):** Uma planilha com ideias de conteúdo para Reels, Carrosséis, Imagens e Stories, alinhadas aos pilares de conteúdo definidos.

## 🚀 Tecnologias e Bibliotecas

- **Linguagem:** Python 3
- **IA e LLMs:**
    - `langchain`: Para orquestrar as interações com os modelos de linguagem.
    - `langchain_groq`: Para acesso a LLMs de alta velocidade (Gemma, Llama).
    - `pydantic`: Para estruturar e validar as saídas dos LLMs.
- **Análise e Manipulação de Dados:**
    - `pandas`: Para manipulação e análise dos dados extraídos.
    - `scikit-learn`: Para análises estatísticas como PCA.
- **Visualização de Dados:**
    - `matplotlib` & `seaborn`: Para a criação de gráficos estáticos.
    - `wordcloud`: Para gerar nuvens de hashtags.
- **Extração de Dados:**
    - `apify_client`: Para interagir com a plataforma Apify e extrair dados do Instagram.
- **Geração de Relatórios:**
    - `python-docx`: Para criar e manipular documentos Word (`.docx`).
    - `openpyxl`: Para criar planilhas Excel (`.xlsx`).
- **Ambiente:**
    - `dotenv`: Para gerenciar variáveis de ambiente (chaves de API).

## ⚙️ Instalação e Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    - Crie um arquivo chamado `.env` na raiz do projeto.
    - Adicione suas chaves de API. Você precisará de chaves para a Apify e para o Groq.
    ```env
    APIFY_API_TOKEN="sua_chave_apify"
    GROQ_API_KEY="sua_chave_groq"
    ```

## ▶️ Como Usar

O processo é executado em etapas, orquestradas pelo `main.py`.

1.  **Etapa 1: Briefing (Opcional)**
    - Para realizar um novo briefing, execute o script interativo:
      ```bash
      python src/reporting/generator_report_briefing.py
      ```
    - Ao final, o script gera um resumo em formato Markdown. Copie esse resumo e salve-o no arquivo `reports/briefing.md`.
    - Alternativamente, preencha o arquivo `reports/briefing.md` manualmente com as informações do cliente.

2.  **Etapa 2: Coleta de Dados**
    - O sistema é projetado para ler os dados de arquivos JSON localizados em `data/raw/`. Certifique-se de que os arquivos `profile_data.json` e `post_data.json` estejam presentes.
    - A função `extrairDadosApifyInstagram` em `main.py` pode ser utilizada para buscar e salvar esses dados automaticamente, desde que os nomes de usuário dos concorrentes estejam definidos.

3.  **Etapa 3: Execução Principal**
    - Com o `briefing.md` e os arquivos de dados prontos, execute o script principal:
      ```bash
      python main.py
      ```
    - O script irá:
        - Criar as pastas de `data` e `reports` se não existirem.
        - Ler e analisar o `briefing.md` usando o LLM.
        - Carregar e processar os dados dos concorrentes.
        - Gerar os três relatórios: `Estrategia.docx`, `Concorrentes.docx` e `publicações.xlsx`.

4.  **Etapa 4: Verifique os Resultados**
    - Os relatórios gerados estarão disponíveis na pasta `reports/`.