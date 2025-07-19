# streamlit_app/master_app.py

import streamlit as st
import httpx
import json

FASTAPI_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(layout="centered", page_title="Master User Admin Panel")

# --- Gerenciamento de Autenticação para Master ---
if 'master_logged_in' not in st.session_state:
    st.session_state.master_logged_in = False
if 'master_auth_token' not in st.session_state:
    st.session_state.master_auth_token = None
if 'master_user_email' not in st.session_state:
    st.session_state.master_user_email = None
if 'is_master_admin' not in st.session_state:
    st.session_state.is_master_admin = False


def master_get_auth_headers():
    if st.session_state.master_logged_in and st.session_state.master_auth_token:
        return {"Authorization": f"Bearer {st.session_state.master_auth_token}"}
    return {}

def render_master_login_page():
    st.title("Login do Usuário Mestre")
    email = st.text_input("Email do Mestre", key="master_login_email")
    password = st.text_input("Senha do Mestre", type="password", key="master_login_password")

    if st.button("Entrar como Mestre", key="master_login_button"):
        try:
            response = httpx.post(
                f"{FASTAPI_BASE_URL}/auth/login",
                json={"email": email, "senha": password}
            )
            response.raise_for_status()
            token_data = response.json()
            st.session_state.master_auth_token = token_data["access_token"]
            st.session_state.master_user_email = email

            # Verificar se o usuário que logou é realmente um admin
            # Para isso, você pode precisar de um endpoint no backend para obter o perfil do usuário logado
            # Ou o token_data pode retornar o status admin, o que seria mais eficiente.
            # Por simplicidade, assumimos que o login bem-sucedido para este app significa que ele tem permissão de master.
            # Em um sistema robusto, você faria uma chamada para /api/v1/auth/me ou similar.
            st.session_state.is_master_admin = True # Assumindo que apenas admins usarão este app
            st.session_state.master_logged_in = True
            st.success("Login do Mestre bem-sucedido!")
            st.rerun()
        except httpx.HTTPStatusError as e:
            st.error(f"Erro de login: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

# --- Lógica Principal do Aplicativo Mestre ---
if not st.session_state.master_logged_in:
    render_master_login_page()
else:
    if not st.session_state.is_master_admin:
        st.error("Acesso negado. Esta área é restrita a usuários mestres.")
        if st.button("Sair"):
            st.session_state.master_logged_in = False
            st.session_state.master_auth_token = None
            st.session_state.master_user_email = None
            st.session_state.is_master_admin = False
            st.rerun()
    else:
        st.sidebar.success(f"Logado como Mestre: {st.session_state.master_user_email}")
        if st.sidebar.button("Sair do Mestre", key="master_logout_button"):
            st.session_state.master_logged_in = False
            st.session_state.master_auth_token = None
            st.session_state.master_user_email = None
            st.session_state.is_master_admin = False
            st.rerun()

        st.title("🔑 Painel Administrativo do Usuário Mestre")
        st.markdown("Use este painel para registrar novos usuários que terão acesso ao aplicativo principal de análise.")

        st.header("Registrar Novo Usuário")
        with st.form("register_new_user_form"):
            new_user_name = st.text_input("Nome do Novo Usuário")
            new_user_email = st.text_input("Email do Novo Usuário")
            new_user_password = st.text_input("Senha do Novo Usuário", type="password")
            is_admin = st.checkbox("Conceder privilégios de Administrador?", value=False) # Permite criar outro admin
            submit_button = st.form_submit_button("Registrar Usuário")

            if submit_button:
                if new_user_name and new_user_email and new_user_password:
                    try:
                        response = httpx.post(
                            f"{FASTAPI_BASE_URL}/auth/master-register-user",
                            json={
                                "nome": new_user_name,
                                "email": new_user_email,
                                "senha": new_user_password,
                                "admin": is_admin
                            },
                            headers=master_get_auth_headers()
                        )
                        response.raise_for_status()
                        st.success(f"Usuário '{new_user_email}' registrado com sucesso!")
                        # Limpar formulário após o registro
                        st.session_state["new_user_name"] = ""
                        st.session_state["new_user_email"] = ""
                        st.session_state["new_user_password"] = ""
                        st.rerun() # Recarregar para limpar os campos
                    except httpx.HTTPStatusError as e:
                        st.error(f"Erro ao registrar usuário: {e.response.status_code} - {e.response.text}")
                    except Exception as e:
                        st.error(f"Ocorreu um erro: {e}")
                else:
                    st.warning("Por favor, preencha todos os campos para registrar o novo usuário.")