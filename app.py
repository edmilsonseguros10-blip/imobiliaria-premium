import streamlit as st
import os
import psycopg2
from openai import OpenAI
from PIL import Image
import io

# --- 1. CONFIGURAÇÕES DE SEGURANÇA (SECRETS) ---
# Aqui o código lê o que você salvou no Streamlit Cloud
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_db_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_pGbh9ZAc2iwf", # <--- Cole aqui a senha que você acabou de resetar
        host="ep-delicate-mud-ah3mkiw5-pooler.us-east-1.aws.neon.tech",
        port="5432",
        sslmode="require"
    )


# --- 2. CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="BR House Imóveis", page_icon="🏠", layout="wide")

# --- 3. ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        width: 100%;
    }
    .main-banner {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1600607687939-ce8a6c25118c");
        height: 300px;
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNÇÃO PARA CRIAR TABELA NO BANCO ---
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # --- ESTA É A LINHA QUE VOCÊ DEVE ADICIONAR ---
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS imoveis_v5 (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                category TEXT,
                tipo_negocio TEXT,
                image_data BYTEA,
                embedding vector(1536)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao inicializar banco: {e}")

# --- 5. FUNÇÃO DE EMBEDDING (IA) ---
def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

# --- INTERFACE DO PORTAL ---
st.markdown('<div class="main-banner"><h1>O imóvel ideal para Morar ou Investir</h1></div>', unsafe_allow_html=True)

# Inicializa o banco
init_db()

# Barra Lateral
with st.sidebar:
    st.image("perfil.png", width=100)
    st.title("Menu de Gestão")
    aba = st.radio("Escolha uma opção:", ["Ver Imóveis", "Cadastrar Novo"])

if aba == "Cadastrar Novo":
    st.subheader("📝 Cadastrar Imóvel")
    with st.form("form_cadastro", clear_on_submit=True):
        titulo = st.text_input("Título do Anúncio")
        preco = st.number_input("Preço (R$)", min_value=0.0)
        desc = st.text_area("Descrição Completa")
        cat = st.selectbox("Categoria", ["Casa", "Apartamento", "Terreno", "Comercial"])
        negocio = st.selectbox("Negócio", ["Venda", "Aluguel"])
        foto = st.file_uploader("Foto do Imóvel", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("Salvar no Portal"):
            if titulo and preco > 0:
                try:
                    img_bytes = foto.read() if foto else None
                    emb = get_embedding(f"{titulo} {desc} {cat}")
                    
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO imoveis_v5 (title, price, description, category, tipo_negocio, image_data, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (titulo, preco, desc, cat, negocio, img_bytes, emb))
                    conn.commit()
                    st.success("✅ Imóvel cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Preencha os campos obrigatórios.")

else:
    st.subheader("🔍 Imóveis Disponíveis")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, price, category, tipo_negocio, description, image_data FROM imoveis_v5 ORDER BY id DESC")
        imoveis = cur.fetchall()
        
        if not imoveis:
            st.info("Nenhum imóvel cadastrado ainda.")
        
        for imovel in imoveis:
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    if imovel[5]:
                        st.image(imovel[5], use_container_width=True)
                    else:
                        st.write("Sem foto")
                with col2:
                    st.write(f"### {imovel[0]}")
                    st.write(f"**{imovel[3]} - {imovel[2]}**")
                    st.write(f"💰 R$ {imovel[1]:,.2f}")
                    st.write(imovel[4])
                st.divider()
    except Exception as e:
        st.error(f"Erro ao buscar imóveis: {e}")





