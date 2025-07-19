from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
import os
import json
import pandas as pd
from config import settings
from src.data_ingestion.extractInstagram import extrairDadosGoogleSerpAPI, extrairDadosApifyInstagram, extract_username_from_url, get_apify_client 
from src.analysis import engine
from auth.dependencies import get_current_active_user
from models import Usuario

router = APIRouter(tags=["Data Ingestion"])

@router.post("/data/extract/google-serp")
async def extract_google_serp_data(keywords: List[str] = Query(...), localizacao: str = Query(...), current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Extrai dados do Google SERP API com base em palavras-chave e localização.
    """
    # Você pode querer usar o current_user.id para nomear o arquivo de saída
    try:
        extrairDadosGoogleSerpAPI(keywords, localizacao, settings.SEARCH_PATH)
        
        return {"message": f"Dados do Google SERP extraídos e salvos em {settings.SEARCH_PATH}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao extrair dados do Google SERP: {str(e)}")

@router.post("/data/extract/instagram")
async def extract_instagram_data(current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Extrai dados de perfis e posts do Instagram via Apify.
    Requer que o briefing já tenha sido analisado e os dados do Google SERP coletados.
    """
    try:
        
        # Carrega os dados de busca para obter as URLs dos perfis
        search_df = engine.load_search_to_df(settings.SEARCH_PATH)
        all_profiles_to_scan = list(search_df['url'].unique())

        if not all_profiles_to_scan:
            raise HTTPException(status_code=400, detail="Nenhum perfil de Instagram encontrado nos dados de busca. Execute a extração do Google SERP primeiro.")

        extrairDadosApifyInstagram(
            all_profiles_to_scan,
            settings.PROFILE_PATH, # Passando o caminho específico do usuário
            settings.POST_PATH,    # Passando o caminho específico do usuário
            settings.MAX_POSTS_PER_PROFILE
        )

        return {"message": "Dados do Instagram extraídos e salvos com sucesso."}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Arquivos de briefing ({settings.BRIEFING_JSON_PATH}) ou busca ({settings.SEARCH_PATH}) não encontrados. Certifique-se de que as etapas anteriores foram executadas.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao extrair dados do Instagram: {str(e)}")