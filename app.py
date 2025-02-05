import streamlit as st
from streamlit.elements.heading import Divider
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import bcrypt
import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt 
import seaborn as sn

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

if "data" not in st.session_state:
    st.session_state.data = np.array([])

if "n_count" not in st.session_state:
    st.session_state.n_count = 0

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
    try:
      for user in data['credentials']['usernames']:
        #SE EMAIL E SENHA COINCIDEREM
        if data['credentials']['usernames'][user]['email'] == email and bcrypt.checkpw(bytes(senha, "UTF-8"), bytes(data['credentials']['usernames'][user]['password'], "UTF-8")):
          #USUÁRIO LOGADO E REINICIAR
          st.session_state.logged_in = True
          st.rerun()
    except:
      st.error("Usuário e senha não batem")
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

def weib(x,n,a):
  return (a / n) * (x / n)**(a - 1) * np.exp(-(x / n)**a)

def mean_rank(i):
  return (i-0.3)/(st.session_state.n_count+0.4)

def y(t):
  aux = 1-mean_rank(t)
  auxx = np.log(aux)
  auxxx = np.log(-auxx)
  return np.log(-np.log(1-mean_rank(t)))

def soma_x(data):
  soma=0;
  for a in data:
    x = np.log(a)
    soma += x
  return soma

def soma_y(data):
  soma=0;
  for i in range(st.session_state.n_count):
    soma += y(i+1)
  return soma

def soma_xx(data):
  soma=0;
  for a in data:
    x = np.log(a)
    soma += x*x
  return soma  

def xpory(data):
  i=1
  soma=0;
  for a in data:
    x = np.log(a)
    soma += x*y(i)
    i+=1
  return soma

#APLICAÇÃO PRINCIPAL
def app():
  #Número de colunas
  colunas = 5

  st.header("Inserir manualmente dados de tempo de vida")
  col_a, col_b = st.columns(2)

  add_value = col_a.number_input("Adicionar tempo de vida", step=1.0, value=None,format="%f ", key="add_input")

  if col_a.button("Adicionar"):
    if not np.isnan(add_value):
      st.session_state.data = np.append(st.session_state.data, add_value)
      st.session_state.data = np.sort(st.session_state.data)
      st.success(f"Valor {add_value} adicionado!")

  remove_value = col_a.number_input("Remover um tempo de vida", step=1.0, value=None, format="%f ", key="remove_input")

  if col_a.button("Remover"):
    if not np.isnan(remove_value):
      matches = np.isclose(st.session_state.data, remove_value, atol=1e-9)
      if np.any(matches):
        first_match_idx = np.where(matches)[0][0]
        st.session_state.data = np.delete(st.session_state.data, first_match_idx)
        st.session_state.data = np.sort(st.session_state.data)
        st.success(f"Valor {remove_value} removido!")
      else:
        st.warning(f"Valor {remove_value} não encontrado!")

  st.header("Dados")
  data = st.file_uploader("Carregar dataset. Atenção: ao carregá-lo, sobrescreverá os dados anteriores.")
  if data:
    try:
      data = pd.read_csv(data, header=None).to_numpy().flatten()
      data = np.sort(data)
      st.session_state.data = data
    except:
      st.error("Não é um arquivo csv")
  if st.button("Calcular a distribuição Weibull"):
    data = st.session_state.data
  
    st.session_state.n_count = len(data)
    n_count = st.session_state.n_count
    a = (n_count*xpory(data)-soma_x(data)*soma_y(data))/(n_count*soma_xx(data)-soma_x(data)*soma_x(data))
    b = (soma_xx(data)*soma_y(data)-soma_x(data)*xpory(data))/(n_count*soma_xx(data)-soma_x(data)*soma_x(data))
    n = np.exp(-b / a)
    beta = a
    x = np.linspace(data.min(), data.max(), 1000)
    weibull_d = weib(x, n, beta)

    # Plot o histrograma e a distribuição
    bin_size = (data.max()-data.min())/n_count
    fig, ax = plt.subplots()
    ax.hist(data, bins=16, density=True, alpha=0.5, label="Histograma")
    ax.plot(x, weibull_d, label="Weibull")
    ax.set_xlabel("Tempo de vida")
    ax.set_ylabel("Densidade")
    plt.grid(True)
    st.pyplot(fig)

    st.write("Beta: ", str(beta))
    st.write("N: ", str(n))


  chunks = [st.session_state.data[i:i+colunas] for i in range(0, len(st.session_state.data), colunas)]
  df = pd.DataFrame(chunks).add_prefix("Coluna ")
  col_b.dataframe(df, height=280, hide_index=True)

#INÍCIO DO PROGRAMA E DIRECIONAMENTO
if st.session_state.sign_up:
  cadastro()
elif st.session_state.logged_in:
  app()
else:
  login()
