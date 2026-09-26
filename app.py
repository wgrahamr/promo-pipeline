from flask import Flask, request
import psycopg

app = Flask(__name__)

conn = psycopg.connect("postgresql://waha:oA0|.8Gjb31iq18S@localhost:5432/waha_app")

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

