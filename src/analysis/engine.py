# src/analysis/engine.py

import pandas as pd
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

# Pydantic Schemas
class Objetivos(BaseModel):
    client_name: str = Field(description="O nome de usuário da empresa cliente no instagram. [tarcisiogdf]")
    objetivo_principal: str = Field(description="O objetivo principal do cliente no modelo SMART (Específicos, Mensuráveis, Atingíveis, Relevantes e com Prazo definido). [Ex: Aumentar as vendas online em 15% através do Instagram nos próximos 6 meses.]")
    objetivo_secundario: List[str] = Field(description="objetivos secundários do cliente nas redes sociais. [Ex: Aumentar o número de seguidores qualificados em 20% no próximo trimestre\nAumentar a taxa de engajamento (curtidas, comentários, salvamentos) em 10% ao mês.]")
    
class Publico(BaseModel):
    idade: str = Field(description="A faixa de idade do principal publico-alvo do cliente. [Ex: 25-35 anos]")
    genero: str = Field(description="Gênero do principal publico-alvo do cliente (Preencha 'Ambos' quando for os dois). [Ex: Feminino]")
    localizacao: str = Field(description="Localização do principal publico-alvo do cliente.  [Ex: Principais capitais do Brasil]")
    ocupacao: str = Field(description="Ocupação do principal publico-alvo do cliente. [Ex: Dona de um pequeno negócio de artesanato]")
    renda: str = Field(description="A faixa da renda do principal publico-alvo do cliente. [Ex: R$ 4.000 - R$ 7.000]")
    interesses: List[str] = Field(description="Lista de Comportamentos e Interesses do publico-alvo do cliente. [Ex: Segue perfis de inspiração, DIY (Faça Você Mesmo) e dicas de negócios\nUsa o Instagram diariamente para descobrir novas marcas e produtos.]")
    dores: List[str] = Field(description="Lista de Dores e Necessidades do público-alvo do cliente. Ex: Sente dificuldade em organizar suas finanças como autônoma. Busca por materiais de alta qualidade para seus produtos. Precisa de dicas para otimizar seu tempo e ser mais produtiva.]")
    #competitor_usernames: List[str] = Field(description="Lista de nomes de usuário dos concorrentes.")

class PilaresConteudo(BaseModel):
    nome: str = Field(description="O nome do pilar de conteúdo, exemplo: 'Educacional'.")
    objetivo: str = Field(description="O objetivo do pilar, exemplo: 'Ensinar e informar'")
    exemplos: List[str] = Field(description="Lista de 3-5 exemplos de conteúdo. ['Tutoriais', 'Dicas rápidas']")

class VetorDePilares(BaseModel):
    """Um vetor (lista) contendo os pilares de conteúdo extraídos do briefing."""
    pilares: List[PilaresConteudo]

class ContentStrategyAnalysis(BaseModel):
    pilares: List[PilaresConteudo] = Field(description="Lista dos principais topicos de conteúdo abordados.")
    descricao: str = Field(description="Descrição dos Contéudos.")
    tom: str = Field(description="Descrição do tom de voz.")
    resumo: str = Field(description="Resumo da estratégia de conteúdo.")
    

# Funções de Análise de Conteúdo
def parse_objetivos(briefing_text: str) -> Objetivos:
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.4)

    structured_llm = llm.with_structured_output(Objetivos)
    prompt = f"""
              ## Contexto 
              Analise o briefing abaixo e extraia os objetivos do cliente. 
              
              ## Requisitos
              O Objetivo principal e cada um dos objetivos secundários devem conter ao menos: 1 métrica mensurável, alcançabilidade, Uma data. 
              Exemplos: 
              - Aumentar as vendas online em 15% através do Instagram nos próximos 6 meses. 
              - Aumentar o número de seguidores qualificados em 20% no próximo trimestre.
              - Aumentar a taxa de engajamento (curtidas, comentários, salvamentos) em 10% ao mês.
              - Gerar [Número] de leads qualificados por mês através de links na bio e stories.
              - Construir e fortalecer o reconhecimento da marca (brand awareness).
              
              ## Briefing:
              \n\"{briefing_text}\ """ 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_publicos(briefing_text: str) -> Publico:
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.4)

    structured_llm = llm.with_structured_output(Publico)
    prompt = f"Analise o briefing a seguir e extraia as informações necessárias sobre o principal público-alvo da empresa cliente. Briefing:\n\"{briefing_text}\"" 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_pilares(briefing_text: str) -> VetorDePilares:
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.6)

    structured_llm = llm.with_structured_output(VetorDePilares)
    prompt = f"""Analise o briefing a seguir e gere tópicos de conteúdo que a empresa cliente precisa falar no instagram para alcançar seus objetivos. 
                Retorne no mínimno 7 tópicos diferentes. 
                
                Briefing:\n\"{briefing_text}\" 
            """ 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_analyses(analyses: dict, objetivos: dict) -> VetorDePilares:
    #llm = ChatOpenAI(model="gpt-4.0-turbo", temperature=0) # ou outro modelo como gpt-4o
    #llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.6)

    structured_llm = llm.with_structured_output(VetorDePilares)
    prompt = f"""
                Analise as estratégias de conteúdo destes concorrentes da empresa cliente e gere 
                ideias de tópicos de conteúdo que ajudem o cliente a alcançar seus objetivos. 
                
                Objetivos em JSON:\n\"{objetivos}\"

                Analises em JSON:\n\"{analyses}\" 
            """ 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 


# Funções de Carregamento e Tratamento de
def load_profiles_to_df(path: str) -> pd.DataFrame:
    return pd.read_json(path) 

def load_posts_to_df(path: str) -> pd.DataFrame:
    df = pd.read_json(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['TOTAL ENGAJAMENTO'] = df['likesCount'] + df['commentsCount']
    return df 

def load_join_profiles_posts(original_posts_df: pd.DataFrame, original_profile_df: pd.DataFrame) -> pd.DataFrame:
        
    posts_df = original_posts_df.copy()
    profile_df = original_profile_df.copy()
    
    # Tratar Dados
    posts_df['data_hora'] = pd.to_datetime(posts_df['timestamp'])

    posts_df_gruped = posts_df.groupby(['ownerId', 'ownerUsername']).agg(
    commentsSum=('commentsCount', 'sum'),
    likesSum=('likesCount', 'sum'),
    minData=('data_hora', 'min'),
    maxData=('data_hora', 'max'),
    count=('ownerId', 'count')
    ).reset_index()

    df_profiles_posts = pd.merge(profile_df, posts_df_gruped, left_on='id', right_on='ownerId', how='left').drop(['ownerId'], axis=1)
    df_profiles_posts['TOTAL ENGAJAMENTO'] = (df_profiles_posts['commentsSum'] + df_profiles_posts['likesSum'])
    df_profiles_posts[r'% ENGAJAMENTO'] =  df_profiles_posts['TOTAL ENGAJAMENTO'] / df_profiles_posts['followersCount']
    df_profiles_posts['RECENCIA'] = 1 / ((df_profiles_posts['maxData'].max() - df_profiles_posts['maxData']).dt.days + 1)
    df_profiles_posts['FREQUENCIA'] = df_profiles_posts['count'] / ((df_profiles_posts['maxData'] - df_profiles_posts['minData']).dt.days + 1)
        
    return df_profiles_posts

def load_top_3_profiles(posts_df: pd.DataFrame, profile_df: pd.DataFrame) -> List[pd.DataFrame]:

    def filtro(usernames):
        return (posts_df['ownerUsername'] == usernames[0]) | (posts_df['ownerUsername'] == usernames[1]) | (posts_df['ownerUsername'] == usernames[2])

    posts_df = pd.read_json("data/raw/post_data.json")
    profile_df = pd.read_json("data/raw/profile_data.json")
        
    filtro = filtro(['tarcisiogdf', 'romeuzemaoficial', 'eduardoleite'])

    posts_df_top_3 = posts_df[filtro]

    posts_df_top_3_merged = pd.merge(posts_df_top_3, profile_df, how='left', left_on='ownerUsername', right_on='username')

    posts_df_top_3_grouped = posts_df_top_3_merged.groupby(['ownerUsername', 'type']).agg(
        countType=('type', 'count'),
        followersMax=('followersCount', 'max'),
        likesSum=('likesCount', 'sum'),
        commentsSum=('commentsCount', 'sum')
    ).reset_index()

    posts_df_top_3_grouped['ENGAJAMENTO TOTAL'] = posts_df_top_3_grouped['commentsSum'] + posts_df_top_3_grouped['likesSum']

    dados_pivot_count = posts_df_top_3_grouped.pivot(index='ownerUsername', columns='type', values='countType')
    dados_pivot_total = posts_df_top_3_grouped.pivot(index='ownerUsername', columns='type', values='ENGAJAMENTO TOTAL')

    dados_pivot_likes = posts_df_top_3_grouped.pivot(index='ownerUsername', columns='type', values='likesSum')
    dados_pivot_comments = posts_df_top_3_grouped.pivot(index='ownerUsername', columns='type', values='commentsSum')

    return [dados_pivot_count, dados_pivot_total, dados_pivot_likes, dados_pivot_comments]

def load_periodo_dias(posts_df: pd.DataFrame, profile_df: pd.DataFrame) -> List[pd.DataFrame]:

    posts_df = pd.read_json("data/raw/post_data.json")
    profile_df = pd.read_json("data/raw/profile_data.json")

    posts_df['DATA-HORA'] = pd.to_datetime(posts_df['timestamp'])
                
                # Usamos .dt.day_name() para obter o nome completo do dia da semana
    posts_df['DIA_DA_SEMANA'] = posts_df['DATA-HORA'].dt.day_name(locale='pt_BR')

    # --- Extraindo o Período do Dia ---
    # Vamos definir as faixas horárias para cada período
    def get_periodo_do_dia(hour):
        if 5 <= hour < 12:
            return 'Manhã'
        elif 12 <= hour < 18:
            return 'Tarde'
        elif 18 <= hour < 23:
            return 'Noite'
        else: # 23 to 5 (inclusive of 23, exclusive of 5)
            return 'Madrugada'

    # Aplicamos a função à hora de cada datetime
    # Primeiro, pegamos a hora, depois aplicamos a função
    posts_df['PERIODO_DO_DIA'] = posts_df['DATA-HORA'].dt.hour.apply(get_periodo_do_dia)

    periodo_df = posts_df.groupby(['PERIODO_DO_DIA']).size().sort_values(ascending=False)
    dias_df = posts_df.groupby(['DIA_DA_SEMANA']).size().sort_values(ascending=False)

    periodo_df = periodo_df.rename('Count')
    dias_df = dias_df.rename('Count')

    # Lista com a nova ordem desejada para as cidades
    ordem_periodos = ['Manhã', 'Tarde', 'Noite', 'Madrugada']
    ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    periodo_df = periodo_df.reindex(ordem_periodos)
    dias_df = dias_df.reindex(ordem_dias)
        
    return [periodo_df, dias_df] 

def load_pivot_periodo_dias(posts_df: pd.DataFrame, profile_df: pd.DataFrame) -> List[pd.DataFrame]:

    posts_df = pd.read_json("data/raw/post_data.json")
    profile_df = pd.read_json("data/raw/profile_data.json")

    # Converte a coluna 'timestamp' para o formato datetime
    posts_df['DATA-HORA'] = pd.to_datetime(posts_df['timestamp'])
                
    # Usamos .dt.day_name() para obter o nome completo do dia da semana em português
    posts_df['DIA_DA_SEMANA'] = posts_df['DATA-HORA'].dt.day_name(locale='pt_BR')

    # --- Extraindo o Período do Dia ---

    # Vamos definir as faixas horárias para cada período
    def get_periodo_do_dia(hour):
        """
        Retorna o período do dia (Manhã, Tarde, Noite, Madrugada)
        com base na hora fornecida (0-23).
        """
        if 5 <= hour < 12:
            return 'Manhã'
        elif 12 <= hour < 18:
            return 'Tarde'
        elif 18 <= hour < 23:
            return 'Noite'
        else:  # Horas da noite (23h) até antes do amanhecer (5h)
            return 'Madrugada'

    # Aplicamos a função à hora de cada datetime
    # Primeiro, extraímos a hora (.dt.hour), depois aplicamos a função
    posts_df['PERIODO_DO_DIA'] = posts_df['DATA-HORA'].dt.hour.apply(get_periodo_do_dia)

    # --- Agrupando os Dados ---

    # Agrupa e conta as postagens por período do dia
    periodo_df = posts_df.groupby(['PERIODO_DO_DIA', 'type']).size().sort_values(ascending=False).reset_index()

    # Agrupa e conta as postagens por dia da semana
    dias_df = posts_df.groupby(['DIA_DA_SEMANA', 'type']).size().sort_values(ascending=False).reset_index()

    # Cria uma tabela pivot com a contagem de tipos de postagem por usuário
    dados_pivot_periodos = periodo_df.pivot(index='PERIODO_DO_DIA', columns='type', values=0)

    # Cria uma tabela pivot com o engajamento total por tipo de postagem e usuário
    dados_pivot_dias = dias_df.pivot(index='DIA_DA_SEMANA', columns='type', values=0)

    # Lista com a nova ordem desejada para as cidades
    ordem_periodos = ['Manhã', 'Tarde', 'Noite', 'Madrugada']
    ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    periodo_df = dados_pivot_periodos.reindex(ordem_periodos)
    dias_df = dados_pivot_dias.reindex(ordem_dias)

    return [dados_pivot_periodos, dados_pivot_dias]

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
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.6)
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