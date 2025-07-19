# api/v1/schemas/briefing.py

from pydantic import BaseModel, Field
from typing import List, Optional # Mantendo Optional para campos que podem ser None

# NOTA: Estas classes devem ser IDÊNTICAS às definidas em src/analysis/engine.py
# para garantir que a validação de entrada/saída da API funcione corretamente.
# Se engine.py usa Pydantic V1 (pydantic.v1.BaseModel), mude para:
# from pydantic.v1 import BaseModel, Field
# A análise do erro 'engine.py' mostrou 'from pydantic import BaseModel, Field'
# então estamos usando essa importação aqui.

# ================
# Schemas de Entrada (para a requisição da API)
# ================

class BriefingInput(BaseModel):
    briefing_text: str = Field(..., description="Texto completo do briefing do usuário.")

# ================
# Schemas de Saída (para a resposta da API, alinhados com engine.py)
# ================

# Corresponde à classe 'Objetivos' em engine.py
class Objetivos(BaseModel):
    client_name: str = Field(description="O nome de usuário da empresa cliente no instagram. [tarcisiogdf]")
    objetivo_principal: str = Field(description="O objetivo principal do cliente no modelo SMART (Específicos, Mensuráveis, Atingíveis, Relevantes e com Prazo definido). [Ex: Aumentar as vendas online em 15% através do Instagram nos próximos 6 meses.]")
    objetivo_secundario: List[str] = Field(description="objetivos secundários do cliente nas redes sociais. [Ex: Aumentar o número de seguidores qualificados em 20% no próximo trimestre\nAumentar a taxa de engajamento (curtidas, comentários, salvamentos) em 10% ao mês.]")

# Corresponde à classe 'Publico' em engine.py
class Publico(BaseModel):
    idade: str = Field(description="A faixa de idade do principal publico-alvo do cliente. [Ex: 25-35 anos]")
    genero: str = Field(description="Gênero do principal publico-alvo do cliente (Preencha 'Ambos' quando for os dois). [Ex: Feminino]")
    localizacao: str = Field(description="Localização do principal publico-alvo do cliente.  [Ex: Principais capitais do Brasil]")
    ocupacao: str = Field(description="Ocupação do principal publico-alvo do cliente. [Ex: Dona de um pequeno negócio de artesanato]")
    renda: str = Field(description="A faixa da renda do principal publico-alvo do cliente. [Ex: R$ 4.000 - R$ 7.000]")
    interesses: List[str] = Field(description="Lista de Comportamentos e Interesses do publico-alvo do cliente. [Ex: Segue perfis de inspiração, DIY (Faça Você Mesmo) e dicas de negócios\nUsa o Instagram diariamente para descobrir novas marcas e produtos.]")
    dores: List[str] = Field(description="Lista de Dores e Necessidades do público-alvo do cliente. Ex: Sente dificuldade em organizar suas finanças como autônoma. Busca por materiais de alta qualidade para seus produtos. Precisa de dicas para otimizar seu tempo e ser mais produtiva.]")

# Corresponde à classe 'PilaresConteudo' em engine.py
class PilaresConteudo(BaseModel):
    nome: str = Field(description="O nome do pilar de conteúdo, exemplo: 'Educacional'.")
    objetivo: str = Field(description="O objetivo do pilar, exemplo: 'Ensinar e informar'")
    exemplos: List[str] = Field(description="Lista de 3-5 exemplos de conteúdo. ['Tutoriais', 'Dicas rápidas']")

# Corresponde à classe 'InfoEmpresa' em engine.py
class InfoEmpresa(BaseModel):
    nome_empresa: str = Field(description="O nome da empresa do cliente no instagram.")
    keywords: List[str] = Field(description="Palavras-chave utilizadas pelos concorrentes do cliente, na biografia do instagram. Exemplo: pizzaria, restaurante, lanchonete")
    localizacao: str = Field(description="Endereço completo da empresa.")
    bairros: List[str] = Field(description="Bairros muito próximos, ou pertencentes, da localização da empresa")

# Corresponde à classe 'Posicionamento' em engine.py
class Posicionamento(BaseModel):
    tom_de_voz: str = Field(description="Adjetivos que descrevem como a marca deve se comunicar. Ex: 'Amigável, especialista e inspirador'.")
    arquetipo: str = Field(description="O arquétipo de marca que melhor representa a empresa. Ex: 'O Sábio', 'O Explorador', 'O Cuidador'.")
    diferenciais: List[str] = Field(description="Uma lista dos 2-3 principais pontos que tornam a marca única em relação à concorrência.")
    proposta_de_valor: str = Field(description="Uma frase curta que resume o principal benefício que o cliente recebe. Ex: 'Ajudamos criativos a transformarem paixão em negócio com ferramentas e inspiração'.")
    resumo_posicionamento: str = Field(description="Um parágrafo único que resume todo o posicionamento da marca, ideal para ser usado em briefings e guias de estilo.")

# Corresponde à classe 'EntradaCalendario' em engine.py
class EntradaCalendario(BaseModel):
    dia: str = Field(description="Dia da semana (ex: 'Segunda-feira').")
    pilar: str = Field(description="O nome de um dos pilares de conteúdo fornecidos a ser usado neste dia.")
    periodo: str = Field(description="O periodo de postagem sugerido (ex: 'Manhã', 'Tarde', 'Noite').")

# Classe principal que agrega todos os dados analisados do briefing
# NOTA: O BriefingData deve refletir a estrutura de saída final após todas as análises.
class BriefingData(BaseModel):
    objetivos: Objetivos # CORREÇÃO: Usando a classe Objetivos
    publico: Publico
    pilares: List[PilaresConteudo] # CORREÇÃO: Usando PilaresConteudo
    infoempresa: InfoEmpresa
    posicionamento: Posicionamento
    calendario: List[EntradaCalendario] = [] # CORREÇÃO: Usando EntradaCalendario