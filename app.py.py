import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# --- Configurações de Layout ---
st.set_page_config(page_title="Painel YouTube Rafael - v6.1", layout="wide", page_icon="🔥")

# 1. SUA API KEY INTEGRADA
API_KEY = "AIzaSyDrsgH04u3kkqUjHNgAWfM3ZnJEZKL5MD0"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# --- FUNÇÕES DE LÓGICA ---

def gerar_titulos_estrategicos(titulos_base):
    if not titulos_base:
        return []
    tema = titulos_base[0].split('|')[0].strip()
    return [
        f"🚀 A estratégia secreta de {tema} que ninguém te conta (Passo a Passo)",
        f"💰 Como eu fiz meus primeiros resultados com {tema} usando apenas IA",
        f"⚠️ Pare de errar em {tema}: O guia definitivo para 2026"
    ]

def buscar_promissores(nicho, dias, meses_canal, max_videos, apenas_virais=False):
    data_video = (datetime.utcnow() - timedelta(days=dias)).isoformat() + 'Z'
    data_canal = (datetime.utcnow() - timedelta(days=meses_canal * 30)).isoformat() + 'Z'
    
    req = youtube.search().list(q=nicho, part="snippet", type="video", publishedAfter=data_video, maxResults=max_videos, order="viewCount")
    res = req.execute()
    
    lista = []
    for item in res.get('items', []):
        c_id = item['snippet']['channelId']
        v_id = item['id']['videoId']
        
        c_info = youtube.channels().list(part="snippet,statistics", id=c_id).execute()
        v_info = youtube.videos().list(part="statistics", id=v_id).execute()
        
        criacao = c_info['items'][0]['snippet']['publishedAt']
        
        # FILTRO DE DATA CORRIGIDO (Lida com milissegundos)
        try:
            # Tenta o formato com milissegundos, se falhar tenta o simples
            dt_obj = datetime.fromisoformat(criacao.replace('Z', '+00:00'))
            data_dt = dt_obj.strftime("%d/%m/%Y")
        except:
            data_dt = "Data Indisponível"
            
        if criacao > data_canal:
            subs = int(c_info['items'][0]['statistics'].get('subscriberCount', 1))
            views = int(v_info['items'][0]['statistics'].get('viewCount', 0))
            
            if apenas_virais and views < (subs * 1.5):
                continue
                
            lista.append({
                'Canal': item['snippet']['channelTitle'],
                'Vídeo': item['snippet']['title'],
                'Inscritos': subs,
                'Views': views,
                'Explosão': f"{round(views/subs, 1)}x" if subs > 0 else "N/A",
                'Link': f"https://www.youtube.com/watch?v={v_id}"
            })
    return pd.DataFrame(lista)

def buscar_thumbs(query, max_v):
    req = youtube.search().list(q=query, part="snippet", type="video", maxResults=max_v)
    res = req.execute()
    dados = []
    for item in res.get('items', []):
        dados.append({
            'Título': item['snippet']['title'],
            'Canal': item['snippet']['channelTitle'],
            'Thumb': item['snippet']['thumbnails']['high']['url'],
            'Link': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })
    return dados

# --- INTERFACE ---
with st.sidebar:
    st.title("🛠️ Painel do Rafael")
    aba = st.radio("Escolha a ferramenta:", ["Início", "Localizador de Canais", "Detector de Virais", "Análise de Thumbs"])
    st.divider()

if aba == "Início":
    st.title("Bem-vindo, Rafael! 👋")
    st.info("Selecione uma ferramenta ao lado para validar sua próxima estratégia.")

elif aba == "Localizador de Canais":
    st.title("🚀 Localizador de Canais Promissores")
    col1, col2 = st.columns(2)
    with col1: nicho = st.text_input("Nicho:", value="deep house")
    with col2: meses = st.slider("Idade máx. canal (meses):", 1, 36, 12)
    if st.button("Buscar Canais"):
        df = buscar_promissores(nicho, 30, meses, 20)
        st.dataframe(df, hide_index=True)

elif aba == "Detector de Virais":
    st.title("🔥 Detector de Tendências Virais")
    nicho_v = st.text_input("Qual tema você quer validar?")
    if st.button("Rastrear Oportunidades"):
        with st.spinner("Analisando..."):
            df_v = buscar_promissores(nicho_v, 30, 120, 30, apenas_virais=True)
            if not df_v.empty:
                st.success("Resultados encontrados!")
                st.dataframe(df_v, hide_index=True)
                st.divider()
                st.subheader("💡 Sugestão de Títulos (Copywriting)")
                sugestoes = gerar_titulos_estrategicos(df_v['Vídeo'].tolist())
                for sug in sugestoes: st.code(sug, language=None)
            else:
                st.warning("Nenhum viral detectado.")

elif aba == "Análise de Thumbs":
    st.title("🔍 Analisador de Thumbnails")
    busca_t = st.text_input("Pesquisar:")
    if st.button("Ver Thumbs"):
        resultados = buscar_thumbs(busca_t, 10)
        for r in resultados:
            c1, c2 = st.columns([1, 2])
            with c1: st.image(r['Thumb'])
            with c2:
                st.subheader(r['Título'])
                st.link_button("Abrir Vídeo", r['Link'])
            st.divider()