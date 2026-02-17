import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
try:
    # Tenta pegar das configurações seguras da nuvem
    DB_URL = st.secrets["DB_URL"]
except Exception:
    # Se falhar (rodando local), usa a sua URL padrão
    DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# Configurações de Design do Streamlit
st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #4e5d6c; }
    </style>
    """, unsafe_allow_html=True)

def carregar_dados():
    try:
        conn = psycopg2.connect(DB_URL)
        query = "SELECT fixture_name, prob_over_2_5, fair_odd, created_at FROM analysis_logs ORDER BY created_at DESC LIMIT 100"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return pd.DataFrame()

# --- INTERFACE ---
st.title("⚽ Edge Analytics Pro")
st.write(f"📅 **Data do Sistema:** {datetime.now().strftime('%d/%m/%Y')}")

# Barra Lateral (Filtros)
st.sidebar.header("⚙️ Configurações")
min_prob = st.sidebar.slider("Probabilidade Mínima (%)", 0, 100, 50)
search = st.sidebar.text_input("🔍 Buscar Time ou Liga")

df = carregar_dados()

if not df.empty:
    df_filtrado = df[df['prob_over_2_5'] >= min_prob]
    if search:
        df_filtrado = df_filtrado[df_filtrado['fixture_name'].str.contains(search, case=False)]

    # Métricas de Resumo
    c1, c2, c3 = st.columns(3)
    c1.metric("Jogos Analisados", len(df))
    c2.metric("Filtro Ativo", len(df_filtrado))
    if not df_filtrado.empty:
        c3.metric("Melhor Probabilidade", f"{df_filtrado['prob_over_2_5'].max()}%")

    st.markdown("---")

    # Exibição da Tabela com Estilo
    st.write("### 📊 Grade de Oportunidades")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
else:
    st.info("Aguardando minerador enviar dados...")

st.sidebar.caption("v1.2.0 | João Pessoa - PB")