# api/v1/endpoints/chat_routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from uuid import uuid4
import os
import json
from config import settings
from api.v1.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from src.chatbot.briefing_chat import ChatbotHandler, BriefingState # Importe o handler do chatbot
from src.analysis import engine # Para operações de dados e relatórios
from src.reporting import generator_report_concorrentes, generator_report_estrategia, generator_report_publicacoes
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

router = APIRouter(tags=["Chatbot Briefing"])

# Dicionário para armazenar instâncias de ChatbotHandler por sessão
# Em um ambiente de produção real, isso seria um banco de dados ou Redis.
chat_sessions: Dict[str, ChatbotHandler] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    Processa uma mensagem do usuário e retorna a resposta do chatbot.
    Mantém o histórico da conversa e o estado do briefing.
    """
    session_id = request.session_id
    if session_id not in chat_sessions:
        chat_sessions[session_id] = ChatbotHandler(llm=settings.LLM, session_id=session_id)
        # Se for a primeira mensagem, o bot pode dar uma saudação inicial
        if not request.chat_history:
            initial_response = chat_sessions[session_id].get_initial_greeting()
            chat_sessions[session_id].chat_history.append(AIMessage(content=initial_response))
            return ChatResponse(
                response=initial_response,
                chat_history=[{"role": "assistant", "content": initial_response}],
                briefing_complete=False
            )

    chatbot_handler = chat_sessions[session_id]

    # Processa a mensagem do usuário
    result = chatbot_handler.process_message(request.message)

    return ChatResponse(
        response=result["response"],
        chat_history=result["chat_history"],
        briefing_complete=result["briefing_complete"],
        extracted_briefing=result["extracted_briefing"]
    )

@router.post("/briefing/complete-and-generate-reports")
async def complete_and_generate_reports(session_id: str):
    """
    Endpoint para finalizar o briefing e disparar a geração de todos os relatórios.
    Deve ser chamado apenas quando o briefing estiver 'briefing_complete'.
    """
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada. Inicie um briefing primeiro.")

    chatbot_handler = chat_sessions[session_id]

    if not chatbot_handler.briefing_state.is_briefing_complete():
        raise HTTPException(status_code=400, detail="Briefing não está completo. Continue a conversa com o chatbot.")

    reports_status = {"estrategia": "pendente", "publicacoes": "pendente", "concorrentes": "pendente"}

    try:
        # 1. Compilar o briefing completo a partir do estado do chatbot
        brief_data = chatbot_handler.compile_full_briefing()
        if "error" in brief_data:
             raise HTTPException(status_code=500, detail=f"Erro ao compilar briefing: {brief_data['error']}")

        # Salvar o briefing compilado para que as funções de relatório possam lê-lo
        with open(settings.BRIEFING_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(brief_data, f, indent=4, ensure_ascii=False)


        # 2. Gerar Relatório de Estratégia
        try:
            objetivo_principal = [brief_data['objetivos']['objetivo_principal']]
            objetivos_secundarios = brief_data['objetivos']['objetivo_secundario']
            list_objetivos = objetivo_principal + objetivos_secundarios

            generator_report_estrategia.preencher_plano_marketing(
                brief_data,
                caminho_saida=settings.ESTRATEGIA_PATH,
                nome_empresa=brief_data['objetivos']['client_name'],
                responsavel="Equipe AI Social",
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
            reports_status["estrategia"] = "sucesso"
        except Exception as e:
            reports_status["estrategia"] = f"falha: {e}"
            print(f"Erro ao gerar relatório de estratégia: {e}")

        # 3. Gerar Relatório de Publicações
        try:
            llm = settings.LLM
            generator_report_publicacoes.preencher_publicacoes(
                llm=llm,
                pilares=brief_data['pilares'],
                objetivos=brief_data['objetivos'],
                publico=brief_data['publico'],
                posicionamento=brief_data['posicionamento']
            )
            reports_status["publicacoes"] = "sucesso"
        except Exception as e:
            reports_status["publicacoes"] = f"falha: {e}"
            print(f"Erro ao gerar relatório de publicações: {e}")

        # 4. Gerar Relatório de Concorrentes (requer dados de Instagram/SERP)
        # Atenção: Você precisará decidir como esses dados são obtidos no fluxo do chatbot.
        # Opções:
        # a) O chatbot também pergunta por concorrentes e faz a extração de dados no final.
        # b) O usuário faz a extração de dados em um passo separado no frontend.
        # c) Assume-se que os dados já foram extraídos e salvos previamente.
        # Para este exemplo, vou assumir que os dados já existem ou você vai adaptar.
        try:
            posts_df = engine.load_posts_to_df(settings.POST_PATH)
            profile_df = engine.load_profiles_to_df(settings.PROFILE_PATH)

            if posts_df.empty or profile_df.empty:
                reports_status["concorrentes"] = "falha: Dados de Instagram não encontrados. Extraia-os primeiro."
                print("Dados de posts ou perfis do Instagram não encontrados para relatório de concorrentes.")
            else:
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
                llm = settings.LLM
                generator_report_concorrentes.generate_full_report(
                    llm,
                    dataframes,
                    client_name=brief_data['objetivos']['client_name'],
                    output_path=settings.CONCORRENTES_PATH,
                    template_path=settings.TEMPLATE_PATH,
                )
                reports_status["concorrentes"] = "sucesso"
        except FileNotFoundError as e:
            reports_status["concorrentes"] = f"falha: Arquivos de dados para concorrentes não encontrados: {e}"
            print(f"Erro de FileNotFoundError ao gerar relatório de concorrentes: {e}")
        except Exception as e:
            reports_status["concorrentes"] = f"falha: {e}"
            print(f"Erro ao gerar relatório de concorrentes: {e}")

        # Limpa o estado da sessão após a conclusão (opcional)
        # del chat_sessions[session_id]

        return {"message": "Geração de relatórios concluída.", "status": reports_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro crítico ao gerar relatórios: {str(e)}")

# Limpar sessão do chat (opcional)
@router.delete("/chat/{session_id}")
async def reset_chat(session_id: str):
    if session_id in chat_sessions:
        # Remover arquivos de histórico e estado
        handler = chat_sessions[session_id]
        if os.path.exists(handler.briefing_file_path):
            os.remove(handler.briefing_file_path)
        if os.path.exists(handler.chat_history_file_path):
            os.remove(handler.chat_history_file_path)
        del chat_sessions[session_id]
        return {"message": f"Sessão {session_id} resetada e arquivos limpos."}
    raise HTTPException(status_code=404, detail="Sessão não encontrada.")