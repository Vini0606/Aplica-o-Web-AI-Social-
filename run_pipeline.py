import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from config import settings
from src.data_ingestion import extractInstagram
from src.analysis import engine
from src.reporting import generator_report_concorrentes
from src.reporting import generator_report_estrategia
from src.reporting import generator_report_briefing
from src.reporting import generator_report_publicacoes
import json
import re # Import the re module for regular expressions

# Supondo que você crie um arquivo config/settings.py para constantes
# Ex: config/settings.py
# RAW_DATA_PATH = "data/raw"
# REPORTS_PATH = "reports"
# TEMPLATE_PATH = "templates/template.docx"
# MAX_POSTS_PER_PROFILE = 50

from fastapi import FastAPI
from dotenv import load_dotenv
import os
from config import settings # Certifique-se que config.py esteja configurado corretamente

    # Importar os routers das novas rotas da API
from api.v1.endpoints import brief_routes
from api.v1.endpoints import data_routes
from api.v1.endpoints import report_routes

def main():
    
    load_dotenv(override=True) # Carrega as variáveis de ambiente no início da aplicação
    
    print("Iniciando o processo de geração de relatório...") 
    load_dotenv(override=True)
    os.makedirs(settings.REPORTS_PATH, exist_ok=True)
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_PATH, exist_ok=True)
    llm = settings.LLM
    
    #user_briefing = generator_report_briefing.preencher_briefing(settings.BRIEFING_PATH)

    with open(settings.BRIEFING_PATH, 'r', encoding='utf-8') as f:
        user_briefing = f.read()   

    # 2. Analisar o briefing com LangChain
    print("Analisando o briefing...") 
    brief_data = {}
    
    brief_data['objetivos'] = engine.parse_objetivos(user_briefing, llm).model_dump()
    brief_data['publico'] = engine.parse_publicos(user_briefing, llm).model_dump()
    brief_data['pilares'] = engine.parse_pilares(user_briefing, llm, brief_data['objetivos'], brief_data['publico']).model_dump()["pilares"]
    brief_data['infoempresa'] = engine.parse_info_empresa(user_briefing, llm).model_dump()
    brief_data['posicionamento'] = engine.parse_posicionamento(objetivos=brief_data['objetivos'], publico=brief_data['publico'], llm=llm).model_dump() 
    
    print("Briefing Analisado com Sucesso!")

    with open(settings.BRIEFING_JSON_PATH, 'w', encoding='utf-8') as arquivo_json:
        json.dump(brief_data, arquivo_json)

    if not brief_data:
        print("Não foi possível analisar o briefing. Encerrando.") 
        return
    
    #extrairDadosGoogleSerpAPI(brief_data['infoempresa']['keywords'], brief_data['infoempresa']['localizacao'], settings.SEARCH_PATH)
    search_df = engine.load_search_to_df(settings.SEARCH_PATH)
    #extrairDadosApifyInstagram(list(search_df['url'].unique()), settings.PROFILE_PATH, settings.POST_PATH, settings.MAX_POSTS_PER_PROFILE) 
    
    profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH) 
    posts_df = engine.load_posts_to_df(settings.POST_PATH)
    profiles_posts_df = engine.load_join_profiles_posts(posts_df, profile_df)

    with open(settings.BRIEFING_JSON_PATH, 'w', encoding='utf-8') as arquivo_json:
        json.dump(brief_data, arquivo_json)
    
    objetivo_principal = [brief_data['objetivos']['objetivo_principal']]  # Coloca o objetivo principal em sua própria lista
    objetivos_secundarios = brief_data['objetivos']['objetivo_secundario'] # Pega a lista de secundários
    list_objetivos = objetivo_principal + objetivos_secundarios # Cria uma NOVA lista concatenando as duas
    
    # Gerar o calendário editorial com base nos dados já analisados
    print("Gerando sugestão de calendário editorial...")
    calendario_obj = engine.parse_calendario_editorial(
        pilares=brief_data['pilares'],
        objetivos=brief_data['objetivos'],
        publico=brief_data['publico'],
        llm=llm
    )
    if calendario_obj:
        brief_data['calendario'] = calendario_obj.model_dump()["calendario"]
    else:
        brief_data['calendario'] = [] # Garante que a chave exista
    print("Calendário gerado com sucesso!")     
    
    generator_report_estrategia.preencher_plano_marketing(
        brief_data,
        caminho_saida=settings.ESTRATEGIA_PATH,
        nome_empresa=brief_data['objetivos']['client_name'],
        responsavel="Equipe AI Social",
        objetivos=list_objetivos,
        persona={
            "Idade":  brief_data['publico']['idade'],
            "Gênero": brief_data['publico']['genero'],
            "Localização": brief_data['publico']['localizacao'],
            "Ocupação": brief_data['publico']['ocupacao'],
            "Interesses": brief_data['publico']['interesses'],
            "Dores": brief_data['publico']['dores']
        },
        pilares_conteudo=[pilar for pilar in brief_data['pilares']],
        posicionamento=brief_data['posicionamento'],
        calendario=brief_data.get('calendario', [])
    )
        
    dataframes = {}
    
    list_dfs_pivot = engine.load_top_3_profiles(posts_df, profile_df)
    list_dfs_periodo = engine.load_periodo_dias(posts_df, profile_df)
    list_dfs_pivot_periodo = engine.load_pivot_periodo_dias(posts_df, profile_df)
    dataframes['df_profiles_posts'] = profiles_posts_df
    dataframes['posts_df'] = posts_df
    dataframes['dados_pivot_count'] = list_dfs_pivot[0]
    dataframes['dados_pivot_total'] = list_dfs_pivot[1]
    dataframes['dados_pivot_likes'] =  list_dfs_pivot[2]
    dataframes['dados_pivot_comments'] = list_dfs_pivot[3]
    dataframes['periodo_df'] = list_dfs_periodo[0]
    dataframes['dias_df'] = list_dfs_periodo[1]
    dataframes['dados_pivot_periodos'] = list_dfs_pivot_periodo[0] 
    dataframes['dados_pivot_dias'] = list_dfs_pivot_periodo[1]
    
    generator_report_concorrentes.generate_full_report(
        llm,
        dataframes,
        client_name=brief_data['objetivos']['client_name'],
        output_path=settings.CONCORRENTES_PATH,
        template_path=settings.TEMPLATE_PATH,
    )
   
    generator_report_publicacoes.preencher_publicacoes(
    llm=llm,
    pilares=brief_data['pilares'],
    objetivos=brief_data['objetivos'],
    publico=brief_data['publico'],
    posicionamento=brief_data['posicionamento']
    )

if __name__ == "__main__":

    load_dotenv(override=True) # Carrega as variáveis de ambiente no início da aplicação
    
    print("Iniciando o processo de geração de relatório...") 
    load_dotenv(override=True)
    os.makedirs(settings.REPORTS_PATH, exist_ok=True)
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_PATH, exist_ok=True)
    llm = settings.LLM
     
    with open(settings.BRIEFING_JSON_PATH, 'r', encoding='utf-8') as arquivo_json:
        brief_data = json.load(arquivo_json)

    profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH) 
    posts_df = engine.load_posts_to_df(settings.POST_PATH)
    profiles_posts_df = engine.load_join_profiles_posts(posts_df, profile_df)

    dataframes = {}

    list_dfs_pivot = engine.load_top_3_profiles(posts_df, profile_df)
    list_dfs_periodo = engine.load_periodo_dias(posts_df, profile_df)
    list_dfs_pivot_periodo = engine.load_pivot_periodo_dias(posts_df, profile_df)
    dataframes['df_profiles_posts'] = profiles_posts_df
    dataframes['posts_df'] = posts_df
    dataframes['dados_pivot_count'] = list_dfs_pivot[0]
    dataframes['dados_pivot_total'] = list_dfs_pivot[1]
    dataframes['dados_pivot_likes'] =  list_dfs_pivot[2]
    dataframes['dados_pivot_comments'] = list_dfs_pivot[3]
    dataframes['periodo_df'] = list_dfs_periodo[0]
    dataframes['dias_df'] = list_dfs_periodo[1]
    dataframes['dados_pivot_periodos'] = list_dfs_pivot_periodo[0] 
    dataframes['dados_pivot_dias'] = list_dfs_pivot_periodo[1]

    generator_report_concorrentes.generate_full_report(
        llm,
        dataframes,
        client_name=brief_data['objetivos']['client_name'],
        output_path=settings.CONCORRENTES_PATH,
        template_path=settings.TEMPLATE_PATH,
    )    
    

