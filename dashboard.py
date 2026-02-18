import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- CONFIGURAÇÃO ---
try:
    DB_URL = st.secrets["DB_URL"]
except:
    DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

# CSS para destacar o Valor (+EV)
st.markdown("""
    <style>
    .ev-box { background-color: #004d00; color: white; padding: 5px; border-radius: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def carregar_dados():
    try:
        conn = psycopg2.connect(DB_URL)
        # Selecionamos a nova coluna odd_mercado
        query = "SELECT fixture_name, prob_over_2_5, fair_odd, odd_mercado, created_at FROM analysis_logs ORDER BY created_at DESC LIMIT 60"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return pd.DataFrame()

st.title("⚽ Edge Analytics - Inteligência de Valor")
st.write("Análise matemática comparada com as Odds da Bet365")

df = carregar_dados()

if not df.empty:
    # Cálculo de Valor: Diferença entre Odd Mercado e Odd Justa
    df['EV'] = df['odd_mercado'] - df['fair_odd']
    
    # Filtros
    st.sidebar.header("Filtros de Elite")
    so_valor = st.sidebar.checkbox("Mostrar apenas Valor (+EV)", value=True)
    
    if so_valor:
        df = df[df['odd_mercado'] > df['fair_odd']]

    # Métricas
    c1, c2 = st.columns(2)
    c1.metric("Oportunidades (+EV)", len(df))
    if not df.empty:
        c2.metric("Maior Desajuste", f"{df['EV'].max():.2f}")

    # Estilização da tabela
    def style_valor(row):
        return ['background-color: #052e16' if row['EV'] > 0 else '' for _ in row]

    st.write("### 💎 Grade de Apostas de Valor")
    st.dataframe(
        df.style.apply(style_valor, axis=1).format({
            'prob_over_2_5': '{:.1f}%',
            'fair_odd': '{:.2f}',
            'odd_mercado': '{:.2f}',
            'EV': '+{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhuma oportunidade encontrada. Rode o minerador!")

st.caption(f"Última varredura: {datetime.now().strftime('%H:%M')}")