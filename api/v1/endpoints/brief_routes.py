from fastapi import APIRouter, HTTPException, Depends
import json
from config import settings
from src.analysis import engine
from api.v1.schemas.briefing import BriefingInput, BriefingData # Importe BriefingInput e BriefingData
from auth.dependencies import get_current_active_user # NOVO
from models import Usuario # NOVO

router = APIRouter(prefix='/briefing', tags=['Briefing Analysis']) # Renomeado para briefing

@router.post("/analyze", response_model=BriefingData) # Renomeado para analyze
async def analyze_briefing(briefing_data: BriefingInput, current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Analisa o texto do briefing do usuário e extrai informações chave.
    """
    print(f"Analisando o briefing para o usuário: {current_user.email}")
    llm = settings.LLM

    try:
        brief_data = {}
        # Usando .dict() se os modelos do engine forem Pydantic V1, senão .model_dump()
        brief_data['objetivos'] = engine.parse_objetivos(briefing_data.briefing_text, llm).dict()
        brief_data['publico'] = engine.parse_publicos(briefing_data.briefing_text, llm).dict()
        brief_data['pilares'] = engine.parse_pilares(
            briefing_data.briefing_text, llm, brief_data['objetivos'], brief_data['publico']
        ).dict()["pilares"]
        brief_data['infoempresa'] = engine.parse_info_empresa(briefing_data.briefing_text, llm).dict()
        brief_data['posicionamento'] = engine.parse_posicionamento(
            objetivos=brief_data['objetivos'], publico=brief_data['publico'], llm=llm
        ).dict()

        print("Gerando sugestão de calendário editorial...")
        calendario_obj = engine.parse_calendario_editorial(
            pilares=brief_data['pilares'],
            objetivos=brief_data['objetivos'],
            publico=brief_data['publico'],
            llm=llm
        )
        brief_data['calendario'] = calendario_obj.dict()["calendario"] if calendario_obj else [] # Usando .dict()
        print("Calendário gerado com sucesso!")

        # Salvar o briefing analisado em um arquivo JSON
        # Você pode considerar salvar por usuário, usando current_user.id
        with open(settings.BRIEFING_JSON_PATH, 'w', encoding='utf-8') as arquivo_json:
            json.dump(brief_data, arquivo_json, indent=4, ensure_ascii=False)

        print("Briefing Analisado com Sucesso!")
        return BriefingData(**brief_data) # Retorna o objeto completo de BriefingData
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar o briefing: {str(e)}")

# Se precisar de um GET para o briefing analisado por usuário
@router.get("/", response_model=BriefingData)
async def get_analyzed_briefing(current_user: Usuario = Depends(get_current_active_user)): # Protegido
    """
    Recupera os dados do briefing analisado previamente para o usuário atual.
    """
    try:
        with open(settings.BRIEFING_JSON_PATH, 'r', encoding='utf-8') as f:
            brief_data = json.load(f)
        return BriefingData(**brief_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Briefing não encontrado para este usuário. Analise um briefing primeiro.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar o briefing: {str(e)}")