import streamlit as st
import os
from dotenv import load_dotenv
import psycopg2
from openai import OpenAI
from PIL import Image
import io
# --- FUNÇÃO DE CONEXÃO (MODO NUVEM NEON ☁️) ---
def get_db_connection():
    # ⚠️ IMPORTANTE: Apague o texto abaixo e cole o link que você copiou do Neon!
    url_do_banco = "postgres://neondb_owner:npg_HxAsIhy6q8n@ep-delicate-mud-ah3mkiw5-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
   
    return psycopg2.connect(url_do_banco)
    
# 1. Configurações de Página
st.set_page_config(page_title="BR House Imóveis", page_icon="🏡", layout="wide")


# --- 1. ESTILO CSS (Visual Portal + Upload) ---
def carregar_estilo_portal():
    st.markdown("""
    <style>
        /* === 1. TEMA VERDE === */
        .stButton > button, .stLinkButton > a {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }
        .stButton > button:hover, .stLinkButton > a:hover {
            background-color: #1e7e34 !important;
        }
        
        /* Upload Verde */
        [data-testid="stFileUploader"] {
            border: 2px dashed #28a745; background-color: #E8F5E9;
            padding: 15px; text-align: center; border-radius: 15px;
        }
        [data-testid="stFileUploader"] small { display: none; }
        [data-testid="stFileUploader"] button {
            background-color: #28a745 !important; color: transparent !important; border: none;
        }
        [data-testid="stFileUploader"] button::after {
            content: "📂 Selecionar"; color: white; position: absolute;
            left: 50%; top: 50%; transform: translate(-50%, -50%);
            font-weight: 700;
        }

        /* === 2. BANNER DE TOPO (HERO) - LINK NOVO === */
        .hero-container {
            /* Link novo e mais estável 👇 */
            background-image: url("https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=2053&auto=format&fit=crop");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            padding: 80px 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
            position: relative;
        }
        
        /* Sombra escura (O cinza que você viu) */
        .hero-container::before {
            content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.4); /* Um pouco mais transparente */
            border-radius: 15px;
        }
        .hero-title {
            font-size: 42px; font-weight: 800; position: relative; z-index: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5); margin-bottom: 10px;
        }
        .hero-subtitle {
            font-size: 18px; position: relative; z-index: 1;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        
        /* Títulos */
        h3 { color: #222222; font-weight: 800; }
    </style>

    <div class="hero-container">
        <div class="hero-title">O imóvel ideal para Morar ou Investir.</div>
        <div class="hero-subtitle">Busca Inteligente para encontrar a sua oportunidade.</div>
    </div>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÃO DE BANCO DE DADOS ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imoveis_v5 (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price NUMERIC,
            description TEXT,
            category TEXT,
            tipo_negocio TEXT,
            image_data BYTEA,
            is_opportunity BOOLEAN DEFAULT FALSE,
            embedding vector(1536)
        );
    """)
    conn.commit()
    conn.close()
def formatar_moeda(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"{valor}"

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def processar_imagem(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
    image.thumbnail((1024, 1024))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=85)
    return img_byte_arr.getvalue()

# --- LIGANDO O SISTEMA ---
carregar_estilo_portal()  # <--- Desenha o fundo e o visual
init_db()                 # <--- Conecta no banco de dados
# -------------------------

# Aqui embaixo deve estar o código que você achou:


# --- SIDEBAR ---
# --- SIDEBAR PREMIUM ---
with st.sidebar:
    # 1. Foto de Perfil Arredondada
    st.markdown("""
        <style>
        .profile-pic {
            display: block; margin-left: auto; margin-right: auto;
            border-radius: 50%; border: 3px solid #FF385C;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .text-center { text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # Tenta carregar a foto (certifique-se de ter o arquivo 'profile.jpg' ou mude o nome aqui)
    try:
        col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
        with col_img2:
            st.image("perfil.png", use_container_width=True) # Mantive o nome que vi no seu código
    except:
        st.warning("Foto não encontrada")

    # 2. Informações do Corretor
    st.markdown("""
        <div class='text-center'>
            <h2 style='margin-bottom: 0;'>Edmilson Cruz</h2>
            <p style='color: gray; margin-top: 0; font-size: 14px;'>Consultoria Imobiliária Premium</p>
            <p style='font-size: 12px; color: #555;'>CRECI/MT: 12345-F</p>
        </div>
        <hr style='margin: 10px 0;'>
    """, unsafe_allow_html=True)

    # 3. Menu de Navegação
    menu = st.radio(
        "Navegação",
        ["🏠 Início / Buscar", "🔐 Área do Corretor"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Botão WhatsApp Melhorado
    st.link_button(
        "💬 Falar no WhatsApp", 
        "https://wa.me/5565992456522", # Seu número já configurado
        use_container_width=True, 
        type="primary"
    )

    # 5. Rodapé com Redes Sociais
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Siga nas redes:**")
        c_insta, c_linkedin = st.columns(2)
        with c_insta:
            st.markdown("[📸 Instagram](https://instagram.com/edmilsoncruzimoveis)")
        with c_linkedin:
            st.markdown("[💼 LinkedIn](#)")
            
        st.markdown("---")
        st.caption("📍 Cuiabá - MT")
        st.caption("© 2026 BR House")

# --- LÓGICA DA PÁGINA INICIAL (A VITRINE) ---
if menu == "🏠 Início / Buscar":
    st.markdown("### 🔍 Encontre seu imóvel ideal")
    
    # 1. Barra de Pesquisa
    c_busca, c_btn = st.columns([4, 1])
    with c_busca:
        termo = st.text_input("Pesquisar", placeholder="Ex: Apartamento no centro...", label_visibility="collapsed")
    with c_btn:
        st.button("Buscar", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Conexão e Busca no Banco
    conn = get_db_connection()
    cur = conn.cursor()

    if termo:
        # Busca simples por texto no título ou descrição
        query = """
            SELECT title, price, description, category, tipo_negocio, image_data 
            FROM imoveis_v5 
            WHERE title ILIKE %s OR description ILIKE %s
        """
        cur.execute(query, (f'%{termo}%', f'%{termo}%'))
    else:
        # Se não tiver busca, traz tudo
        cur.execute("SELECT title, price, description, category, tipo_negocio, image_data FROM imoveis_v5")
    
    imoveis = cur.fetchall()
    conn.close()

    # 3. Exibição dos Cards
    if not imoveis:
        st.info("📭 O banco de dados está vazio. Vá na aba 'Área do Corretor' para cadastrar o primeiro imóvel!")
    else:
        # Cria um grid de 3 colunas
        cols = st.columns(3)
        for index, imovel in enumerate(imoveis):
            with cols[index % 3]: # Distribui entre as colunas
                with st.container(border=True):
                    # Tenta mostrar a imagem
                    if imovel[5]: # Se tiver dados da imagem
                        try:
                            st.image(io.BytesIO(imovel[5]), use_container_width=True)
                        except:
                            st.image("https://via.placeholder.com/300x200?text=Erro+Imagem", use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=Sem+Foto", use_container_width=True)

                    st.markdown(f"**{imovel[0]}**") # Título
                    st.caption(f"{imovel[3]} | {imovel[4]}") # Categoria e Tipo
                    st.markdown(f"### R$ {formatar_moeda(imovel[1])}") # Preço
                    
                    with st.expander("Ver detalhes"):
                        st.write(imovel[2]) # Descrição
                        st.button(f"Tenho Interesse", key=f"btn_{index}")



# --- ÁREA DO CORRETOR (COM CHECKBOX DE DESTAQUE) ---
# --- ÁREA DO CORRETOR ---
if menu == "🔐 Área do Corretor":
    st.subheader("Painel do Corretor - Novo Ativo")
    
    # Sem st.form para permitir atualização em tempo real
    with st.container():
        categoria_imovel = st.selectbox("Tipo", ["Residencial", "Lote em Condomínio", "Comercial", "Rural/Fazenda"])
        
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Título Comercial")
            tipo_negocio = st.radio("Modalidade", ["Venda", "Aluguel"], horizontal=True)
            
            # Campo de preço com atualização automática na legenda
            preco = st.number_input("Valor (R$)", min_value=0.0, step=1000.0, format="%.2f")
            st.caption(f"💰 Visualização no site: **R$ {formatar_moeda(preco)}**")
            
            with c2:
                foto = st.file_uploader("Foto Principal", type=["jpg", "png", "jpeg"])
                is_destaque = st.checkbox("🔥 Marcar como Oportunidade/Destaque na Home")

        descricao_livre = st.text_area("Descrição Técnica e Diferenciais", height=150)
        
        # Botão comum (fora de formulário)
        if st.button("Publicar Imóvel", type="primary"):
            if not titulo or not descricao_livre or not foto:
                st.warning("Preencha os campos obrigatórios (Título, Descrição e Foto).")
            else:
                with st.spinner("Publicando..."):
                    try:
                        img_bytes = processar_imagem(foto)
                        texto_para_ia = f"Categoria: {categoria_imovel}. Título: {titulo}. {descricao_livre}"
                        vector = get_embedding(texto_para_ia)
                        
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO imoveis_v5 (title, price, description, category, tipo_negocio, image_data, is_opportunity, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (titulo, preco, descricao_livre, categoria_imovel, tipo_negocio, img_bytes, is_destaque, vector)
                        )
                        conn.commit()
                        conn.close()
                        st.success("✅ Imóvel publicado com sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro: {e}")

    
    # --- SEÇÃO 1: VITRINE DE OPORTUNIDADES 🔥 ---
    st.subheader("🔥 Oportunidades em Destaque")
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, price, description, category, tipo_negocio, image_data FROM imoveis_v5 WHERE is_opportunity = TRUE ORDER BY id DESC LIMIT 3;")
    destaques = cur.fetchall()
    conn.close()
    
    if destaques:
        cols_destaque = st.columns(3)
        for i, imovel in enumerate(destaques):
            with cols_destaque[i]:
                with st.container(border=False):
                    if imovel[5]:
                        st.image(bytes(imovel[5]), use_container_width=True, style="height: 200px; object-fit: cover; border-radius: 12px 12px 0 0;")
                    
                    st.markdown("""<div style="padding: 15px;">""", unsafe_allow_html=True)
                    st.caption(f"⭐ {imovel[4]} • {imovel[3]}")
                    st.markdown(f"#### {imovel[0]}")
                    
                    # Preço Corrigido com Pontos
                    preco_formatado = formatar_moeda(imovel[1])
                    st.markdown(f"### R$ {preco_formatado}")
                    
                    with st.expander("Ver detalhes"):
                        st.write(imovel[2])
                        st.markdown(f'''<a href="https://wa.me/5565999999999?text=Olá, vi o destaque {imovel[0]}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px; width:100%; border-radius:5px; cursor:pointer;">📲 Chamar no WhatsApp</button></a>''', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Em breve, novas oportunidades exclusivas aqui.")

    st.markdown("---")

    # --- SEÇÃO 2: BUSCA INTELIGENTE ---
    st.subheader("🔍 Encontre o imóvel ideal")
    col_busca1, col_busca2 = st.columns([4, 1])
    with col_busca1:
        pergunta = st.text_input("Digite o que você procura...", placeholder="Ex: Casa em condomínio seguro para crianças...", label_visibility="collapsed")
    with col_busca2:
        btn_pesquisar = st.button("Pesquisar", type="primary")

    if btn_pesquisar and pergunta:
        with st.spinner("Buscando nas nossas bases..."):
            query_vector = get_embedding(pergunta)
            conn = get_db_connection()
            cur = conn.cursor()
            sql = "SELECT title, price, description, category, tipo_negocio, image_data FROM imoveis_v5 ORDER BY embedding <-> %s::vector LIMIT 5;"
            cur.execute(sql, (query_vector,))
            resultados = cur.fetchall()
            conn.close()
            
            if resultados:
                st.markdown("### Resultados da Busca")
                for i, imovel in enumerate(resultados):
                    with st.container():
                        c_img, c_info = st.columns([1.5, 3])
                        with c_img:
                            if imovel[5]: st.image(bytes(imovel[5]), use_container_width=True)
                        with c_info:
                            st.caption(f"{imovel[4]} • {imovel[3]}")
                            st.markdown(f"### {imovel[0]}")
                            
                            # Preço Corrigido aqui também
                            preco_formatado = formatar_moeda(imovel[1])
                            st.markdown(f"## R$ {preco_formatado}")
                            
                            with st.expander("Ver detalhes"):
                                st.write(imovel[2])
                    st.markdown("<br>", unsafe_allow_html=True)
            else:

                st.warning("Nenhum imóvel encontrado com esse perfil.")




