import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
try:
    DB_URL = st.secrets["DB_URL"]
except:
    # Backup para rodar localmente no VS Code
    DB_URL = "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# Configuração da Página
st.set_page_config(page_title="Edge Analytics Pro", page_icon="⚽", layout="wide")

# Estilização CSS para o Modo Dark
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
        # Filtro de 24 horas para manter o dashboard limpo
        query = f"""SELECT fixture_name, probabilidade, odd_justa, odd_mercado, valor_ev 
                   FROM analysis_logs 
                   WHERE mercado_tipo LIKE '%{tipo}%' 
                   AND created_at >= CURRENT_DATE - INTERVAL '1 day'
                   ORDER BY valor_ev DESC LIMIT 50"""
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro de conexão com o banco: {e}")
        return pd.DataFrame()

# --- SIDEBAR (BARRA LATERAL) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/53/53244.png", width=80)
st.sidebar.title("Edge Analytics")
st.sidebar.markdown("---")

mercado = st.sidebar.selectbox(
    "Filtro de Mercado", 
    ["Escanteios (Over 9.5)", "Gols"]
)

st.sidebar.info("As oportunidades são ordenadas automaticamente pelo maior Valor Esperado (+EV).")

# --- CORPO PRINCIPAL ---
st.title(f"💎 Ranking de Valor: {mercado}")
st.write("Análise matemática de alta precisão vs Odds do Mercado.")

df = carregar_dados(mercado)

if not df.empty:
    # Cálculo de ROI % para análise de investimento
    df['ROI %'] = (df['valor_ev'] / df['odd_justa']) * 100

    # Métricas de Resumo
    m1, m2, m3 = st.columns(3)
    m1.metric("Oportunidades (+EV)", len(df[df['valor_ev'] > 0]))
    m2.metric("ROI Máximo", f"{df['ROI %'].max():.1f}%")
    m3.metric("Maior Odd", f"{df['odd_mercado'].max():.2f}")

    st.markdown("---")
    st.write("### 📊 Grade de Entradas de Elite")
    
    # Renomeando colunas para o usuário final
    df_final = df.rename(columns={
        'fixture_name': 'Confronto',
        'probabilidade': 'Prob. (%)',
        'odd_justa': 'Odd Justa',
        'odd_mercado': 'Odd Bet365',
        'valor_ev': 'Vantagem (Pts)'
    })

    # Tenta aplicar o degradê (precisa do matplotlib no requirements.txt)
    try:
        st.dataframe(
            df_final.style.background_gradient(subset=['Vantagem (Pts)', 'ROI %'], cmap='Greens')
            .format({
                'Prob. (%)': '{:.1f}%', 
                'Odd Justa': '{:.2f}', 
                'Odd Bet365': '{:.2f}', 
                'Vantagem (Pts)': '+{:.2f}', 
                'ROI %': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    except Exception:
        # Se o matplotlib não estiver instalado, mostra a tabela limpa
        st.dataframe(df_final, use_container_width=True, hide_index=True)
        st.warning("Dica: Adicione 'matplotlib' ao seu arquivo requirements.txt para ativar as cores.")

else:
    st.warning(f"Nenhum jogo de {mercado} processado nas últimas 24h.")
    st.info("Execute o seu minerador no computador para atualizar os dados.")


st.caption(f"Sistema Edge Analytics | Atualizado em: {datetime.now().strftime('%H:%M:%S')}")
