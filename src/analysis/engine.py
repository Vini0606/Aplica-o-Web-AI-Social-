# src/analysis/engine.py

import pandas as pd
import json
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

# ================
# Pydantic Schemas
# ================

class InfoEmpresa(BaseModel):
    nome_empresa: str = Field(description="O nome da empresa do cliente no instagram.")
    keywords: List[str] = Field(description="Palavras-chave utilizadas pelos concorrentes do cliente, na biografia do instagram. Exemplo: pizzaria, restaurante, lanchonete")
    localizacao: str = Field(description="Endereço completo da empresa.")
    bairros: List[str] = Field(description="Bairros muito próximos, ou pertencentes, da localização da empresa")

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

class Posicionamento(BaseModel):
    """Define o posicionamento estratégico e o tom de voz da marca."""
    tom_de_voz: str = Field(description="Adjetivos que descrevem como a marca deve se comunicar. Ex: 'Amigável, especialista e inspirador'.")
    arquetipo: str = Field(description="O arquétipo de marca que melhor representa a empresa. Ex: 'O Sábio', 'O Explorador', 'O Cuidador'.")
    diferenciais: List[str] = Field(description="Uma lista dos 2-3 principais pontos que tornam a marca única em relação à concorrência.")
    proposta_de_valor: str = Field(description="Uma frase curta que resume o principal benefício que o cliente recebe. Ex: 'Ajudamos criativos a transformarem paixão em negócio com ferramentas e inspiração'.")
    resumo_posicionamento: str = Field(description="Um parágrafo único que resume todo o posicionamento da marca, ideal para ser usado em briefings e guias de estilo.")

# ==============================
# Funções de Análise de Conteúdo
# ==============================

def parse_objetivos(briefing_text: str, llm: BaseChatModel) -> Objetivos:

    structured_llm = llm.with_structured_output(Objetivos)
    prompt = f"""
            ## Persona
            Você é um consultor de marketing digital especializado em definir metas estratégicas para redes sociais. Sua principal habilidade é traduzir as necessidades de um cliente em objetivos SMART (Específicos, Mensuráveis, Atingíveis, Relevantes e com Prazo definido).

            ## Contexto
            Você recebeu o seguinte briefing de um novo cliente. Sua tarefa é analisar este texto e extrair os objetivos de negócio e de marketing dele.

            ## Tarefa
            Extraia o objetivo principal e os objetivos secundários do cliente. Siga estritamente as seguintes regras:
            1.  **Objetivo Principal:** Deve ser a meta de negócio mais importante. Se o cliente mencionar vendas ou crescimento, priorize isso.
            2.  **Objetivos Secundários:** Devem ser metas de marketing que suportam o objetivo principal (ex: engajamento, crescimento de seguidores, geração de leads).
            3.  **Formato SMART:** Cada objetivo, tanto o principal quanto os secundários, DEVE ser reescrito para conter:
                - **Métrica clara:** Um número ou percentual (ex: "aumentar em 15%", "gerar 50 leads").
                - **Prazo definido:** Um período de tempo (ex: "nos próximos 3 meses", "até o final do ano").
            4.  **Inferência:** Se o cliente não fornecer um número ou prazo exato, infira um valor razoável com base no contexto do briefing (ex: se ele quer "crescer", defina como "crescer 10% em 2 meses"). Não deixe esses campos em branco.
            5.  **Objetividade:** Os objetivos devem ser o mais objetivos e concisos possível.

            
            ## Briefing do Cliente:
            \n\"{briefing_text}\"
            """ 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_info_empresa(briefing_text: str, llm: BaseChatModel) -> InfoEmpresa:

    structured_llm = llm.with_structured_output(InfoEmpresa)
    prompt = f"""
            ## Persona
            Você é um assistente de pesquisa com excelente atenção aos detalhes, especializado em extrair informações de perfis de negócios.

            ## Contexto
            Você está analisando o briefing de um cliente para preencher a ficha cadastral da empresa dele.

            ## Tarefa
            Analise o briefing abaixo e extraia as informações da empresa cliente, seguindo estas diretrizes para cada campo:
            - **nome_empresa:** O nome comercial da empresa.
            - **keywords:** Pense no tipo de negócio (pizzaria, consultório, etc.) e em termos relacionados que os concorrentes usariam na bio do Instagram. Extraia do texto ou sugira com base no negócio.
            - **localizacao:** Extraia o endereço mais completo possível. Se apenas a cidade ou bairro for mencionado, extraia isso.
            - **bairros:** Liste os bairros exatos mencionados. Se nenhum for mencionado, liste bairros conhecidos que pertencem à `localizacao` extraída.

            ## Briefing:
            \n\"{briefing_text}\"
            """ 
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_publicos(briefing_text: str, llm: BaseChatModel) -> Publico:

    structured_llm = llm.with_structured_output(Publico)

    prompt = f"""
            ## Persona
            Você é um analista de pesquisa de mercado especializado em criar "personas" de clientes. Seu objetivo é construir um perfil detalhado do público-alvo principal de uma empresa.

            ## Contexto
            Você está analisando o briefing de um cliente para definir o perfil do consumidor ideal para as campanhas de marketing.

            ## Tarefa
            Analise o briefing a seguir e extraia as informações sobre o principal público-alvo. Para cada campo, siga as instruções:
            - **Se a informação não estiver explícita no texto, use o contexto geral do briefing para inferir a resposta mais provável.**
            - **Se for impossível inferir, preencha o campo com a string "Não especificado".**
            - **idade:** Uma faixa etária (ex: 25-35 anos).
            - **genero:** Masculino, Feminino ou Ambos.
            - **localizacao:** Onde esse público mora ou frequenta (ex: Mesmo bairro da empresa, Capitais do Brasil).
            - **ocupacao:** Profissão ou estilo de vida (ex: Universitários, Empreendedores, Donas de casa).
            - **renda:** Faixa de renda mensal (ex: R$ 3.000 - R$ 5.000).
            - **interesses:** Hobbies, comportamentos e tipos de conteúdo que consomem.
            - **dores:** Os problemas, desafios e necessidades que o produto/serviço do cliente resolve para esse público. Pense "o que tira o sono dessa pessoa?".

            ## Briefing:
            \n\"{briefing_text}\"
            """

    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return Publico 

def parse_pilares(briefing_text: str, llm: BaseChatModel, objetivos: dict, publico: dict) -> VetorDePilares:

    structured_llm = llm.with_structured_output(VetorDePilares)
    objetivos_dict = objetivos
    publico_dict = publico

    prompt = f"""
            ## Persona
            Você é um estrategista de conteúdo sênior para mídias sociais. Sua especialidade é criar linhas editoriais de conteúdo que geram resultados de negócio.

            ## Contexto
            Você precisa definir as linhas editoriais, ou pilares de conteúdo, para a estratégia de marketing de conteúdo de um novo cliente no instagram. Você já tem em mãos os objetivos e a definição do público-alvo. O briefing geral também está disponível para contexto adicional.

            ## Informações Estratégicas
            - **Objetivos do Cliente:** {json.dumps(objetivos_dict, indent=2, ensure_ascii=False)}
            - **Público-Alvo:** {json.dumps(publico_dict, indent=2, ensure_ascii=False)}

            ## Tarefa
            Com base nos objetivos e no público-alvo fornecidos, crie 5 a 7 pilares de conteúdo para o Instagram do cliente. Para cada pilar, siga estritamente a estrutura:
            1.  **Nome:** Um nome curto e descritivo para o pilar (ex: "Educacional", "Bastidores", "Prova Social").
            2.  **Objetivo:** Explique como este pilar ajuda a alcançar um dos objetivos do cliente E/OU resolve uma das 'dores' do público-alvo.
            3.  **Exemplos:** Forneça de 3 a 5 exemplos de posts concretos (ideias de Reels, Carrossel, Stories) para este pilar.

            ## Briefing (para contexto adicional):
            \n\"{briefing_text}\"
            """
    
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao analisar o briefing: {e}") 
        return None 

def parse_analyses(analyses: dict, objetivos: dict, llm: BaseChatModel) -> VetorDePilares:

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

def parse_posicionamento(objetivos: dict, publico: dict, llm: BaseChatModel) -> Posicionamento:
    """
    Sintetiza um posicionamento de marca estratégico com base nos objetivos e no público-alvo definidos.
    """
    structured_llm = llm.with_structured_output(Posicionamento)

    objetivos_dump = objetivos
    publico_dump = publico

    prompt = f"""
        ## Persona
        Você é um estrategista de marca (Brand Strategist) sênior, especialista em criar identidades de marca fortes e coerentes.

        ## Contexto
        Você foi contratado para definir o posicionamento estratégico de uma marca no Instagram. Você já tem acesso às informações mais cruciais: os objetivos de negócio e o perfil detalhado do público-alvo. Sua tarefa não é extrair, mas sim CRIAR o posicionamento a partir desses dados.

        ## Informações Estratégicas Fornecidas
        
        ### Objetivos do Cliente:
        {json.dumps(objetivos_dump, indent=2, ensure_ascii=False)}

        ### Perfil do Público-Alvo:
        {json.dumps(publico_dump, indent=2, ensure_ascii=False)}

        ## Tarefa
        Com base EXCLUSIVAMENTE nos objetivos e no público-alvo acima, desenvolva o posicionamento da marca. Seja criativo, estratégico e conecte os pontos. É obrigatório preencher todos os campos do schema:
        1.  **tom_de_voz:** Defina o tom de voz com 3 a 4 adjetivos que descrevem como a marca deve se comunicar para ressoar com o público e atingir seus objetivos. Ex: 'Amigável, especialista, inspirador'.
        2.  **arquetipo:** Qual arquétipo de marca (ex: O Sábio, O Herói, O Mago) se alinha melhor com a missão de resolver as 'dores' do público?
        3.  **diferenciais:** Quais são os 2-3 pontos únicos que a marca pode alegar, considerando o que o público valoriza?
        4.  **proposta_de_valor:** Crie uma frase de impacto que comunique diretamente como a marca resolve o principal problema do público.
        5.  **resumo_posicionamento:** Junte tudo em um parágrafo coeso e responda a pergunta esta pergunta em detalhes: como a empresa cliente quer ser percebida no instagram? Comece o resumo com "A 'nome_empresa' quer ser percebida no instagram como..."
        """
    
    try:
        return structured_llm.invoke(prompt) 
    except Exception as e:
        print(f"Falha ao gerar o posicionamento estratégico: {e}") 
        return None

# =====================================
# Funções Tratamento e Análise de Dados
# =====================================

def load_profiles_to_df(path: str) -> pd.DataFrame:
    return pd.read_json(path) 

def load_posts_to_df(path: str) -> pd.DataFrame:
    df = pd.read_json(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['TOTAL ENGAJAMENTO'] = df['likesCount'] + df['commentsCount']
    return df 

def load_search_to_df(path: str) -> pd.DataFrame:
    try:
        # Lê todo o conteúdo do arquivo
        with open(path, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Tenta analisar todo o conteúdo como um único objeto JSON
        data = json.loads(file_content)

        # Converte para DataFrame usando json_normalize
        # Removendo o argumento 'meta' para incluir apenas os dados de 'organic'
        search_df = pd.json_normalize(
            data,
            record_path=['organic']
            # meta=[] # Não é necessário, pois estamos removendo o 'meta'
            # errors='ignore' # Não é mais necessário, pois não há chaves 'meta' para ignorar
        )

        return search_df

    except json.JSONDecodeError as e:
        print(f"Falha ao decodificar JSON do '{path}': {e}")
        print("Isso indica que o arquivo contém sintaxe JSON inválida ou não é um único objeto JSON válido.")
        print("Por favor, inspecione o conteúdo do arquivo diretamente em busca de erros.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

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
    """
    Identifica os 3 melhores perfis com base no número de seguidores
    e retorna DataFrames pivotados para análise.
    """
    # --- CORREÇÃO ---
    # 1. REMOVIDAS as linhas que liam os arquivos .json novamente.
    #    Agora a função usa os DataFrames passados como argumentos.

    # 2. O filtro agora é dinâmico. Ele pega os 3 perfis com mais seguidores.
    #    Você pode mudar 'followersCount' para outra métrica se preferir (ex: 'TOTAL ENGAJAMENTO').
    top_3_usernames = profile_df.nlargest(3, 'followersCount')['username'].tolist()
    
    # Garante que temos exatamente 3 nomes de usuário, caso contrário, retorna DataFrames vazios para evitar erros.
    if len(top_3_usernames) < 3:
        print("Aviso: Não foram encontrados 3 perfis para analisar. Retornando DataFrames vazios.")
        empty_df = pd.DataFrame()
        return [empty_df, empty_df, empty_df, empty_df]

    # Filtra os posts para incluir apenas os dos top 3 perfis
    posts_df_top_3 = posts_df[posts_df['ownerUsername'].isin(top_3_usernames)].copy()

    # O resto da lógica da função permanece o mesmo
    posts_df_top_3_merged = pd.merge(posts_df_top_3, profile_df, how='left', left_on='ownerUsername', right_on='username')

    posts_df_top_3_grouped = posts_df_top_3_merged.groupby(['ownerUsername', 'type']).agg(
        countType=('type', 'count'),
        followersMax=('followersCount', 'max'),
        likesSum=('likesCount', 'sum'),
        commentsSum=('commentsCount', 'sum')
    ).reset_index()

    posts_df_top_3_grouped['ENGAJAMENTO TOTAL'] = posts_df_top_3_grouped['commentsSum'] + posts_df_top_3_grouped['likesSum']

    # Preenche com 0 para evitar erros na pivotação se algum tipo de post estiver faltando
    dados_pivot_count = posts_df_top_3_grouped.pivot_table(index='ownerUsername', columns='type', values='countType', fill_value=0)
    dados_pivot_total = posts_df_top_3_grouped.pivot_table(index='ownerUsername', columns='type', values='ENGAJAMENTO TOTAL', fill_value=0)
    dados_pivot_likes = posts_df_top_3_grouped.pivot_table(index='ownerUsername', columns='type', values='likesSum', fill_value=0)
    dados_pivot_comments = posts_df_top_3_grouped.pivot_table(index='ownerUsername', columns='type', values='commentsSum', fill_value=0)

    return [dados_pivot_count, dados_pivot_total, dados_pivot_likes, dados_pivot_comments]

def load_periodo_dias(posts_df: pd.DataFrame, profile_df: pd.DataFrame) -> List[pd.DataFrame]:

    # 1. Garante que a coluna de data está no formato correto
    posts_df['DATA-HORA'] = pd.to_datetime(posts_df['timestamp'])
                
    # 2. Extrai o nome do dia da semana em português
    posts_df['DIA_DA_SEMANA'] = posts_df['DATA-HORA'].dt.day_name(locale='pt_BR.UTF-8')
    
    # 3. Extrai o período do dia (Manhã, Tarde, etc.)
    def get_periodo_do_dia(hour):
        if 5 <= hour < 12:
            return 'Manhã'
        elif 12 <= hour < 18:
            return 'Tarde'
        elif 18 <= hour < 23:
            return 'Noite'
        else:
            return 'Madrugada'
    posts_df['PERIODO_DO_DIA'] = posts_df['DATA-HORA'].dt.hour.apply(get_periodo_do_dia)

    # 4. Conta as ocorrências usando .value_counts()
    periodo_df = posts_df['PERIODO_DO_DIA'].value_counts()
    dias_df = posts_df['DIA_DA_SEMANA'].value_counts()
    dias_df.rename(index={'Terça-feira': 'Terca-feira', 'Sábado': 'Sabado'})

    # Renomeia a série (opcional, mas bom para clareza)
    periodo_df = periodo_df.rename('Count')
    dias_df = dias_df.rename('Count')

    # 6. Define a ordem correta para os eixos do gráfico
    ordem_periodos = ['Manhã', 'Tarde', 'Noite', 'Madrugada']
    ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']

    # 7. Reordena, preenche os dias sem dados com 0 e converte para número inteiro
    # Esta lógica continua a mesma e funciona perfeitamente com a saída do .value_counts()
    periodo_df = periodo_df.reindex(ordem_periodos).fillna(0).astype(int)
    dias_df = dias_df.reindex(ordem_dias).fillna(0).astype(int)
    
    # --- FIM DA CORREÇÃO ---
    
    return [periodo_df, dias_df]

def load_pivot_periodo_dias(posts_df: pd.DataFrame, profile_df: pd.DataFrame) -> List[pd.DataFrame]:

    # Converte a coluna 'timestamp' para o formato datetime
    posts_df['DATA-HORA'] = pd.to_datetime(posts_df['timestamp'])
                
    # Usamos .dt.day_name() para obter o nome completo do dia da semana em português
    posts_df['DIA_DA_SEMANA'] = posts_df['DATA-HORA'].dt.day_name(locale='pt_BR.UTF-8')

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
    #sdados_pivot_dias = dias_df.pivot(index='DIA_DA_SEMANA', columns='type', values=0)
    dados_pivot_dias = dias_df.pivot_table(index='DIA_DA_SEMANA', columns='type', values=0, aggfunc='sum')

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

def analyze_content_strategy_for_user(posts_df: pd.DataFrame, username: str, llm: BaseChatModel) -> ContentStrategyAnalysis:

    user_posts = posts_df[posts_df['ownerUsername'] == username] 
    top_captions = user_posts.nlargest(10, 'likesCount')['caption'].dropna().tolist() 

    if not top_captions:
        return ContentStrategyAnalysis(content_pillars=[], tone_of_voice="N/A", summary="Dados insuficientes para análise.") 

    captions_text = "\n".join(f"- {c}" for c in top_captions) 
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
        return ContentStrategyAnalysis(
               pilares=[],
               descricao="Erro na análise",
               tom="Erro na análise",
               resumo="Erro na análise"
              )