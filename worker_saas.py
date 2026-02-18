import requests
import psycopg2
import time
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
API_KEY = os.getenv("API_KEY", "a38db0f256a84b4c71d294ac0e213307")
DB_URL = os.getenv("DB_URL", "postgresql://postgres.vbxmtclyraxmhvfcnfee:0LMMYBrja3phgofg@aws-1-sa-east-1.pooler.supabase.com:6543/postgres")

def salvar_no_banco_universal(fixture, tipo, prob, justa, mercado):
    try:
        ev = mercado - justa
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        # Note: Agora enviamos 'prob' e 'justa' para as colunas antigas e novas para garantir compatibilidade
        query = """INSERT INTO analysis_logs (fixture_name, mercado_tipo, probabilidade, odd_justa, odd_mercado, valor_ev, prob_over_2_5, fair_odd) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(query, (fixture, tipo, float(prob), float(justa), float(mercado), float(ev), float(prob), float(justa)))
        conn.commit()
        cur.close()
        conn.close()
        print(f"    📈 {tipo} salvo: {fixture} | Mkt: {mercado}")
    except Exception as e:
        print(f"    ❌ Erro ao salvar: {e}")

def rodar_minerador_escanteios():
    headers = {'x-rapidapi-key': API_KEY}
    hoje = datetime.now().strftime('%Y-%m-%d')
    print(f"🚩 Minerador de ESCANTEIOS: {hoje}")
    
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    try:
        response = requests.get(url, headers=headers).json()
        jogos = response.get('response', [])
        
        count = 0
        for jogo in jogos:
            f_id = jogo['fixture']['id']
            nome_jogo = f"{jogo['teams']['home']['name']} vs {jogo['teams']['away']['name']}"

            # Busca Odds
            url_odds = f"https://v3.football.api-sports.io/odds?fixture={f_id}&bookmaker=8"
            odd_mkt = 0.0
            try:
                res_odds = requests.get(url_odds, headers=headers).json()
                for b in res_odds['response'][0]['bookmakers'][0]['bets']:
                    if "Corners" in b['name']:
                        for v in b['values']:
                            if v['value'] == 'Over 9.5': odd_mkt = float(v['odd'])
            except: continue

            if odd_mkt > 0:
                prob = 54.0 # Base estatística
                odd_justa = round(100/prob, 2)
                salvar_no_banco_universal(nome_jogo, "Escanteios (Over 9.5)", prob, odd_justa, odd_mkt)
                count += 1
                time.sleep(1)

            if count >= 20: break
        print("🏁 Concluído!")
    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    rodar_minerador_escanteios()