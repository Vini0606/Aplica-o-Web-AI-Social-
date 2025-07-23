# branded_app.py

import streamlit as st
import httpx
import base64
from pathlib import Path

# --- Configurações Iniciais e Variáveis Globais ---
FASTAPI_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    layout="wide",
    page_title="IA Social Planner",
    page_icon="🧠" # Favicon
)

# --- Funções de Utilitários e Estilo ---

def load_css():
    """Carrega e injeta o CSS customizado para alinhar ao manual de marca."""
    st.markdown("""
    <style>
        /* Importar Fontes do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500&display=swap');

        /* --- Tipografia --- */
        /* Fonte Principal (Títulos) */
        h1, h2, h3 {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            color: #0A2540; /* Cor Primária (Azul Profundo) */
        }
        /* Fonte Secundária (Corpo de Texto) */
        body, .stTextInput, .stTextArea, p {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            color: #333333;
        }
                
        div[data-testid="stSidebar"] button[kind="secondary"] {
            color: #FFFFFF !important;
        }
        
        /* Cor de Fundo Principal */
        .main .block-container {
            background-color: #FFFFFF;
        }
        /* Cor de Fundo da Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F6F9FC; /* Cinza Claro (Fundo) */
        }

        /* --- Estilo dos Botões --- */
        .stButton>button {
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.3s ease;
            color: #FFFFFF !important; /* Texto do botão branco */
        }
        
        .stButton>button p {
            color: #FFFFFF;
        }

        .stButton>button:hover {
            opacity: 0.9;
            transform: scale(1.02);
        }

        /* Botão Primário (CTA Principal - Gradiente) */
        /* Usado para a ação mais importante da página */
        div[data-testid*="stButton"] button[kind="primary"] {
            background-color: #28A745; /* Cor Primária (Azul) */
        }

        /* Botão Secundário (Azul Profundo) */
        div[data-testid*="stButton"] button[kind="secondary"] {
            background-color: #0A2540; /* Cor Primária (Azul) */
            color: #FFFFFF;
        }
        
        /* Botão de Logout/Login (Estilo sutil) */
        div[data-testid*="stButton"] button[kind="tertiary"] {
            background-color: #0A2540; /* Cor Primária (Azul) */
        }
        
        /* Estilo para inputs de texto */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            border: 1px solid #E6E6E6; /* Cinza Médio (Bordas) */
            border-radius: 5px;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #7A5CFA; /* Cor secundária no foco */
            box-shadow: 0 0 0 1px #7A5CFA;
        }

    </style>
    """, unsafe_allow_html=True)

def get_image_as_base64(path):
    """Converte uma imagem local para base64 para embutir no HTML."""
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

# Carrega o CSS customizado
load_css()

# --- Gerenciamento de Autenticação ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'brief_data' not in st.session_state:
    st.session_state.brief_data = None

def render_login_page():
    """Renderiza a interface de login na sidebar."""
    st.sidebar.subheader("Acesse a Plataforma")
    email = st.sidebar.text_input("Seu e-mail", key="login_email")
    password = st.sidebar.text_input("Sua senha", type="password", key="login_password")
    
    # Adicionando um espaço antes do botão para melhor layout
    st.sidebar.write("")
    
    # Usando st.columns para centralizar o botão de login se necessário, ou apenas para aplicar a classe
    col1, col2, col3 = st.sidebar.columns([1,2,1])
    with col2:
        if st.button("Entrar", key="login_button", use_container_width=True):
            if not email or not password:
                st.sidebar.warning("Por favor, preencha e-mail e senha.")
                return
            try:
                with st.spinner("Autenticando..."):
                    response = httpx.post(
                        f"{FASTAPI_BASE_URL}/auth/login",
                        json={"email": email, "senha": password}
                    )
                    response.raise_for_status()
                    token_data = response.json()
                    st.session_state.auth_token = token_data["access_token"]
                    st.session_state.user_email = email
                    st.session_state.logged_in = True
                    st.rerun() # Recarrega a aplicação para o estado "logado"
            except httpx.HTTPStatusError as e:
                st.sidebar.error(f"Falha na autenticação. Verifique seu e-mail e senha.")
            except Exception as e:
                st.sidebar.error(f"Ocorreu um erro de conexão. Tente novamente.")

def get_auth_headers():
    """Retorna os headers de autorização para as chamadas de API."""
    if st.session_state.logged_in and st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

# --- Logo da Marca ---
# (Assumindo que a imagem 'logo.png' está no mesmo diretório que o script)
logo_path = Path("Logo.png") # Substitua pelo caminho real do seu logo .png ou .svg
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True)
else:
    # Fallback para o nome da marca caso a imagem não seja encontrada
    st.sidebar.title("IA Social Planner")


# --- Lógica Principal da Aplicação ---
if not st.session_state.logged_in:
    render_login_page()
    st.info("Por favor, realize o login para acessar a plataforma e gerar sua estratégia de conteúdo.")
else:
    # --- Sidebar do Usuário Logado ---
    st.sidebar.success(f"Login como: {st.session_state.user_email}")
    if st.sidebar.button("Sair", key="logout_button", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.auth_token = None
        st.session_state.user_email = None
        st.session_state.brief_data = None
        st.rerun()

    # --- Conteúdo Principal ---
    st.title("Plataforma de Estratégia para Social Media")
    st.markdown("Preencha o formulário de briefing para que nossa IA possa analisar seu negócio e gerar relatórios estratégicos.")

    # --- Formulário de Briefing ---
    st.header("1. Detalhes da Empresa e Marca")
    nome_empresa = st.text_input("1. Qual é o nome da sua empresa?", key="q1_nome_empresa")
    o_que_faz = st.text_area("2. Em poucas palavras, o que a sua empresa faz e qual problema ela resolve?", key="q2_o_que_faz")
    valores_personalidade = st.text_area("3. Quais são os valores e a personalidade da sua marca?", key="q3_valores_personalidade")
    percepcao_desejada = st.text_area("4. Como você espera que a sua empresa seja percebida pelo seu público?", key="q4_percepcao_desejada")
    produtos_servicos = st.text_area("5. Descreva todos os seus produtos e/ou serviços detalhadamente", key="q5_produtos_servicos")
    produtos_promover = st.text_area("6. Quais são os principais produtos ou serviços que você deseja promover nas redes sociais?", key="q6_produtos_promover")
    concorrentes = st.text_area("7. Quem são seus principais concorrentes diretos e indiretos?", key="q7_concorrentes")

    st.header("2. Perfil do Cliente Ideal (Persona)")
    cliente_ideal_geral = st.text_area("8. Quem é o seu cliente ideal? Descreva um perfil geral.", key="q8_cliente_ideal_geral")
    cliente_idade = st.text_input("9. Qual a faixa de idade do seu cliente ideal?", key="q9_cliente_idade")
    cliente_genero = st.text_input("10. Qual o gênero predominante do seu cliente ideal?", key="q10_cliente_genero")
    cliente_localizacao = st.text_input("11. Onde seu público ideal mora, trabalha ou frequenta?", key="q11_cliente_localizacao")
    cliente_interesses = st.text_area("12. Quais são os principais interesses do seu público? (separados por vírgula)", key="q12_cliente_interesses")
    cliente_renda = st.text_input("13. Qual a faixa de renda aproximada do seu cliente ideal?", key="q13_cliente_renda")
    cliente_dores_necessidades_desejos = st.text_area("14. Quais são as principais dores, necessidades e desejos do seu público?", key="q14_cliente_dores_necessidades_desejos")

    st.header("3. Objetivos e Estratégia de Conteúdo")
    objetivo_principal_social = st.text_area("15. Qual é o principal objetivo com a gestão de redes sociais?", key="q15_objetivo_principal_social")
    metas_especificas = st.text_area("16. Você tem alguma meta específica em mente?", key="q16_metas_especificas")
    resultado_justificar_investimento = st.text_area("17. Qual é o resultado esperado que irá justificar seu investimento na estratégia?", key="q17_resultado_justificar_investimento")
    redes_sociais_ativas = st.text_area("18. Em quais redes sociais você acredita que seu público está mais ativo?", key="q18_redes_sociais_ativas")
    tipo_conteudo_desejado = st.text_area("19. Que tipo de conteúdo você gostaria de ver nas suas redes sociais?", key="q19_tipo_conteudo_desejado")
    tom_de_voz_desejado = st.text_input("20. Qual é o tom de voz que devemos usar nas redes sociais?", key="q20_tom_de_voz_desejado")
    assunto_evitar = st.text_area("21. Existe algum assunto ou abordagem que você gostaria de EVITAR nas redes sociais?", key="q21_assunto_evitar")
    material_marketing = st.text_input("23. Você já possui algum material de marketing que possamos usar?", key="q23_material_marketing")
    informacao_extra = st.text_area("24. Existe mais alguma informação que você acha que eu deveria saber sobre a sua empresa antes de começarmos a estratégia?", key="q24_informacao_extra")

    def validate_briefing_fields():
        required_fields = [
            nome_empresa, o_que_faz, valores_personalidade, percepcao_desejada,
            produtos_servicos, produtos_promover, concorrentes, cliente_ideal_geral,
            cliente_idade, cliente_genero, cliente_localizacao, cliente_interesses,
            cliente_renda, cliente_dores_necessidades_desejos, objetivo_principal_social,
            metas_especificas, resultado_justificar_investimento, redes_sociais_ativas,
            tipo_conteudo_desejado, tom_de_voz_desejado, assunto_evitar,
            material_marketing, informacao_extra
        ]
        return all(field and field.strip() != "" for field in required_fields)

    st.markdown("---")
    
    # --- Módulo de Extração de Dados ---
    st.header("4. Análise de Concorrentes (Opcional, mas Recomendado)")
    st.info("Para uma análise competitiva completa, forneça os dados abaixo para extrairmos insights sobre seus concorrentes.")

    keywords_input = st.text_input("Palavras-chave para busca de concorrentes (separadas por vírgula):", "pão da vila, padaria vila mariana", key="serp_keywords")
    location_input = st.text_input("Localização para a busca:", "São Paulo", key="serp_location")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="stButton"><button kind="secondary" style="width:100%;">1. Extrair Dados do Google</button></div>', unsafe_allow_html=True)
        if st.button("1. Extrair Dados do Google", key="extract_serp_button_hidden", type="secondary"):
            if keywords_input and location_input:
                # ... (lógica da API como no original)
                st.success("Extração do Google SERP concluída.")
            else:
                st.warning("Insira palavras-chave e localização para a extração.")
    with col2:
        st.markdown('<div class="stButton"><button kind="secondary" style="width:100%;">2. Extrair Dados do Instagram</button></div>', unsafe_allow_html=True)
        if st.button("2. Extrair Dados do Instagram", key="extract_instagram_button_hidden", type="secondary"):
            # ... (lógica da API como no original)
            st.success("Extração do Instagram concluída.")

    st.markdown("---")
    
    # --- Geração de Relatórios Finais ---
    st.header("5. Geração da Estratégia Completa")
    st.markdown("Após preencher o briefing (e opcionalmente extrair os dados dos concorrentes), clique no botão abaixo para gerar seus relatórios estratégicos.")

    # HTML/CSS para o botão primário com gradiente
    st.markdown("""
    <div class="stButton">
        <button kind="primary" style="width:100%; font-size: 1.2em; padding: 18px 24px;">
            Gerar Relatórios Finais
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Gerar Relatórios Finais", key="generate_all_reports_button_hidden", type="primary"):
        if not validate_briefing_fields():
            st.warning("Atenção: Por favor, preencha todos os campos do briefing para garantir uma análise completa e precisa.")
        else:
            # Construir o texto do briefing (mesma lógica do original)
            full_briefing_text = f"""...""" # (O texto completo do briefing é construído aqui como no original)

            with st.spinner("Analisando o briefing e gerando os relatórios... Isso pode levar alguns minutos."):
                try:
                    # 1. Analisar Briefing
                    # ... (código da chamada para /briefing/analyze como no original)
                    st.success("Briefing analisado com sucesso pela IA!")

                    # 2. Gerar Relatórios
                    st.subheader("Iniciando Geração dos Relatórios...")
                    # ... (código da chamada para os endpoints de relatório como no original)
                    st.success("✅ Relatórios gerados com sucesso!")

                except Exception as e:
                    st.error(f"❌ Ocorreu um erro inesperado: {e}")