# src/chatbot/briefing_chat.py

import os
import json
from typing import List, Dict, Union, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnablePassthrough
# REMOVIDO: from langchain_core.output_parsers import JsonOutputParser # Não será usado para a resposta do LLM diretamente
from pydantic.v1 import BaseModel, Field # MANTIDO: Usando pydantic.v1 para BaseModel e Field
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings # Para acessar o LLM e caminhos de salvamento
from src.analysis import engine # Para as funções parse_objetivos, etc.

# --- 1. Definir os modelos de saída para o briefing (Pydantic V1) ---
# Essas classes são usadas para validar e estruturar a saída do LLM (se houver, no compile_full_briefing)
# e também para armazenar o estado do briefing.

class Objetivo(BaseModel):
    objetivo_principal: str = Field(..., description="Objetivo principal do cliente")
    objetivo_secundario: List[str] = Field(..., description="Objetivos secundários do cliente")
    client_name: str = Field(..., description="Nome da empresa/cliente")

class Publico(BaseModel):
    idade: str
    genero: str
    localizacao: str
    ocupacao: str
    interesses: List[str]
    dores: List[str]

class Pilar(BaseModel):
    pilar: str
    descricao: str

class InfoEmpresa(BaseModel):
    nome: str
    ramo: str
    produtos_servicos: List[str]
    diferenciais: List[str]
    concorrentes: List[str]
    keywords: List[str]
    localizacao: str

class Posicionamento(BaseModel):
    tom_de_voz: str
    atributos_chave: List[str]
    vantagem_competitiva: str

class CalendarioItem(BaseModel):
    tema: str
    tipo_conteudo: str
    objetivo_associado: str
    data_sugerida: Optional[str] = None

class BriefingDataExtracted(BaseModel): # Modelo para o briefing COMPLETO que será re-analisado
    objetivos: Objetivo
    publico: Publico
    pilares: List[Pilar]
    infoempresa: InfoEmpresa
    posicionamento: Posicionamento
    calendario: List[CalendarioItem] = []

class BriefingState(BaseModel):
    # Campos que o chatbot deve coletar, mapeados às perguntas
    nome_empresa: Optional[str] = None
    o_que_faz: Optional[str] = None
    valores_personalidade: Optional[str] = None
    percepcao_desejada: Optional[str] = None
    produtos_servicos: Optional[str] = None
    produtos_promover: Optional[str] = None
    concorrentes: Optional[str] = None
    cliente_ideal_geral: Optional[str] = None
    cliente_idade: Optional[str] = None
    cliente_genero: Optional[str] = None
    cliente_localizacao: Optional[str] = None
    cliente_interesses: Optional[str] = None
    cliente_renda: Optional[str] = None
    cliente_dores_necessidades_desejos: Optional[str] = None
    objetivo_principal_social: Optional[str] = None
    metas_especificas: Optional[str] = None
    resultado_justificar_investimento: Optional[str] = None
    redes_sociais_ativas: Optional[str] = None
    tipo_conteudo_desejado: Optional[str] = None
    tom_de_voz_desejado: Optional[str] = None
    assunto_evitar: Optional[str] = None
    material_marketing: Optional[str] = None
    informacao_extra: Optional[str] = None

    # Controle de fluxo do chatbot
    current_question_index: int = 0
    briefing_questions = [
        "Qual é o nome da sua empresa?", # 0
        "Em poucas palavras, o que a sua empresa faz e qual problema ela resolve?", # 1
        "Quais são os valores e a personalidade da sua marca?", # 2
        "Como você espera que a sua empresa seja percebida pelo seu público?", # 3
        "Quais são os seus produtos e/ou serviços detalhadamente?", # 4
        "Quais são os principais produtos ou serviços que você deseja promover nas redes sociais?", # 5
        "Quem são seus principais concorrentes diretos e indiretos?", # 6
        "Quem é o seu cliente ideal? Descreva um perfil geral.", # 7
        "Qual a faixa de idade do seu cliente ideal?", # 8
        "Qual o gênero predominante do seu cliente ideal?", # 9
        "Onde seu público ideal mora, trabalha ou frequenta?", # 10
        "Quais são os principais interesses do seu público?", # 11
        "Qual a faixa de renda aproximada do seu cliente ideal?", # 12
        "Quais são as principais dores, necessidades e desejos do seu público?", # 13
        "Qual é o principal objetivo com a gestão de redes sociais?", # 14
        "Você tem alguma meta específica em mente?", # 15
        "Qual é o resultado esperado que irá justificar seu investimento na estratégia?", # 16
        "Em quais redes sociais você acredita que seu público está mais ativo?", # 17
        "Que tipo de conteúdo você gostaria de ver nas suas redes sociais?", # 18
        "Qual é o tom de voz que devemos usar nas redes sociais?", # 19
        "Existe algum assunto ou abordagem que você gostaria de EVITAR nas redes sociais?", # 20
        "Você já possui algum material de marketing que possamos usar?", # 21 (Pergunta 22 pulada)
        "Existe mais alguma informação que você acha que eu deveria saber sobre a sua empresa antes de começarmos a estratégia?", # 22
    ]

    def is_briefing_complete(self) -> bool:
        """Verifica se o índice da pergunta atual atingiu ou ultrapassou o número total de perguntas."""
        return self.current_question_index >= len(self.briefing_questions)

class ChatbotHandler:
    
    def __init__(self, llm: ChatGoogleGenerativeAI, session_id: str):
        
        self.llm = llm
        self.session_id = session_id
        self.briefing_file_path = os.path.join(settings.PROCESSED_DATA_PATH, f"briefing_chat_state_{session_id}.json")
        self.chat_history_file_path = os.path.join(settings.CHAT_HISTORY_PATH, f"chat_history_{session_id}.json")

        self.briefing_state: BriefingState = self._load_briefing_state()
        self.chat_history: List[BaseMessage] = self._load_chat_history()

        # self.parser = JsonOutputParser(pydantic_object=BriefingState) # Não usaremos mais diretamente na chain

        # PROMPT PARA GERAR A PRÓXIMA PERGUNTA (texto simples)
        self.prompt = ChatPromptTemplate(
            messages=[
                ("system", """Você é um assistente de briefing de social media. Seu objetivo é guiar o usuário pelas perguntas de briefing, uma por vez.
                Sua resposta deve ser SOMENTE a próxima pergunta na sequência do briefing ou a mensagem de conclusão.
                Não adicione comentários extras ou formatações. Apenas a pergunta ou a mensagem final.
                Se a resposta do usuário para a PERGUNTA ANTERIOR for ambígua, peça para ele elaborar antes de fazer a próxima pergunta.
                As perguntas devem ser feitas na seguinte ordem:
                {briefing_questions_list}

                ---
                Considere o histórico da conversa e o estado atual do briefing para formular a próxima pergunta.
                Estado atual do briefing (para sua referência, não retorne JSON na sua resposta): {briefing_state_json}
                ---
                """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input_message}") # input_message é a resposta do usuário à pergunta anterior
            ],
            # partial_variables não é mais necessário aqui, pois o parser não está na chain final
        )

        self.chain = (
            RunnablePassthrough.assign(
                briefing_questions_list=lambda x: "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.briefing_state.briefing_questions)]),
                briefing_state_json=lambda x: self.briefing_state.json() # CORREÇÃO: Usando .json()
            )
            | self.prompt
            | self.llm # CORREÇÃO: A chain termina no LLM, que retorna APENAS TEXTO
            # REMOVIDO: | self.parser # JsonOutputParser não está mais aqui
        )

    def _load_briefing_state(self) -> BriefingState:
        if os.path.exists(self.briefing_file_path):
            with open(self.briefing_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return BriefingState(**data)
        return BriefingState()

    def _save_briefing_state(self):
        with open(self.briefing_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.briefing_state.dict(), f, indent=4, ensure_ascii=False) # CORREÇÃO: Usando .dict()

    def _load_chat_history(self) -> List[BaseMessage]:
        if os.path.exists(self.chat_history_file_path):
            with open(self.chat_history_file_path, 'r', encoding='utf-8') as f:
                raw_history = json.load(f)
                history = []
                for msg in raw_history:
                    if msg['type'] == 'human':
                        history.append(HumanMessage(content=msg['content']))
                    elif msg['type'] == 'ai':
                        history.append(AIMessage(content=msg['content']))
                return history
        return []

    def _save_chat_history(self):
        serializable_history = []
        for msg in self.chat_history:
            serializable_history.append({"type": msg.type, "content": msg.content})
        with open(self.chat_history_file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_history, f, indent=4, ensure_ascii=False)

    def get_initial_greeting(self) -> str:
        # CORREÇÃO: A primeira mensagem real virá do process_message após o "Olá" do usuário
        if not self.briefing_state.is_briefing_complete():
            if not self.chat_history:
                return "Olá! Sou seu assistente de briefing de social media. Digite 'Olá' ou 'Começar' para iniciarmos!"
            else:
                return self.chat_history[-1].content
        else:
            return "O briefing já está completo. Posso agora processar os relatórios com base nas suas respostas?"

    def process_message(self, user_message: str) -> Dict[str, Union[str, bool, Dict]]:
        # Adiciona a mensagem do usuário ao histórico
        self.chat_history.append(HumanMessage(content=user_message))

        ai_response = "Desculpe, tive um problema. Poderia repetir ou reformular?" # Fallback
        extracted_briefing_data = {} # Será preenchido se o briefing for completo

        try:
            # 1. ATUALIZA o BriefingState com a resposta do usuário à PERGUNTA ANTERIOR
            # O 'user_message' é a resposta para a pergunta que o bot fez no turno anterior.
            self._update_briefing_state_from_user_response(user_message)

            # 2. Incrementa o índice da pergunta, pois a pergunta anterior foi "respondida"
            # (Mesmo que o LLM peça elaboração, avançamos o índice para manter o fluxo simples.
            # O LLM será instruído a repetir a pergunta se precisar de elaboração).
            if not self.briefing_state.is_briefing_complete():
                self.briefing_state.current_question_index += 1
            self._save_briefing_state() # Salva o estado atualizado imediatamente

            # 3. CHAMA o LLM para GERAR a PRÓXIMA PERGUNTA (texto simples) ou a mensagem final
            llm_response = self.chain.invoke({ # chain agora retorna TEXTO diretamente
                "input_message": user_message, # A última resposta do usuário para contexto
                "chat_history": self.chat_history, # Histórico completo da conversa
            })
            # O retorno do invoke deve ser uma Content (string) do LLM
            ai_response = str(llm_response.content) if hasattr(llm_response, 'content') else str(llm_response)

            # 4. Verifica se o briefing está completo após o avanço do índice
            if self.briefing_state.is_briefing_complete():
                ai_response = "Obrigado! O briefing foi concluído. Posso agora processar os relatórios com base nas suas respostas?"
                extracted_briefing_data = self.compile_full_briefing()

        except Exception as e:
            print(f"Erro ao processar mensagem do chatbot: {e}")
            ai_response = "Desculpe, tive um problema interno ao processar sua mensagem. Poderia repetir ou reformular, por favor?"
            # Em caso de erro, não avançamos o índice para que o usuário possa tentar novamente a mesma pergunta

        self.chat_history.append(AIMessage(content=ai_response))
        self._save_chat_history()

        return {
            "response": ai_response,
            "chat_history": [{"role": m.type, "content": m.content} for m in self.chat_history],
            "briefing_complete": self.briefing_state.is_briefing_complete(),
            "extracted_briefing": extracted_briefing_data if self.briefing_state.is_briefing_complete() else {}
        }

    def _update_briefing_state_from_user_response(self, user_response: str):
        """
        Atualiza o campo correspondente no BriefingState com base na resposta do usuário
        para a pergunta ANTERIOR.
        """
        # A pergunta a que o usuário acabou de responder é a (current_question_index - 1)
        # Se current_question_index for 0, significa que o usuário acabou de enviar
        # a primeira mensagem ("Olá"/"Começar"), então não há uma resposta
        # a uma pergunta do briefing para processar ainda.
        if self.briefing_state.current_question_index > 0:
            answered_question_idx = self.briefing_state.current_question_index - 1
            # Isso é um mapeamento manual e simples. Para um bot mais robusto,
            # o LLM faria a extração da entidade de forma mais flexível.
            if answered_question_idx == 0: self.briefing_state.nome_empresa = user_response
            elif answered_question_idx == 1: self.briefing_state.o_que_faz = user_response
            elif answered_question_idx == 2: self.briefing_state.valores_personalidade = user_response
            elif answered_question_idx == 3: self.briefing_state.percepcao_desejada = user_response
            elif answered_question_idx == 4: self.briefing_state.produtos_servicos = user_response
            elif answered_question_idx == 5: self.briefing_state.produtos_promover = user_response
            elif answered_question_idx == 6: self.briefing_state.concorrentes = user_response
            elif answered_question_idx == 7: self.briefing_state.cliente_ideal_geral = user_response
            elif answered_question_idx == 8: self.briefing_state.cliente_idade = user_response
            elif answered_question_idx == 9: self.briefing_state.cliente_genero = user_response
            elif answered_question_idx == 10: self.briefing_state.cliente_localizacao = user_response
            elif answered_question_idx == 11: self.briefing_state.cliente_interesses = user_response
            elif answered_question_idx == 12: self.briefing_state.cliente_renda = user_response
            elif answered_question_idx == 13: self.briefing_state.cliente_dores_necessidades_desejos = user_response
            elif answered_question_idx == 14: self.briefing_state.objetivo_principal_social = user_response
            elif answered_question_idx == 15: self.briefing_state.metas_especificas = user_response
            elif answered_question_idx == 16: self.briefing_state.resultado_justificar_investimento = user_response
            elif answered_question_idx == 17: self.briefing_state.redes_sociais_ativas = user_response
            elif answered_question_idx == 18: self.briefing_state.tipo_conteudo_desejado = user_response
            elif answered_question_idx == 19: self.briefing_state.tom_de_voz_desejado = user_response
            elif answered_question_idx == 20: self.briefing_state.assunto_evitar = user_response
            elif answered_question_idx == 21: self.briefing_state.material_marketing = user_response
            elif answered_question_idx == 22: self.briefing_state.informacao_extra = user_response
            # Você pode adicionar um else para 'print' ou log se o índice for inesperado.

    def compile_full_briefing(self) -> Dict:
        """
        Compila o BriefingState em um formato compatível com o seu BriefingData,
        re-analisando o texto completo com as funções 'engine'.
        """
        compiled_briefing = {}

        full_briefing_text = self._build_full_briefing_text()
        print(f"DEBUG: Texto completo do briefing para análise final: {full_briefing_text[:500]}...")

        llm = settings.LLM

        try:
            compiled_briefing['objetivos'] = engine.parse_objetivos(full_briefing_text, llm).dict()
            compiled_briefing['publico'] = engine.parse_publicos(full_briefing_text, llm).dict()
            compiled_briefing['pilares'] = engine.parse_pilares(full_briefing_text, llm, compiled_briefing['objetivos'], compiled_briefing['publico']).dict()["pilares"]
            compiled_briefing['infoempresa'] = engine.parse_info_empresa(full_briefing_text, llm).dict()
            compiled_briefing['posicionamento'] = engine.parse_posicionamento(
                objetivos=compiled_briefing['objetivos'], publico=compiled_briefing['publico'], llm=llm
            ).dict()

            calendario_obj = engine.parse_calendario_editorial(
                pilares=compiled_briefing['pilares'],
                objetivos=compiled_briefing['objetivos'],
                publico=compiled_briefing['publico'],
                llm=llm
            )
            compiled_briefing['calendario'] = calendario_obj.dict()["calendario"] if calendario_obj else []

        except Exception as e:
            print(f"Erro ao compilar briefing completo com funções de análise: {e}")
            raise

        return compiled_briefing

    def _build_full_briefing_text(self) -> str:
        """Constrói um texto de briefing completo a partir do BriefingState para re-análise."""
        full_text = ""
        qa_map = {
            "nome_empresa": "1. Pergunta Original: Qual é o nome da sua empresa?\n*Resposta: ",
            "o_que_faz": "2. Pergunta Original: Em poucas palavras, o que a sua empresa faz e qual problema ela resolve?\n*Resposta: ",
            "valores_personalidade": "3. Pergunta Original: Quais são os valores e a personalidade da sua marca?\n*Resposta: ",
            "percepcao_desejada": "4. Pergunta Original: Como você espera que a sua empresa seja percebida pelo seu público?\n*Resposta: ",
            "produtos_servicos": "5. Pergunta Original: Quais são os seus produtos e/ou serviços detalhadamente?\n*Resposta: ",
            "produtos_promover": "6. Pergunta Original: Quais são os principais produtos ou serviços que você deseja promover nas redes sociais?\n*Resposta: ",
            "concorrentes": "7. Pergunta Original: Quem são seus principais concorrentes diretos e indiretos?\n*Resposta: ",
            "cliente_ideal_geral": "8. Pergunta Original: Quem é o seu cliente ideal? Descreva um perfil geral.\n*Resposta: ",
            "cliente_idade": "9. Pergunta Original: Qual a faixa de idade do seu cliente ideal?\n*Resposta: ",
            "cliente_genero": "10. Pergunta Original: Qual o gênero predominante do seu cliente ideal?\n*Resposta: ",
            "cliente_localizacao": "11. Pergunta Original: Onde seu público ideal mora, trabalha ou frequenta?\n*Resposta: ",
            "cliente_interesses": "12. Pergunta Original: Quais são os principais interesses do seu público?\n*Resposta: ",
            "cliente_renda": "13. Pergunta Original: Qual a faixa de renda aproximada do seu cliente ideal?\n*Resposta: ",
            "cliente_dores_necessidades_desejos": "14. Pergunta Original: Quais são as principais dores, necessidades e desejos do seu público?\n*Resposta: ",
            "objetivo_principal_social": "15. Pergunta Original: Qual é o principal objetivo com a gestão de redes sociais?\n*Resposta: ",
            "metas_especificas": "16. Pergunta Original: Você tem alguma meta específica em mente?\n*Resposta: ",
            "resultado_justificar_investimento": "17. Pergunta Original: Qual é o resultado esperado que irá justificar seu investimento na estratégia?\n*Resposta: ",
            "redes_sociais_ativas": "18. Pergunta Original: Em quais redes sociais você acredita que seu público está mais ativo?\n*Resposta: ",
            "tipo_conteudo_desejado": "19. Pergunta Original: Que tipo de conteúdo você gostaria de ver nas suas redes sociais?\n*Resposta: ",
            "tom_de_voz_desejado": "20. Pergunta Original: Qual é o tom de voz que devemos usar nas redes sociais?\n*Resposta: ",
            "assunto_evitar": "21. Pergunta Original: Existe algum assunto ou abordagem que você gostaria de EVITAR nas redes sociais?\n*Resposta: ",
            "material_marketing": "23. Pergunta Original: Você já possui algum material de marketing que possamos usar?\n*Resposta: ",
            "informacao_extra": "24. Pergunta Original: Existe mais alguma informação que você acha que eu deveria saber sobre a sua empresa antes de começarmos a estratégia?\n*Resposta: "
        }

        for field_name, question__prefix in qa_map.items():
            response_value = getattr(self.briefing_state, field_name, None)
            if response_value:
                full_text += f"{question__prefix}{response_value}\n\n"
        return full_text