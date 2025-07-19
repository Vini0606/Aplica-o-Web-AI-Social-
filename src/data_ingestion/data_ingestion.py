# src/data_ingestion.py

import os
import requests
import json
import re
from apify_client import ApifyClient # Importar apify-client se você estiver usando diretamente aqui
from config import settings # Para acessar APIFY_API_TOKEN, MAX_POSTS_PER_PROFILE

def get_apify_client():
    # Lógica para inicializar o cliente Apify (pode precisar de uma chave de API do .env)
    return ApifyClient(os.getenv("APIFY_API_TOKEN")) # Exemplo

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
        response.raise_for_status()
        data = response.json()

        with open(output_path, 'w', encoding='utf-8') as arquivo_json:
            json.dump(data, arquivo_json)
        return data # Retornar os dados também
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise # Re-lançar a exceção para que o FastAPI possa capturá-la

def extrairDadosApifyInstagram(all_profiles_to_scan, profile_output, post_output, MAX_POSTS_PER_PROFILE):
    print("\nIniciando a ingestão de dados da Apify...")
    apify_client = get_apify_client()

    profile_usernames = [extract_username_from_url(url) for url in all_profiles_to_scan]
    profile_usernames = list(set([u for u in profile_usernames if u]))

    # Supondo que 'extractInstagram' seja um módulo ou que você tenha métodos correspondentes aqui
    # Este trecho assume que você tem uma lógica similar ao que estava no main.py original
    # e que 'extractInstagram' é um placeholder para essas funções.
    # Exemplo: Se scrape_profile_data e get_data_from_run estão aqui, use:
    # profile_run = scrape_profile_data(apify_client, all_profiles_to_scan)
    # profile_data = get_data_from_run(apify_client, profile_run, profile_output)

    # Para simular o uso do ApifyClient diretamente, você teria que chamar as APIs do Apify:
    # Este é um placeholder, adapte ao seu uso real da Apify Client
    # client_run = apify_client.actor("apify/instagram-profile-scraper").call(
    #    {"usernames": profile_usernames},
    #    contentType="application/json"
    # )
    # profile_data = list(apify_client.dataset(client_run["defaultDatasetId"]).iterate_items())
    # with open(profile_output, 'w', encoding='utf-8') as f: json.dump(profile_data, f)

    # client_run_posts = apify_client.actor("apify/instagram-post-scraper").call(
    #    {"urls": all_profiles_to_scan, "resultsLimit": MAX_POSTS_PER_PROFILE},
    #    contentType="application/json"
    # )
    # post_data = list(apify_client.dataset(client_run_posts["defaultDatasetId"]).iterate_items())
    # with open(post_output, 'w', encoding='utf-8') as f: json.dump(post_data, f)

    # placeholder para a lógica de Apify
    profile_data = [{"username": u, "followers": 1000} for u in profile_usernames] if profile_usernames else []
    post_data = [{"post_id": i, "likes": 50} for i in range(MAX_POSTS_PER_PROFILE)] if profile_usernames else []

    if not profile_data or not post_data:
        print("Falha na coleta de dados da Apify. Encerrando.")
        return None, None
    else:
        with open(profile_output, 'w', encoding='utf-8') as arquivo_json:
            json.dump(profile_data, arquivo_json)
        with open(post_output, 'w', encoding='utf-8') as arquivo_json:
            json.dump(post_data, arquivo_json)
        return profile_data, post_data