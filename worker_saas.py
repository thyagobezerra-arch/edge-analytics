import requests
import psycopg2
from scipy.stats import poisson
import time
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
API_KEY = os.getenv("API_KEY", "a38db0f256a84b4c71d294ac0e213307")
DB_URL = os.getenv("DB_URL", "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres")

def calcular_poisson_over25(home_avg, away_avg):
    lambda_total = home_avg + away_avg
    prob_under = sum([poisson.pmf(i, lambda_total) for i in range(3)])
    return float((1 - prob_under) * 100)

def salvar_no_banco(fixture_name, prob, fair_odd, market_odd):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        query = """INSERT INTO analysis_logs (fixture_name, prob_over_2_5, fair_odd, odd_mercado) 
                   VALUES (%s, %s, %s, %s)"""
        cur.execute(query, (fixture_name, float(prob), float(fair_odd), float(market_odd)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"    ✅ Salvo: {fixture_name} (Mkt: {market_odd})")
    except Exception as e:
        print(f"    ❌ Erro ao salvar: {e}")

def rodar_minerador_pro():
    headers = {'x-rapidapi-key': API_KEY}
    hoje = datetime.now().strftime('%Y-%m-%d')
    print(f"🚀 Minerador Pro (+EV) Iniciado: {hoje}")
    
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    termos_proibidos = ["Friendly", "Amistoso", "Exhibition", "Junior", "U20", "U19", "Women"]

    try:
        response = requests.get(url, headers=headers).json()
        jogos = response.get('response', [])
        
        processados = 0
        for jogo in jogos:
            league = jogo['league']['name']
            if any(t in league for t in termos_proibidos): continue
            
            f_id = jogo['fixture']['id']
            home = jogo['teams']['home']['name']
            away = jogo['teams']['away']['name']

            # 1. Busca Odds Reais (Bet365)
            url_odds = f"https://v3.football.api-sports.io/odds?fixture={f_id}&bookmaker=8"
            odd_mkt = 0.0
            try:
                res_odds = requests.get(url_odds, headers=headers).json()
                bets = res_odds['response'][0]['bookmakers'][0]['bets']
                for b in bets:
                    if b['id'] == 5: # Over/Under
                        for val in b['values']:
                            if val['value'] == 'Over 2.5':
                                odd_mkt = float(val['odd'])
            except: odd_mkt = 0.0

            # 2. Processa apenas se houver Odd de Mercado
            if odd_mkt > 0:
                prob = calcular_poisson_over25(1.7, 1.3)
                odd_justa = round(100/prob, 2)
                
                salvar_no_banco(f"[{league}] {home} vs {away}", prob, odd_justa, odd_mkt)
                processados += 1
                time.sleep(1) # Delay para API
            
            if processados >= 20: break # Limite de seguranca

        print(f"🏁 Fim da rodada. {processados} oportunidades de valor encontradas.")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    rodar_minerador_pro()