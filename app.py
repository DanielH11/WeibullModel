import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt

#ABRIR YAML, ARQUIVO CONTENDO OS REGISTROS DE USUÁRIOS
with open('config.yaml') as file:
  config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)
#FLAG DE USUÁRIO LOGADO
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#FLAG DE CADASTRO SENDO FEITO
if "sign_up" not in st.session_state:
    st.session_state.sign_up = False

#CONTAINER PARA LOGIN
def login():
  #DIVIDIR TELA EM DOIS
  col1, col2 = st.columns(2)
  col1.title("Modelo")
  col1.title("Weibull")
  #FORMULÁRIO
  col2.header("Faça seu login")
  email = col2.text_input("Email")
  senha = col2.text_input("Senha",type="password",placeholder="******")
  #BOTÃO PARA LOGAR
  b = col2.button("Logar")
  col2.header("", divider='gray')
  if b:
    with open('config.yaml', 'r') as f:
      data = yaml.full_load(f)
    #BUSCA NO YAML UM REGISTRO COMPATÍVEL AO INSERIDO
    for user in data['credentials']['usernames']:
      #SE EMAIL E SENHA COINCIDEREM
      if data['credentials']['usernames'][user]['email'] == email and bcrypt.checkpw(bytes(senha, "UTF-8"), bytes(data['credentials']['usernames'][user]['password'], "UTF-8")):
        #USUÁRIO LOGADO E REINICIAR
        st.session_state.logged_in = True
        st.rerun()
  col2.header("Não tem conta ainda?")
  if col2.button("Cadastrar-se"):
    #LEVAR AO CADASTRO
    st.session_state.sign_up = True
    st.rerun()

#DEFINIÇÃO DO CADASTRO
def cadastro():
  st.header("Cadastre-se")
  #FORMULÁRIO
  nome = st.text_input("Nome")
  email = st.text_input("Email a ser registrado")
  senha = st.text_input("Insira uma senha",type="password",placeholder="******")
  confirma_senha = st.text_input("Confirme a senha",type="password",placeholder="******")
  #CONCLUIR
  if st.button("Concluído"):
    #VERIFICA SE AS SENHAS BATEM
    if senha == confirma_senha:
      #INSERE NO YAML
      try:
        config['credentials']['usernames'][email] = {
          'email': email,
          'name': nome,
          'password': bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        }
        with open('config.yaml', 'w') as file:
          yaml.dump(config, file, default_flow_style=False)
      #CASO DÊ ERRADO
      except Exception as e:
        st.error(f"Erro ao cadastrar: {e}")
    else:
      #CASO DÊ ERRADO
      st.error("As senhas não coincidem")
    #CADASTRO FEITO E RETORNO
    st.success('User registered successfully')
    st.session_state.sign_up= False;
    st.rerun()

#APLICAÇÃO PRINCIPAL
def app():
  st.write("APP") 


#INÍCIO DO PROGRAMA E DIRECIONAMENTO
if st.session_state.sign_up:
  cadastro()
elif st.session_state.logged_in:
  app()
else:
  login()
