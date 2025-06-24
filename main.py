# main.py

import os
from datetime import datetime
from dotenv import load_dotenv
#from src.data_ingestion import apify_handler
from src.analysis import engine
from src.reporting import generator

# Supondo que você crie um arquivo config/settings.py para constantes
# Ex: config/settings.py
# RAW_DATA_PATH = "data/raw"
# REPORTS_PATH = "reports"
# TEMPLATE_PATH = "templates/template.docx"
# MAX_POSTS_PER_PROFILE = 50

def main():
    
    """Função principal que orquestra o fluxo completo de geração do relatório de análise de concorrentes.""" 
    print("Iniciando o processo de geração de relatório...") 
    load_dotenv() 

    # 1. Obter o briefing do usuário
    user_briefing = """
    Por favor, prepare um relatório de análise de concorrentes para o meu cliente, jeronimorodriguesba. 
    Quero uma análise detalhada dos principais concorrentes no Instagram: 'ronaldocaiado', 'romeuzemaoficial' e 'tarcisiogdf'. 
    """

    # 2. Analisar o briefing com LangChain
    print("Analisando o briefing...") 
    brief_data = engine.parse_briefing(user_briefing) 
    if not brief_data:
        print("Não foi possível analisar o briefing. Encerrando.") 
        return 

    client_name = brief_data.client_name
    competitor_usernames = brief_data.competitor_usernames
    # O nome do cliente é difícil de extrair como username, simplificando aqui
    all_profiles_to_scan = competitor_usernames + [client_name.lower().replace(' ', '')]
    print(f"Cliente: {client_name}") 
    print(f"Concorrentes a serem analisados: {competitor_usernames}")  

    # Supondo que os diretórios existem
    RAW_DATA_PATH = "data/raw"
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    
    profile_data_path = os.path.join(RAW_DATA_PATH, "profile_data.json")
    post_data_path = os.path.join(RAW_DATA_PATH, "post_data.json")

    """ 

    # 3. Ingestão de Dados via Apify
    print("\nIniciando a ingestão de dados da Apify...") 
    apify_client = apify_handler.get_apify_client()
    
    MAX_POSTS_PER_PROFILE = 50

    profile_run = apify_handler.scrape_profile_data(apify_client, all_profiles_to_scan) 
    profile_data = apify_handler.get_data_from_run(apify_client, profile_run, profile_data_path) 
    
    post_run = apify_handler.scrape_post_data(apify_client, all_profiles_to_scan, max_posts=MAX_POSTS_PER_PROFILE) 
    post_data = apify_handler.get_data_from_run(apify_client, post_run, post_data_path) 
    
    if not profile_data or not post_data:
        print("Falha na coleta de dados da Apify. Encerrando.") 
        return 

    """
    
    # 4. Análise dos Dados
    print("\nIniciando a análise dos dados...") 
    profile_df = engine.load_profiles_to_df(profile_data_path) 
    posts_df = engine.load_posts_to_df(post_data_path) 
    kpi_df = engine.calculate_kpis(profile_df, posts_df) 
    print("KPIs calculados:") 
    print(kpi_df) 

    content_analysis_results = {}
    for username in all_profiles_to_scan:
        print(f"Analisando estratégia de conteúdo para: {username}") 
        analysis = engine.analyze_content_strategy_for_user(posts_df, username) 
        content_analysis_results[username] = analysis 
        
    # 5. Geração do Relatório
    print("\nIniciando a geração do relatório .docx...") 
    REPORTS_PATH = "reports"
    os.makedirs(REPORTS_PATH, exist_ok=True)
    TEMPLATE_PATH = "templates/template.docx"

    report_filename = f"Relatorio_Concorrentes_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
    report_path = os.path.join(REPORTS_PATH, report_filename) 
    
    generator.generate_full_report(
        client_name=client_name,
        kpi_df=kpi_df,
        content_analysis=content_analysis_results,
        output_path=report_path,
        template_path=TEMPLATE_PATH
    ) 
    print(f"\nRelatório gerado com sucesso em: {report_path}") 

if __name__ == "__main__":
    main()