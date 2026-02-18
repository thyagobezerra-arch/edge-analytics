import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
try:
    DB_URL = st.secrets["DB_URL"]
except:
    DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

# Estilização CSS Dark Pro
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
    .stDataFrame { border: 1px solid #31333f; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def carregar_dados(tipo):
    try:
        conn = psycopg2.connect(DB_URL)
        # Ordenamos pelo valor_ev para o melhor aparecer no topo
        query = f"""SELECT fixture_name, probabilidade, odd_justa, odd_mercado, valor_ev 
                   FROM analysis_logs 
                   WHERE mercado_tipo LIKE '%{tipo}%' 
                   AND created_at >= NOW() - INTERVAL '24 HOURS'
                   ORDER BY valor_ev DESC LIMIT 50"""
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/53/53244.png", width=100)
st.sidebar.title("Edge Analytics")
mercado = st.sidebar.selectbox("Filtro de Mercado", ["Escanteios (Over 9.5)", "Gols"])
st.sidebar.markdown("---")
st.sidebar.info("As oportunidades são ordenadas pelo maior Valor Esperado (+EV).")

# --- CORPO PRINCIPAL ---
st.title(f"💎 Ranking de Valor: {mercado}")

df = carregar_dados(mercado)

if not df.empty:
    # Cálculo de ROI Estimado (Apenas para exibição)
    df['ROI %'] = (df['valor_ev'] / df['odd_justa']) * 100

    # Métricas de Topo
    m1, m2, m3 = st.columns(3)
    m1.metric("Oportunidades Hoje", len(df))
    m2.metric("Melhor Odd Mercado", f"{df['odd_mercado'].max():.2f}")
    m3.metric("ROI Máximo Detectado", f"{df['ROI %'].max():.1f}%")

    st.write("### 📊 Grade de Entradas de Elite")
    
    # Renomeando para o usuário final
    df_final = df.rename(columns={
        'fixture_name': 'Confronto',
        'probabilidade': 'Prob. (%)',
        'odd_justa': 'Odd Justa',
        'odd_mercado': 'Odd Bet365',
        'valor_ev': 'Vantagem (Pts)'
    })

    # Aplicando o gradiente de verde (mais escuro = melhor)
    st.dataframe(
        df_final.style.background_gradient(subset=['Vantagem (Pts)', 'ROI %'], cmap='Greens')
        .format({'Prob. (%)': '{:.1f}%', 'Odd Justa': '{:.2f}', 'Odd Bet365': '{:.2f}', 'Vantagem (Pts)': '+{:.2f}', 'ROI %': '{:.1f}%'}),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning(f"Ainda não encontramos entradas de valor para {mercado} nas últimas 24h.")

st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - João Pessoa/PB")