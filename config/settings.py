import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)

# Chaves de API
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Caminho base do projeto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminhos para os diretórios de dados
DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, r'data/raw/')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, r'data/processed')
BRIEFING_JSON_PATH = os.path.join(PROJECT_ROOT, r'data/processed/briefing.json')
PROFILE_PATH = os.path.join(PROJECT_ROOT, r"data/raw/profile_data.json")
POST_PATH = os.path.join(PROJECT_ROOT, r"data/raw/post_data.json")
SEARCH_PATH = os.path.join(PROJECT_ROOT, r"data/raw/search_data.json")

# Caminho para o diretório de relatórios
REPORTS_PATH = os.path.join(PROJECT_ROOT, 'reports')
BRIEFING_PATH = os.path.join(PROJECT_ROOT, r'reports\briefing.md')
ESTRATEGIA_PATH = os.path.join(PROJECT_ROOT, r'reports\Estrategia.docx')
CONCORRENTES_PATH = os.path.join(PROJECT_ROOT, r'reports\Concorrentes.docx')

# Caminho para o template do Word
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, r'templates\template.docx') # [cite: 296]

# Parâmetros da API e de análise
MAX_POSTS_PER_PROFILE = 5 #

# Modelos de Linguagem (LLMs)
LLM = ChatGroq(model="gemma2-9b-it", temperature=0.4)
#LLM = ChatNVIDIA(model="google/gemma-2-9b-it", api_key=NVIDIA_API_KEY, temperature=0.2, top_p=0.7, max_tokens=1024)
LLM = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)
LLM_HIGH = ChatGroq(model="llama3-70b-8192", temperature=0.4)