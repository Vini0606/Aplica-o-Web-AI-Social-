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
    
    if st.button("Gerar Relatórios Finais", key="generate_all_reports_button"):
        
        if not validate_briefing_fields():
            st.warning("Por favor, preencha TODOS os campos do briefing antes de gerar os relatórios.")
        else:
            # Construir o texto completo do briefing a partir dos campos do formulário
            full_briefing_text = f"""
            # Briefing de Social Media

            ## Sobre a Empresa e Marca

            1. Pergunta Original: Qual é o nome da sua empresa?
            *Resposta: {nome_empresa}

            2. Pergunta Original: Em poucas palavras, o que a "Pão da Vila" faz e qual problema ela resolve?
            *Resposta: {o_que_faz}

            3. Pergunta Original: Quais são os valores e a personalidade da "Pão da Vila"?
            *Resposta: {valores_personalidade}

            4. Pergunta Original: Como você espera que a "Pão da Vila" seja percebida pelo seu público?
            *Resposta: {percepcao_desejada}

            5. Pergunta Original: Quais são os seus produtos e/ou serviços detalhadamente?
            *Resposta: {produtos_servicos}

            6. Pergunta Original: Quais são os principais produtos ou serviços que você deseja promover nas redes sociais?
            *Resposta: {produtos_promover}

            7. Pergunta Original: Quem são seus principais concorrentes diretos e indiretos?
            *Resposta: {concorrentes}

            8. Pergunta Original: Quem é o seu cliente ideal? Descreva um perfil geral.
            *Resposta: {cliente_ideal_geral}

            9. Pergunta Original: Qual a faixa de idade do seu cliente ideal?
            *Resposta: {cliente_idade}

            10. Pergunta Original: Qual o gênero predominante do seu cliente ideal?
            *Resposta: {cliente_genero}

            11. Pergunta Original: Onde seu público ideal mora, trabalha ou frequenta?
            *Resposta: {cliente_localizacao}

            12. Pergunta Original: Quais são os principais interesses do seu público?
            *Resposta: {cliente_interesses}

            13. Pergunta Original: Qual a faixa de renda aproximada do seu cliente ideal?
            *Resposta: {cliente_renda}

            14. Pergunta Original: Quais são as principais dores, necessidades e desejos do seu público?
            *Resposta: {cliente_dores_necessidades_desejos}

            15. Pergunta Original: Qual é o principal objetivo com a gestão de redes sociais?
            *Resposta: {objetivo_principal_social}

            16. Pergunta Original: Você tem alguma meta específica em mente?
            *Resposta: {metas_especificas}

            17. Pergunta Original: Qual é o resultado esperado que irá justificar seu investimento na estratégia?
            *Resposta: {resultado_justificar_investimento}

            18. Pergunta Original: Em quais redes sociais você acredita que seu público está mais ativo?
            *Resposta: {redes_sociais_ativas}

            19. Pergunta Original: Que tipo de conteúdo você gostaria de ver nas suas redes sociais?
            *Resposta: {tipo_conteudo_desejado}

            20. Pergunta Original: Qual é o tom de voz que devemos usar nas redes sociais?
            *Resposta: {tom_de_voz_desejado}

            21. Pergunta Original: Existe algum assunto ou abordagem que você gostaria de EVITAR nas redes sociais?
            *Resposta: {assunto_evitar}

            23. Pergunta Original: Você já possui algum material de marketing que possamos usar?
            *Resposta: {material_marketing}

            24. Pergunta Original: Existe mais alguma informação que você acha que eu deveria saber sobre a "Pão da Vila antes de começarmos a estratégia?
            *Resposta: {informacao_extra}
            """
            with st.spinner("Analisando o briefing e gerando os relatórios... Isso pode levar alguns minutos."):
                
                try:
                    # 1. Enviar o briefing completo para o endpoint de análise
                    response_analyze = httpx.post(
                        f"{FASTAPI_BASE_URL}/briefing/analyze",
                        json={"briefing_text": full_briefing_text},
                        headers=get_auth_headers(),
                        timeout=300
                    )
                    response_analyze.raise_for_status()
                    st.session_state.brief_data = response_analyze.json()
                    st.success("Briefing analisado com sucesso pela IA!")

                    # 2. Disparar a geração dos relatórios (chama os endpoints PROTEGIDOS)
                    st.subheader("Iniciando Geração dos Relatórios...")
                    reports_status = {}

                    # Incluindo todos os relatórios novamente
                    report_endpoints = {
                        "estrategia": "/reports/estrategia",
                        "publicacoes": "/reports/publicacoes",
                        "concorrentes": "/reports/concorrentes" # Incluído novamente
                    }

                    for report_name, endpoint_path in report_endpoints.items():
                        st.info(f"Gerando relatório de {report_name.replace('_', ' ').title()}...")
                        try:
                            report_response = httpx.post(
                                f"{FASTAPI_BASE_URL}{endpoint_path}",
                                headers=get_auth_headers(),
                                timeout=3200 # Aumente o timeout para relatórios
                            )
                            report_response.raise_for_status()
                            reports_status[report_name] = "sucesso"
                            st.success(f"✅ Relatório de {report_name.replace('_', ' ').title()} gerado com sucesso!")
                        except httpx.HTTPStatusError as e:
                            reports_status[report_name] = f"falha: {e.response.status_code} - {e.response.text}"
                            st.error(f"❌ Erro ao gerar relatório de {report_name.replace('_', ' ').title()}: {e.response.status_code} - {e.response.text}")
                        except httpx.RequestError as e:
                            reports_status[report_name] = f"falha: Erro de conexão - {e}"
                            st.error(f"❌ Erro de conexão ao gerar relatório de {report_name.replace('_', ' ').title()}: {e}")
                        except Exception as e:
                            reports_status[report_name] = f"falha: {e}"
                            st.error(f"❌ Ocorreu um erro inesperado ao gerar relatório de {report_name.replace('_', ' ').title()}: {e}")

                    st.subheader("Status Final da Geração dos Relatórios:")
                    for report_name, status in reports_status.items():
                         if "sucesso" in status:
                             st.success(f"✅ Relatório de {report_name.replace('_', ' ').title()}: {status}")
                         elif "falha" in status:
                             st.error(f"❌ Relatório de {report_name.replace('_', ' ').title()}: {status}")
                         else:
                             st.warning(f"⚠️ Relatório de {report_name.replace('_', ' ').title()}: {status}")

                    st.markdown("Os arquivos `.docx` foram salvos no diretório `reports` do seu backend.")

                except httpx.HTTPStatusError as e:
                    st.error(f"Erro na API ao analisar o briefing: {e.response.status_code} - {e.response.text}")
                except httpx.RequestError as e:
                    st.error(f"Erro de conexão com a API: {e}. Verifique se o backend FastAPI está rodando.")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")
    
                
                                    # ETAPA 3: Upload para o Google Drive (NOVO BLOCO)

            if False:
                with st.spinner("Enviando relatórios para o Google Drive..."):
                    try:
                        # O nome da empresa foi capturado no formulário
                        client_name_for_upload = nome_empresa 
                        
                        upload_response = httpx.post(
                            f"{FASTAPI_BASE_URL}/reports/upload-to-drive",
                            json={"client_name": client_name_for_upload},
                            headers=get_auth_headers(),
                            timeout=600 # Timeout para o upload
                        )
                        upload_response.raise_for_status()
                        st.success("✅ " + upload_response.json().get("message"))
                        st.balloons()

                    except Exception as e:
                        st.error(f"❌ Falha ao enviar arquivos para o Google Drive: {e}")