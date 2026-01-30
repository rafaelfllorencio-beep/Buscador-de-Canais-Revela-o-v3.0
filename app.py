import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd

# 1. Configuração Visual do App (Estilo Minimalista)
st.set_page_config(page_title="YouTube Growth Finder Pro", layout="wide")

st.title("💎 Buscador de Canais Revelação v3.0")
st.markdown("Identifique tendências visuais e canais em ascensão rapidamente.")

# 2. Barra Lateral - Configurações
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    api_key = st.text_input("Sua YouTube API Key", type="password")
    nicho = st.text_input("Nicho", placeholder="Ex: Oração, Luxo, Deep House...")
    
    dias_videos = st.slider("Vídeos postados nos últimos X dias", 1, 90, 30)
    idade_canal_meses = st.slider("Idade máxima do canal (meses)", 1, 60, 12)
    max_resultados = st.number_input("Analisar quantos vídeos?", 10, 50, 20)
    
    st.divider()
    st.info("💡 Foco visual: Analise as thumbnails para entender o clique.")

# 3. Função de Busca
def get_youtube_data(api_key, query, days, max_ch_age_months, max_results):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        date_threshold = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        search_res = youtube.search().list(
            q=query, part='snippet', type='video', order='viewCount',
            publishedAfter=date_threshold, maxResults=max_results
        ).execute()

        results = []
        for item in search_res.get('items', []):
            channel_id = item['snippet']['channelId']
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            # Pega a URL da thumbnail (tamanho padrão/médio)
            thumb_url = item['snippet']['thumbnails']['default']['url']
            
            ch_res = youtube.channels().list(part='snippet,statistics', id=channel_id).execute()['items'][0]
            
            raw_date = ch_res['snippet']['publishedAt'][:19]
            creation_date = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S')
            ch_age_days = (datetime.utcnow() - creation_date).days
            
            if ch_age_days <= (max_ch_age_months * 30):
                subs = int(ch_res['statistics'].get('subscriberCount', 0))
                views = int(ch_res['statistics'].get('viewCount', 0))
                virality_score = round(views / max(subs, 1), 2)
                
                results.append({
                    "Capa": thumb_url,
                    "Canal": ch_res['snippet']['title'],
                    "Vídeo Viral": video_title,
                    "Inscritos": subs,
                    "Views Totais": views,
                    "Score Viral": virality_score,
                    "Criado em": creation_date.strftime('%d/%m/%Y'),
                    "Link": f"https://www.youtube.com/watch?v={video_id}"
                })
        return results
    except Exception as e:
        st.error(f"Erro: {e}")
        return []

# 4. Exibição com Configuração de Imagem
if st.sidebar.button("🔍 Iniciar Mineração"):
    if not api_key or not nicho:
        st.warning("Preencha a API Key e o Nicho.")
    else:
        with st.spinner('Minerando dados visuais...'):
            data = get_youtube_data(api_key, nicho, dias_videos, idade_canal_meses, max_resultados)
            
            if data:
                df = pd.DataFrame(data)
                df = df.sort_values(by="Score Viral", ascending=False)
                
                # Botão de Download
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Lista (CSV)", csv, f"canais_{nicho}.csv", "text/csv")
                
                # Configuração para mostrar a imagem na tabela
                st.dataframe(
                    df,
                    column_config={
                        "Capa": st.column_config.ImageColumn("Thumbnail", help="Capa do vídeo viral"),
                        "Link": st.column_config.LinkColumn("Assistir")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum canal recente encontrado.")