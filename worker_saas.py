import requests
import psycopg2
from scipy.stats import poisson
import time
from datetime import datetime
import os

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# No PC, ele usa as strings abaixo. Na nuvem, ele usaria 'os.environ'
API_KEY = os.getenv("API_KEY", "a38db0f256a84b4c71d294ac0e213307")
DB_URL = os.getenv("DB_URL", "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres")

def calcular_poisson_over25(home_avg, away_avg):
    lambda_total = home_avg + away_avg
    prob_under = sum([poisson.pmf(i, lambda_total) for i in range(3)])
    return float((1 - prob_under) * 100)

def salvar_no_banco(fixture_name, prob, fair_odd):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = "INSERT INTO analysis_logs (fixture_name, prob_over_2_5, fair_odd) VALUES (%s, %s, %s)"
        cur.execute(query, (fixture_name, float(prob), float(fair_odd)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"    ✅ Salvo: {fixture_name}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")

def rodar_varredura():
    headers = {'x-rapidapi-key': API_KEY}
    hoje = datetime.now().strftime('%Y-%m-%d')
    print(f"🌍 Iniciando Varredura Global: {hoje}...")
    
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    try:
        response = requests.get(url, headers=headers).json()
        jogos = response.get('response', [])
        
        for jogo in jogos[:20]: # Analisa os 20 primeiros
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']
            league = jogo['league']['name']
            
            prob = calcular_poisson_over25(1.7, 1.3)
            odd = round(100/prob, 2)
            
            salvar_no_banco(f"[{league}] {home} vs {away}", prob, odd)
            time.sleep(1)
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    rodar_varredura()