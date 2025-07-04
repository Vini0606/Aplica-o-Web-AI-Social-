import os
from langchain_groq import ChatGroq

# Caminho base do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminhos para os diretórios de dados
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data/raw/')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data/processed')
BRIEFING_JSON_PATH = os.path.join(PROJECT_ROOT, r'data/processed/briefing.json')
PROFILE_PATH = os.path.join(PROJECT_ROOT, "data/raw/profile_data.json")
POST_PATH = os.path.join(PROJECT_ROOT, "data/raw/post_data.json")

# Caminho para o diretório de relatórios
REPORTS_PATH = os.path.join(PROJECT_ROOT, 'reports')
BRIEFING_PATH = os.path.join(PROJECT_ROOT, r'reports\briefing.md')
ESTRATEGIA_PATH = os.path.join(PROJECT_ROOT, 'reports\Estrategia.docx')
CONCORRENTES_PATH = os.path.join(PROJECT_ROOT, 'reports\Concorrentes.docx')

# Caminho para o template do Word
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, r'templates\template.docx') # [cite: 296]

# Parâmetros da API e de análise
MAX_POSTS_PER_PROFILE = 50 #

LLM = ChatGroq(model="gemma2-9b-it", temperature=0.4)