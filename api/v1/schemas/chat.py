from pydantic import BaseModel
from typing import List, Dict

class ChatMessage(BaseModel):
    role: str # 'user' ou 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: List[ChatMessage] # Para manter o histórico da conversa
    session_id: str # Para identificar a sessão do usuário (pode ser gerado no frontend)

class ChatResponse(BaseModel):
    response: str
    chat_history: List[ChatMessage]
    briefing_complete: bool = False # Indica se o briefing foi concluído
    extracted_briefing: Dict = None # O briefing extraído, se estiver completo