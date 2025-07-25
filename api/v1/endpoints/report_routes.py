from fastapi import APIRouter, HTTPException, Depends
import json
import os
import pandas as pd # Adicionado import de pandas
from config import settings
from src.analysis import engine
from src.reporting import generator_report_concorrentes, generator_report_estrategia, generator_report_publicacoes
from auth.dependencies import get_current_active_user
from models import Usuario

# CORREÇÃO: Definindo o nome da instância do APIRouter como 'router'
router = APIRouter(tags=["Report Generation"])

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel # <-- IMPORTAÇÃO NOVA
import json
import os
import pandas as pd
from config import settings
from src.analysis import engine
from src.reporting import generator_report_concorrentes, generator_report_estrategia, generator_report_publicacoes
from auth.dependencies import get_current_active_user
from models import Usuario
from src.data_ingestion.gdrive_uploader import upload_reports_to_drive

router = APIRouter(tags=["Report Generation"])

# NOVO MODELO PARA A REQUISIÇÃO DE UPLOAD
class UploadRequest(BaseModel):
    client_name: str

# NOVO ENDPOINT DE UPLOAD
@router.post("/reports/upload-to-drive")
async def upload_generated_reports(
    request_data: UploadRequest, 
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Pega os relatórios já gerados do disco e faz o upload para o Google Drive.
    """
    try:
        client_name = request_data.client_name
        print(f"Iniciando processo de upload para o cliente: {client_name}")

        # Lista de arquivos que devem ter sido gerados pelas outras rotas
        # Certifique-se que estes caminhos correspondem aos caminhos de saída dos seus geradores
        files_to_upload = [
            settings.ESTRATEGIA_PATH,
            settings.PUBLICACOES_PATH, # Conforme o código em generator_report_publicacoes.py
            settings.CONCORRENTES_PATH,
        ]

        upload_reports_to_drive(
            client_name=client_name,
            file_paths=files_to_upload,
            credentials_path=settings.GDRIVE_PATH_CREDENTIALS # Caminho para suas credenciais
        )

        return {"message": f"Relatórios para '{client_name}' enviados com sucesso para o Google Drive."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado. Certifique-se de que os relatórios foram gerados primeiro. Erro: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro durante o upload para o Google Drive: {str(e)}")

@router.post("/reports/estrategia")
async def generate_strategy_report(current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Gera o relatório de estratégia de marketing.
    Requer que o briefing já tenha sido analisado.
    """
    try:
        with open(settings.BRIEFING_JSON_PATH, 'r', encoding='utf-8') as f:
            brief_data = json.load(f)

        if not brief_data:
            raise HTTPException(status_code=400, detail="Briefing não analisado. Analise um briefing primeiro.")

        objetivo_principal = [brief_data['objetivos']['objetivo_principal']]
        objetivos_secundarios = brief_data['objetivos']['objetivo_secundario']
        list_objetivos = objetivo_principal + objetivos_secundarios

        generator_report_estrategia.preencher_plano_marketing(
            brief_data,
            caminho_saida=settings.ESTRATEGIA_PATH,
            nome_empresa=brief_data['objetivos']['client_name'],
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
        return {"message": f"Relatório de estratégia gerado em {settings.ESTRATEGIA_PATH}"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Arquivo de briefing ({settings.BRIEFING_JSON_PATH}) não encontrado. Analise um briefing primeiro.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de estratégia: {str(e)}")

@router.post("/reports/publicacoes")
async def generate_publications_report(current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Gera o relatório de sugestões de publicações.
    Requer que o briefing já tenha sido analisado.
    """
    try:
        with open(settings.BRIEFING_JSON_PATH, 'r', encoding='utf-8') as f:
            brief_data = json.load(f)

        if not brief_data:
            raise HTTPException(status_code=400, detail="Briefing não analisado. Analise o briefing primeiro.")

        llm = settings.LLM
        generator_report_publicacoes.preencher_publicacoes(
            llm=llm,
            pilares=brief_data['pilares'],
            objetivos=brief_data['objetivos'],
            publico=brief_data['publico'],
            posicionamento=brief_data['posicionamento']
        )
        return {"message": "Relatório de publicações gerado com sucesso."}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Arquivo de briefing ({settings.BRIEFING_JSON_PATH}) não encontrado. Analise um briefing primeiro.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de publicações: {str(e)}")

@router.post("/reports/concorrentes")
async def generate_competitor_report(current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Gera o relatório de análise de concorrentes.
    Requer que os dados do Instagram tenham sido extraídos.
    """

    try:
        
        # Carrega os dataframes necessários
        posts_df = engine.load_posts_to_df(settings.POST_PATH)
        profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH)

        if posts_df.empty or profile_df.empty:
            raise HTTPException(status_code=400, detail="Dados de posts ou perfis do Instagram não encontrados. Execute a extração do Google SERP e Instagram primeiro.")

        profiles_posts_df = engine.load_join_profiles_posts(posts_df, profile_df)
        list_dfs_pivot = engine.load_top_3_profiles(posts_df, profile_df)
        list_dfs_periodo = engine.load_periodo_dias(posts_df, profile_df)
        list_dfs_pivot_periodo = engine.load_pivot_periodo_dias(posts_df, profile_df)
        dataframes = {
            'df_profiles_posts': profiles_posts_df,
            'posts_df': posts_df,
            'dados_pivot_count': list_dfs_pivot[0],
            'dados_pivot_total': list_dfs_pivot[1],
            'dados_pivot_likes':  list_dfs_pivot[2],
            'dados_pivot_comments': list_dfs_pivot[3],
            'periodo_df': list_dfs_periodo[0],
            'dias_df': list_dfs_periodo[1],
            'dados_pivot_periodos': list_dfs_pivot_periodo[0],
            'dados_pivot_dias': list_dfs_pivot_periodo[1]
        }

        with open(settings.BRIEFING_JSON_PATH, 'r', encoding='utf-8') as f:
            brief_data = json.load(f)

        if not brief_data or 'objetivos' not in brief_data:
            raise HTTPException(status_code=400, detail="Briefing não analisado ou incompleto. Analise o briefing primeiro.")

        llm = settings.LLM
        generator_report_concorrentes.generate_full_report(
            llm,
            dataframes,
            client_name=brief_data['objetivos']['client_name'],
            output_path=settings.CONCORRENTES_PATH,
            template_path=settings.TEMPLATE_PATH,
        )
        return {"message": f"Relatório de concorrentes gerado em {settings.CONCORRENTES_PATH}"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Arquivos de dados ou briefing não encontrados para o relatório de concorrentes: {e}. Certifique-se de que as etapas anteriores (análise do briefing, extração de SERP e Instagram) foram executadas para o usuário logado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de concorrentes: {str(e)}")