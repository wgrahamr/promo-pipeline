import os

from flask import Flask, request
import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

app = Flask(__name__)

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)

@app.route('/waha', methods=['POST'])
def receber_webhook():
    dados = request.get_json()
    chat_id = dados['payload']['from']
    resultado = conn.execute("SELECT * FROM grupos_monitorados WHERE chat_id = %s AND ativo", (chat_id,)).fetchall()

    if not resultado:
        return "ignorado", 200

    print(dados)
    return "ok", 200

app.run(host="0.0.0.0", port=8080, debug=True)

