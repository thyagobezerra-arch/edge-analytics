import streamlit as st
import pandas as pd
import psycopg2

# Conexão segura
try: DB_URL = st.secrets["DB_URL"]
except: DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

# Menu de Navegação
st.sidebar.title("🎮 Painel de Controle")
categoria = st.sidebar.radio("Escolha o Mercado:", ["Gols", "Escanteios (Over 9.5)"])

def carregar_dados(tipo):
    try:
        conn = psycopg2.connect(DB_URL)
        query = f"SELECT fixture_name, probabilidade, odd_justa, odd_mercado, valor_ev FROM analysis_logs WHERE mercado_tipo LIKE '%{tipo}%' ORDER BY created_at DESC LIMIT 40"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except: return pd.DataFrame()

st.title(f"🚀 Oportunidades em {categoria}")

df = carregar_dados(categoria)

if not df.empty:
    # Filtro de Valor Positivo
    df_valor = df[df['valor_ev'] > 0]
    
    col1, col2 = st.columns(2)
    col1.metric("Análises Totais", len(df))
    col2.metric("Oportunidades +EV", len(df_valor))

    st.write("### 📊 Tabela de Valor")
    # Estilizando a tabela para destacar o lucro
    st.dataframe(
        df.style.background_gradient(subset=['valor_ev'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(f"O minerador ainda não encontrou oportunidades para {categoria} hoje.")