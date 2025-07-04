# main.py

import os
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

# Supondo que você crie um arquivo config/settings.py para constantes
# Ex: config/settings.py
# RAW_DATA_PATH = "data/raw"
# REPORTS_PATH = "reports"
# TEMPLATE_PATH = "templates/template.docx"
# MAX_POSTS_PER_PROFILE = 50

def extrairDadosApifyInstagram(all_profiles_to_scan):

    # 3. Ingestão de Dados via Apify
    print("\nIniciando a ingestão de dados da Apify...") 
    apify_client = extractInstagram.get_apify_client()
    
    MAX_POSTS_PER_PROFILE = 50

    profile_run = extractInstagram.scrape_profile_data(apify_client, all_profiles_to_scan) 
    profile_data = extractInstagram.get_data_from_run(apify_client, profile_run, settings.PROFILE_PATH) 
    
    post_run = extractInstagram.scrape_post_data(apify_client, all_profiles_to_scan, max_posts=MAX_POSTS_PER_PROFILE) 
    post_data = extractInstagram.get_data_from_run(apify_client, post_run, settings.POST_PATH)

    
    if not profile_data or not post_data:
        print("Falha na coleta de dados da Apify. Encerrando.") 
        return
    else:
        return profile_data, post_data

def main():
    
    print("Iniciando o processo de geração de relatório...") 
    load_dotenv(override=True)
    os.makedirs(settings.REPORTS_PATH, exist_ok=True)
    os.makedirs(settings.REPORTS_PATH, exist_ok=True)
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True)
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True) 
    os.makedirs(settings.PROCESSED_DATA_PATH, exist_ok=True)
    llm = settings.LLM 
    
    #user_briefing = generator_report_briefing.preencher_briefing()
    
    with open(settings.BRIEFING_PATH, "r", encoding="utf-8") as f:
        user_briefing = f.read()    

    # 2. Analisar o briefing com LangChain
    print("Analisando o briefing...") 
    brief_data = {}
    brief_data['objetivos'] = engine.parse_objetivos(user_briefing).model_dump()
    brief_data['publico'] = engine.parse_publicos(user_briefing).model_dump()
    brief_data['pilares'] = engine.parse_pilares(user_briefing).model_dump()["pilares"]
    print("Briefing Analisado com Sucesso!")

    if not brief_data:
        print("Não foi possível analisar o briefing. Encerrando.") 
        return
    
    profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH) 
    posts_df = engine.load_posts_to_df(settings.POST_PATH)
    profiles_posts_df = engine.load_join_profiles_posts(posts_df, profile_df)

    """ 
    
    #extrairDadosApifyInstagram(all_profiles_to_scan)

    profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH) 
    posts_df = engine.load_posts_to_df(settings.POST_PATH)
    profiles_posts_df = engine.load_join_profiles_posts(posts_df, profile_df)
    all_profiles_to_scan = list(profiles_posts_df.sort_values(by='TOTAL ENGAJAMENTO', ascending=False).head(10).reset_index()["ownerUsername"].unique())
    
    print("Analisando o conteúdo dos Concorrentes...") 
    content_analysis_results = {}
    for username in all_profiles_to_scan:
        print(f"Analisando concorrentes: {username}...") 
        analysis = engine.analyze_content_strategy_for_user(posts_df, username).model_dump() 
        content_analysis_results[username] = analysis 
    print("Concorrentes Analisados com Sucesso!")
    
    # main.py - Correção Definitiva
    vetor_pilares_obj = engine.parse_analyses(content_analysis_results, brief_data['objetivos'])

    # Verificamos se o objeto não é nulo e depois acessamos o atributo .pilares
    if vetor_pilares_obj and vetor_pilares_obj.pilares:
        for pilar in vetor_pilares_obj.pilares:
            # Agora 'pilar' é um objeto PilaresConteudo e o .model_dump() funcionará
            brief_data['pilares'].append(pilar.model_dump())
     
    
    print("Estratégia Produzida com Sucesso!")
    print(end='\n\n')
    print('Cliente: ', brief_data['objetivos']['client_name'], end='\n')
    print('Objetivo: ', brief_data['objetivos']['objetivo_principal'], end='\n')
    print('Objetivo Secundário: ', brief_data['objetivos']['objetivo_secundario'], end='\n')
    print('Idade do Público: ', brief_data['publico']['idade'], end='\n')
    print('Genêro do Público', brief_data['publico']['genero'], end='\n')
    print('Localização do Publico: ', brief_data['publico']['localizacao'], end='\n')
    print('Ocupação do Publico: ', brief_data['publico']['ocupacao'], end='\n')
    print('Renda do Publico: ', brief_data['publico']['renda'], end='\n')
    print('Interesses do Publico', brief_data['publico']['interesses'], end='\n')
    print('Qtd de Pilares de Conteúdo: ', len(brief_data['pilares']), end='\n') 
    print('Pilar de Conteúdo 1: ', brief_data['pilares'][0], end='\n')
    print('Dores: ', brief_data['publico']['dores'], end='\n')
    print(end='\n\n')
    
    with open(settings.BRIEFING_JSON_PATH, 'w', encoding='utf-8') as arquivo_json:
        json.dump(brief_data, arquivo_json)
    
    objetivo_principal = [brief_data['objetivos']['objetivo_principal']]  # Coloca o objetivo principal em sua própria lista
    objetivos_secundarios = brief_data['objetivos']['objetivo_secundario'] # Pega a lista de secundários
    list_objetivos = objetivo_principal + objetivos_secundarios # Cria uma NOVA lista concatenando as duas
    
    generator_report_estrategia.preencher_plano_marketing(
        brief_data,
        caminho_saida=settings.ESTRATEGIA_PATH,
        nome_empresa=brief_data['objetivos']['client_name'],
        responsavel="Equipe AI Social",
        objetivos=list_objetivos,
        persona={
            "Nome": "",
            "Idade":  brief_data['publico']['idade'],
            "Gênero": brief_data['publico']['genero'],
            "Localização": brief_data['publico']['localizacao'],
            "Ocupação": brief_data['publico']['ocupacao'],
            "Interesses": brief_data['publico']['interesses'],
            "Dores": brief_data['publico']['dores']
        },
        pilares_conteudo=[pilar for pilar in brief_data['pilares']]
    )  
    
    generator_report_publicacoes.preencher_publicacoes(brief_data['pilares'])

    """ 
    
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
   
if __name__ == "__main__":
    main()