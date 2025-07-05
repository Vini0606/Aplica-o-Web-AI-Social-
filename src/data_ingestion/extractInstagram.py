# src/data_ingestion/apify_handler.py

import os
import json
from apify_client import ApifyClient
from apify_client._errors import ApifyClientError 

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