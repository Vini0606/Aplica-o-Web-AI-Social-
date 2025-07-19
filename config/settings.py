import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI # Exemplo: se estiver usando Gemini/Langchain
import google.generativeai as genai

load_dotenv(override=True)

# Chaves de API
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Configurações de Autenticação JWT (NOVO)
SECRET_KEY = os.getenv("SECRET_KEY", "d1g7h6a9-2b3c-4d5e-6f7g-8h9i0j1k2l3m") # Use uma chave forte em produção!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Tempo de expiração do token

genai.configure(api_key=GEMINI_API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed"
REPORTS_PATH = BASE_DIR / "reports"
TEMPLATE_PATH = BASE_DIR / "templates" / "template.docx"

PROFILE_PATH = RAW_DATA_PATH / "profile_data.json"
POST_PATH = RAW_DATA_PATH / "post_data.json"
SEARCH_PATH = RAW_DATA_PATH / "search_data.json"
BRIEFING_PATH = BASE_DIR / "briefing.md" # Assumindo que o briefing inicial está em um arquivo
BRIEFING_JSON_PATH = PROCESSED_DATA_PATH / "briefing.json"
ESTRATEGIA_PATH = REPORTS_PATH / "Estrategia para Instagram.docx"
CONCORRENTES_PATH = REPORTS_PATH / "Análise de Concorrentes.docx"

CHAT_HISTORY_PATH = PROCESSED_DATA_PATH / "chat_histories" # Nova pasta
os.makedirs(CHAT_HISTORY_PATH, exist_ok=True) # Criar a pasta na inicialização


MAX_POSTS_PER_PROFILE = 5 # Exemplo de constante

# Configuração do LLM (apenas um exemplo, ajuste conforme seu LLM)
# Certifique-se que GOOGLE_API_KEY está no seu .env
LLM = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)