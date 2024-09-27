import streamlit as st


# Função de autenticação
def login():

    # Adiciona o logo ao topo da página
    st.image("logo_site.png", use_column_width=True)

    # Obtém as credenciais do arquivo secrets.toml
    stored_username = st.secrets["credentials"]["username"]
    stored_password = st.secrets["credentials"]["password"]

    # Campos de entrada para o usuário e senha
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    # Validação das credenciais
    if st.button("Entrar"):
        if username == stored_username and password == stored_password:
            st.session_state['logged_in'] = True
        else:
            st.error("Usuário ou senha incorretos.")

# Verifica o estado de login
def is_authenticated():
    return st.session_state.get('logged_in', False)
