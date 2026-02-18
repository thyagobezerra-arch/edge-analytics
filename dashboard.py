import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Conexão segura com o Banco
try:
    DB_URL = st.secrets["DB_URL"]
except:
    DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

# Estilo para o Dashboard
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1c1f2e; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🎯 Menu de Análise")
mercado = st.sidebar.radio("Selecione o Mercado:", ["Escanteios (Over 9.5)", "Gols"])

def carregar_dados(tipo):
    try:
        conn = psycopg2.connect(DB_URL)
        # Puxamos os dados filtrando pelo mercado selecionado
        query = f"""SELECT fixture_name, probabilidade, odd_justa, odd_mercado, valor_ev 
                   FROM analysis_logs 
                   WHERE mercado_tipo LIKE '%{tipo}%' 
                   ORDER BY valor_ev DESC LIMIT 30"""
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# --- CONTEÚDO PRINCIPAL ---
st.title(f"🚀 Oportunidades: {mercado}")

df = carregar_dados(mercado)

if not df.empty:
    # Métricas de destaque
    c1, c2, c3 = st.columns(3)
    c1.metric("Análises", len(df))
    c2.metric("Oportunidades +EV", len(df[df['valor_ev'] > 0]))
    c3.metric("Maior Valor", f"+{df['valor_ev'].max():.2f}")

    st.write("### 📊 Grade de Entradas Sugeridas")
    
    # Formatação amigável
    df_show = df.copy()
    df_show.columns = ['Confronto', 'Probabilidade (%)', 'Odd Justa', 'Odd Bet365', 'Valor (+EV)']
    
    # Exibição com cores (Verde para lucro, Vermelho para prejuízo)
    st.dataframe(
        df_show.style.background_gradient(subset=['Valor (+EV)'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(f"Ainda não há dados minerados para {mercado}. Rode o seu robô no PC!")

st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")