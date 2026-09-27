import os
import json

import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)

resultado = conn.execute("SELECT id, payload->>'body' AS texto FROM mensagens_cruas WHERE NOT processada").fetchall()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)

INSTRUCOES = """
                Você extrai dados de mensagens de grupos de promoções do WhatsApp.
                Responda APENAS com um JSON, com exatamente estes campos:

                - eh_promocao: true se a mensagem anuncia um produto com preço; false caso contrário
                - nome_item: nome do produto (texto)
                - preco_cheio: preço original, como número (ex.: 449), ou null
                - preco_desconto: preço promocional, como número (ex.: 199)
                - cupom: código do cupom, ou null
                - url: link da promoção
                - loja: nome da loja, ou null
                - meio_pagamento: ex.: Pix, cartão, boleto; ou null se não mencionado

                Se eh_promocao for false, todos os outros campos devem ser null.
                Nunca invente informações que não estejam na mensagem.
                """

for mensagem_id, texto in resultado:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": INSTRUCOES
             
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        temperature=0,
        reasoning_effort="low",
    )

    promocao = json.loads(completion.choices[0].message.content)
    print('Dicionário: ', promocao)
    print('É promoção: ', promocao['eh_promocao'])
    print('Preço: ', promocao['preco_desconto'])