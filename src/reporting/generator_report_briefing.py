import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

# Adicionamos a importação da exceção
from langchain_core.exceptions import OutputParserException

# Carrega as variáveis de ambiente (sua chave da API)
load_dotenv()

def preencher_briefing(output_path):

    # --- 1. MODELO DE LINGUAGEM ---
    # Inicializa o modelo de linguagem que será o cérebro do nosso chatbot.
    # O `temperature=0.7` permite um equilíbrio entre respostas criativas e consistentes.
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.4)

    # --- 2. PERGUNTAS DO BRIEFING ---
    # Todas as perguntas que o agente deve fazer.
    questions = """
            1. Qual é o nome da sua empresa?
            2. Descreva em poucas palavras o que sua empresa faz e qual problema ela resolve.
            3. Quais são os valores e a personalidade da sua marca? (Ex: Jovem e descolada, séria e confiável, sofisticada e exclusiva?)
            4. Como você espera que a sua empresa seja percebida pelo seu público?
            5. Descreva todos os produtos e/ou serviços da sua empresa detalhadamente.
            6. Quais são os principais produtos ou serviços que você deseja promover nas redes sociais?
            7. Quem são seus principais concorrentes diretos e indiretos?
            8. Quem é o seu cliente ideal? (Descreva um perfil geral)
            9. Qual a faixa de idade do seu público ideal? (Exemplo: 15 aos 30 anos)
            10. Qual o gênero predominante do seu público ideal?
            11. Onde seu público ideal mora, trabalha ou frequenta? (Exemplo: São Paulo Capital, Bairros X, Y e Z.)
            12. Quais são os principais interesses do seu cliente ideal?
            13. Qual a faixa de renda aproximada do seu cliente ideal? (Exemplo: Até 2 salários mínimos, Acima de R$ 10.000)
            14. Quais são as principais dores, necessidades e desejos desse público?
            15. Qual é o principal objetivo com a gestão de redes sociais? (Ex: Aumentar o reconhecimento da marca, gerar leads, aumentar as vendas, criar uma comunidade?)
            16. Você tem alguma meta específica em mente? (Ex: Atingir 10.000 seguidores em 6 meses, gerar 50 leads por mês?)
            17. Qual é o resultado esperado que irá justificar seu investimento na estratégia?
            18. Em quais redes sociais você acredita que seu público está mais ativo?
            19. Que tipo de conteúdo você gostaria de ver nas suas redes sociais? (Ex: Dicas, bastidores, promoções, vídeos, artigos?)
            20. Qual é o tom de voz que devemos usar? (Ex: Formal, informal, engraçado, educativo?)
            21. Existe algum assunto ou abordagem que você gostaria de EVITAR?
            22. Você já possui algum material de marketing que possamos usar? (Ex: Fotos, vídeos, logo, manual da marca?)
            23. Existe mais alguma informação crucial que você acha que eu deveria saber
    """

    # --- 3. PROMPT E CADEIA DE CONVERSAÇÃO ---
    # O template de prompt define a personalidade e as instruções para o agente.
    template_conversation = f"""
    Você é um especialista em social media simpático e profissional. Sua tarefa é conduzir um briefing completo com um novo cliente.
    Faça as perguntas da lista abaixo, UMA DE CADA VEZ E NA ORDEM EM QUE APARECEM. Espere o cliente responder antes de passar para a próxima.
    Seja natural e conversacional. Comece se apresentando e explicando o processo. Gere o máximo de elogios que consguir.

    Lista de Perguntas:
    {questions}

    Quando tiver feito todas as perguntas, ou se o cliente disser que terminou, agradeça e se despeça.

    Histórico da Conversa:
    {{history}}

    Cliente: {{input}}
    Assistente de IA:
    """

    PROMPT_CONVERSATION = PromptTemplate(
        input_variables=["history", "input", "questions"], 
        template=template_conversation
    )

    # A ConversationChain orquestra o LLM, a Memória e o Prompt.
    conversation_chain = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory(),
        prompt=PROMPT_CONVERSATION,
        verbose=False # Mude para True para ver os detalhes do processo no terminal
    )

    # --- 4. FUNÇÃO PRINCIPAL DO CHAT ---
    def start_briefing_chat():
        """Inicia o loop de conversação com o cliente."""
        print("🤖 Assistente de IA: Olá! Sou seu assistente de IA para mídias sociais.")
        print("🤖 Assistente de IA: Vamos começar seu briefing? Vou fazer algumas perguntas para entender melhor seu negócio.")
        print("🤖 Assistente de IA: Ao final, quando estiver satisfeito, apenas digite 'fim' ou 'concluir'.\n")

        # Injeta a lista de perguntas no início da conversa
        conversation_chain.predict(input=f"Aqui está a lista de perguntas que preciso que você me faça: {questions}")

        # Primeira pergunta real para o cliente
        initial_response = conversation_chain.predict(input="Ótimo, pode começar com a primeira pergunta.")
        print(f"🤖 Assistente de IA: {initial_response}\n")

        while True:
            user_input = input("👤 Você: ")
            if user_input.lower() in ["fim", "concluir", "finalizar"]:
                print("\n🤖 Assistente de IA: Entendido! Briefing concluído. Muito obrigado pelas respostas.")
                print("🤖 Assistente de IA: Estou gerando o arquivo Markdown com o resumo. Um momento...")
                break
            
            ai_response = conversation_chain.predict(input=user_input)
            print(f"\n🤖 Assistente de IA: {ai_response}\n")
        
        return conversation_chain.memory

    # --- 5. FUNÇÃO PARA GERAR O ARQUIVO MARKDOWN ---
    def generate_markdown_file(memory):
        """Pega o histórico da memória e formata em um arquivo .md."""
        
        # Extrai o histórico completo da conversa
        history = memory.load_memory_variables({})["history"]
        
        # Template de prompt para a tarefa de sumarização e formatação
        template_formatter = """
        Sua tarefa é analisar o histórico de uma conversa de briefing entre um assistente de IA e um cliente.
        Extraia as perguntas ORIGINAIS da lista e as respostas do cliente correspondentes.
        Formate a saída EXCLUSIVAMENTE em Markdown, seguindo este modelo:

        # Briefing de Social Media

        ## Sobre a Empresa e Marca

        **1. Pergunta Original...**
        *Resposta:* Resposta do cliente.

        **2. Pergunta Original...**
        *Resposta:* Resposta do cliente.

        ...e assim por diante para todas as categorias e perguntas. Ignore saudações, despedidas e conversas informais.
        Se uma pergunta não foi claramente respondida, escreva "Resposta não fornecida.".

        Histórico da Conversa para Análise:
        {chat_history}
        """
        
        PROMPT_FORMATTER = PromptTemplate(input_variables=["chat_history"], template=template_formatter)
        
        # Cria uma cadeia simples apenas para esta tarefa de formatação
        formatter_chain = PROMPT_FORMATTER | llm
        
        markdown_output = formatter_chain.invoke({"chat_history": history}).content

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)    
        
        print(f"✅ Arquivo Markdown gerado com sucesso!")

        return markdown_output

    final_memory = start_briefing_chat()
    markdown_output = generate_markdown_file(final_memory)

    return markdown_output

# --- EXECUÇÃO ---
if __name__ == "__main__":
    
    preencher_briefing()