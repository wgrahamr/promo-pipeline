import os

from flask import Flask, request, render_template
import psycopg
from psycopg.types.json import Jsonb
from psycopg.rows import dict_row
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True, row_factory=dict_row)

@app.route('/waha', methods=['POST'])
def receber_webhook():
    dados = request.get_json()
    chat_id = dados['payload']['from']
    resultado = conn.execute("SELECT * FROM grupos_monitorados WHERE chat_id = %s AND ativo", (chat_id,)).fetchall()

    if not resultado:
        return "ignorado", 200

    conn.execute(
        "INSERT INTO mensagens_cruas (wa_message_id, chat_id, payload) VALUES (%s, %s, %s) ON CONFLICT (wa_message_id) DO NOTHING", (dados['payload']['id'], chat_id, Jsonb(dados['payload']))
    )
    return "ok", 200


@app.route("/")
def listar_promocoes():
    q = request.args.get("q", "").strip()
    periodo = request.args.get("periodo")

    condicoes = []
    parametros = {}

    if q:
        condicoes.append("p.nome_item ILIKE %(padrao)s")
        parametros["padrao"] = f"%{q}%"

    if periodo == "24h":
        condicoes.append("p.atualizada_em > now() - interval '24 hours'")

    where = "WHERE " + " AND ".join(condicoes) if condicoes else ""

    promocoes = conn.execute(
        f"""
        SELECT p.nome_item, p.preco_cheio, p.preco_desconto, p.cupom,
        p.loja, p.url, c.nome AS categoria, p.deadline,
        m.payload->'_data'->>'thumbnail' AS thumbnail
        FROM promocoes p
        LEFT JOIN categorias c ON c.id = p.categoria_id
        LEFT JOIN mensagens_cruas m ON m.id = p.mensagem_id
        {where}
        ORDER BY p.atualizada_em DESC
        LIMIT 50
        """,
        parametros,
    ).fetchall()

    return render_template("promocoes.html", promocoes=promocoes, q=q, periodo=periodo)
app.run(host="0.0.0.0", port=8080, debug=False)


