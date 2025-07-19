import os
import json
from apify_client import ApifyClient
from apify_client._errors import ApifyClientError
import requests
from config import settings
import re 

def get_apify_client() -> ApifyClient:
    """Inicializa e retorna uma instância do cliente da Apify.""" 
    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        raise ValueError("Token da API da Apify não encontrado. Verifique seu arquivo .env.") 
    return ApifyClient(apify_token) 

def scrape_profile_data(client: ApifyClient, usernames: list[str]) -> dict:
    """Executa o Instagram Profile Scraper para uma lista de nomes de usuário com tratamento de erros.""" 
    print(f"Iniciando a extração de dados de perfil para: {usernames}") 
    try:
        actor = client.actor("apify/instagram-profile-scraper") 
        run_input = {"usernames": usernames} 
        run = actor.call(run_input=run_input) 
        print("Extração de dados de perfil concluida.") 
        return run 
    except ApifyClientError as e:
        print(f"Ocorreu um erro na API da Apify ao buscar perfis: {e.message}") 
        return None 

def scrape_post_data(client: ApifyClient, usernames: list[str], max_posts: int) -> dict:
    """Executa o Instagram Post Scraper com tratamento de erros.""" 
    print(f"Iniciando a extração de até {max_posts} posts para: {usernames} ") 
    try:
        actor = client.actor("apify/instagram-post-scraper") 
        run_input = {"username": usernames, "resultsLimit": max_posts} 
        run = actor.call(run_input=run_input) 
        print("Extração de posts concluída.") 
        return run 
    except ApifyClientError as e:
        print(f"Ocorreu um erro na API da Apify ao buscar posts: {e.message}") 
        return None 

def get_data_from_run(client: ApifyClient, run: dict, output_path: str) -> list:
    """Recupera os itens de um dataset de uma execução e salva em um arquivo JSON.""" 
    if not run:
        print("Execução inválida, não é possível buscar dados.") 
        return 
    
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        print("Nenhum dataset encontrado na execução.") 
        return 

    print(f"Recuperando dados do dataset: {dataset_id}") 
    try:
        dataset_items = client.dataset(dataset_id).list_items().items 
        os.makedirs(os.path.dirname(output_path), exist_ok=True) 
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset_items, f, ensure_ascii=False, indent=4) 
        print(f"Dados salvos em: {output_path}") 
        
        return dataset_items 
    except ApifyClientError as e:
        print(f"Erro ao buscar itens do dataset {dataset_id}: {e.message}") 
        return 
    
def extract_username_from_url(url: str) -> str | None:
    """Extracts the username from an Instagram URL."""
    match = re.search(r'instagram\.com/([a-zA-Z0-9_\.]+)/?.*', url)
    if match:
        # Exclude specific paths that are not usernames
        excluded_paths = ['tv', 'explore', 'reels', 'p', 'locations']
        username = match.group(1)
        if username not in excluded_paths:
            return username
    return None

def extrairDadosGoogleSerpAPI(keywords: list, localizacao: str, output_path: str) -> dict:

    parte_keywords = " OR ".join([f'"{kw}"' for kw in keywords])
        
    # Monta a consulta final
    query_completa = f"({parte_keywords}) AND {localizacao} site:instagram.com// -reel -p -locations -explore"

    url = "https://app.zenserp.com/api/v2/search"
    headers = {
        "apikey": os.getenv("ZENSERP_API_KEY")
    }
    params = {
        "q": query_completa,
        "search_engine": "google.com",
        'num': 100,
    }

    try:
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        with open(output_path, 'w', encoding='utf-8') as arquivo_json:
            json.dump(data, arquivo_json)
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def extrairDadosApifyInstagram(all_profiles_to_scan, profile_output, post_output, MAX_POSTS_PER_PROFILE):

    # 3. Ingestão de Dados via Apify
    print("\nIniciando a ingestão de dados da Apify...") 
    apify_client = get_apify_client()

    profile_usernames = [extract_username_from_url(url) for url in all_profiles_to_scan]
    # Filter out None values and ensure uniqueness
    profile_usernames = list(set([u for u in profile_usernames if u]))

    profile_run = scrape_profile_data(apify_client, all_profiles_to_scan) 
    profile_data = get_data_from_run(apify_client, profile_run, settings.PROFILE_PATH) 
    
    post_run = scrape_post_data(apify_client, profile_usernames, max_posts=MAX_POSTS_PER_PROFILE) 
    post_data = get_data_from_run(apify_client, post_run, settings.POST_PATH)

    
    if not profile_data or not post_data:
        print("Falha na coleta de dados da Apify. Encerrando.") 
        return
    else:
        
        with open(profile_output, 'w', encoding='utf-8') as arquivo_json:
            json.dump(profile_data, arquivo_json)
        
        with open(post_output, 'w', encoding='utf-8') as arquivo_json:
            json.dump(post_data, arquivo_json)
        
        return profile_data, post_data
