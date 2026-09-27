import json
import os
import time

import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)
MAX_TENTATIVAS = 5

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
                - categoria_id: o número da categoria que melhor descreve o produto, escolhido da lista de categorias abaixo
                - deadline: data e hora em que a promoção termina, no formato ISO 8601 com fuso -03:00 (ex.: 2026-09-30T23:59:00-03:00), ou null se a mensagem não indicar prazo. Use a data de envio para interpretar expressões como "hoje", "amanhã" ou "até meia-noite".

                Se eh_promocao for false, todos os outros campos devem ser null.
                Nunca invente informações que não estejam na mensagem.
                """

while True:
    resultado = conn.execute("SELECT id, payload->>'body' AS texto, recebida_em AT TIME ZONE 'America/Sao_Paulo' FROM mensagens_cruas WHERE NOT processada AND tentativas < %s ORDER BY id", (MAX_TENTATIVAS,)).fetchall()
    categorias = conn.execute("SELECT * FROM categorias").fetchall()
    lista_categorias = "\n".join(f"{id_cat}: {nome}" for id_cat, nome in categorias)
    print('Mensagens sendo processadas: ', len(resultado))
    for mensagem_id, texto, recebida_em in resultado:
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": INSTRUCOES + "\n\nCategorias:\n" + lista_categorias                 
                    },

                    {
                        "role": "user",
                        "content": f"Data de envio: {recebida_em}\n\nMensagem:\n{texto}"
                    }
                ],
                temperature=0,
                reasoning_effort="low",
                response_format={"type": "json_object"},
            )

            promocao = json.loads(completion.choices[0].message.content)
            print('Dicionário: ', promocao)
            print('É promoção: ', promocao['eh_promocao'])
            print('Preço: ', promocao['preco_desconto'])
            if promocao['eh_promocao']:
                conn.execute(
                    """
                    INSERT INTO promocoes (mensagem_id, nome_item, preco_cheio, preco_desconto, cupom, url, loja, meio_pagamento, categoria_id, deadline) VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET 
                        
                        mensagem_id = EXCLUDED.mensagem_id,
                        nome_item = EXCLUDED.nome_item,
                        preco_cheio = EXCLUDED.preco_cheio,
                        preco_desconto = EXCLUDED.preco_desconto,
                        cupom = EXCLUDED.cupom,
                        loja = EXCLUDED.loja,
                        meio_pagamento = EXCLUDED.meio_pagamento,
                        categoria_id = EXCLUDED.categoria_id,
                        deadline = EXCLUDED.deadline,
                        atualizada_em = NOW();
                        """
                        ,
                        (
                        mensagem_id,
                        promocao['nome_item'],
                        promocao['preco_cheio'],
                        promocao['preco_desconto'],
                        promocao['cupom'],
                        promocao['url'],
                        promocao['loja'],
                        promocao['meio_pagamento'],
                        promocao['categoria_id'],
                        promocao['deadline']
                        )
                    )
            conn.execute("UPDATE mensagens_cruas SET processada = true WHERE id = %s", (mensagem_id,))
        except Exception as erro:
            print("Erro ao processar mensagens:", mensagem_id, erro)
            conn.execute("UPDATE mensagens_cruas SET tentativas = tentativas + 1, ultimo_erro = %s WHERE id = %s", (str(erro), mensagem_id))
        time.sleep(2)  # Aguarda 2 segundos antes de tentar novamente
    time.sleep(120)  # Aguarda 120 segundos antes de verificar novamente