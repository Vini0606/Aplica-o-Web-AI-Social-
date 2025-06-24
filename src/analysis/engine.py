# src/analysis/engine.py

import pandas as pd
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

# Pydantic Schemas
class AnalysisBrief(BaseModel):
    client_name: str = Field(description="O nome da empresa cliente.")
    competitor_usernames: List[str] = Field(description="Lista de nomes de usuário dos concorrentes.")

class ContentStrategyAnalysis(BaseModel):
    content_pillars: List[str] = Field(description="Lista de 3-5 pilares de conteúdo.")
    tone_of_voice: str = Field(description="Descrição do tom de voz.")
    summary: str = Field(description="Resumo da estratégia de conteúdo.")

# Funções de Análise
def parse_briefing(briefing_text: str) -> AnalysisBrief:
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatOllama(model="llama3.2:latest", temperature=0)

    structured_llm = llm.with_structured_output(AnalysisBrief)
    prompt = f"Analise o briefing a seguir e extraia as informações necessárias. Briefing:\n\"{briefing_text}\"" 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def load_profiles_to_df(path: str) -> pd.DataFrame:
    return pd.read_json(path) 

def load_posts_to_df(path: str) -> pd.DataFrame:
    df = pd.read_json(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df 

def calculate_kpis(profile_df: pd.DataFrame, posts_df: pd.DataFrame) -> pd.DataFrame:
    
    post_metrics = posts_df.groupby('ownerUsername').agg(
        avg_likes=('likesCount', 'mean'),
        avg_comments=('commentsCount', 'mean'),
        total_posts=('id', 'count')
    ).reset_index() 
    
    merged_df = pd.merge(profile_df, post_metrics, left_on='username', right_on='ownerUsername', how='left') 
    
    merged_df['avg_engagement_rate'] = ((merged_df['avg_likes'] + merged_df['avg_comments']) / merged_df['followersCount']) * 100 
    
    kpi_df = merged_df[[
        'username', 'followersCount', 'followsCount', 'postsCount',
        'avg_likes', 'avg_comments', 'avg_engagement_rate'
    ]].copy() 
    
    kpi_df.columns = [
        'Perfil', 'Seguidores', 'Seguindo', 'Total de Posts',
        'Média de Curtidas', 'Média de Comentários', 'Taxa de Engajamento Média (%)'
    ]
    kpi_df = kpi_df.round(2) 
    return kpi_df 

def analyze_content_strategy_for_user(posts_df: pd.DataFrame, username: str) -> ContentStrategyAnalysis:
    user_posts = posts_df[posts_df['ownerUsername'] == username] 
    top_captions = user_posts.nlargest(10, 'likesCount')['caption'].dropna().tolist() 

    if not top_captions:
        return ContentStrategyAnalysis(content_pillars=[], tone_of_voice="N/A", summary="Dados insuficientes para análise.") 

    captions_text = "\n".join(f"- {c}" for c in top_captions) 
    
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatOllama(model="llama3.2:latest", temperature=0)
    structured_llm = llm.with_structured_output(ContentStrategyAnalysis) 

    prompt = f"""
    Persona: Você é um estrategista de marketing de mídias sociais sênior. 
    Contexto: Analise as seguintes legendas do perfil do Instagram '{username}':\n{captions_text} 
    Tarefa: Identifique os 3-5 principais pilares de conteúdo e descreva o tom de voz da marca. 
    Formato: Responda apenas com o objeto JSON. 
    """
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha na análise de conteúdo para {username}: {e}") 
        return ContentStrategyAnalysis(content_pillars=[], tone_of_voice="Erro na análise", summary="Erro na análise.")