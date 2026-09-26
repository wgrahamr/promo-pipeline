from flask import Flask, request
from psycopg import psycopg

app = Flask(__name__)

conn = psycopg.connect("postgresql://waha:oA0|.8Gjb31iq18S@localhost:5432/waha_app")

@app.route('/waha', methods=['POST'])
def receber_webhook():
    dados = request.get_json()
    print(dados)

    return "ok", 200

app.run(host="0.0.0.0", port=8080, debug=True)

