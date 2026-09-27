# promo-pipeline

Pipeline que monitora grupos de promoções do WhatsApp, guarda cada mensagem recebida e usa IA generativa para transformar texto livre em dados estruturados: produto, preço, cupom, link e loja.

> Projeto de estudo. O objetivo é entender cada peça do processo: webhooks, bancos de dados, integração com LLMs e automação.

---

## O problema

Grupos de promoções postam dezenas de ofertas por dia, em texto livre, cada uma escrita de um jeito:

```
QUEM NÃO COMPROU É MALUCO
menor preço no coringa da nike

Tênis Nike Sb Chron 2 Canvas (37 ao 44)

De R$ 449 por R$ 199

Loja Oficial Nike
https://tidd.ly/3FUX0Cw
```

Muitos desses grupos usam mensagens temporárias, então as ofertas somem em poucos dias. E não há como pesquisar, filtrar ou comparar preços no histórico.

## A solução

Cada mensagem vira uma linha consultável no banco:

| nome_item | preco_cheio | preco_desconto | cupom | loja | url |
|---|---|---|---|---|---|
| Tênis Nike Sb Chron 2 Canvas | 449.00 | 199.00 | — | Loja Oficial Nike | https://tidd.ly/3FUX0Cw |

Com isso, dá para responder perguntas como "quais tênis abaixo de R$ 200 apareceram esta semana?" ou "esse produto já esteve mais barato?".

---

## Arquitetura

```mermaid
flowchart LR
    W[WhatsApp] --> H[WAHA]
    H -- webhook POST --> A[app.py<br/>Flask]
    A -- filtra grupo e grava --> M[(mensagens_cruas)]
    M -- processada = false --> P[processador.py]
    P -- body --> G[Groq LLM]
    G -- JSON --> P
    P -- insere ou atualiza --> PR[(promocoes)]
```

O sistema é dividido em duas fases independentes, ligadas pela coluna `processada`:

1. **Ingestão (`app.py`).** O WAHA avisa o webhook a cada mensagem nova. O webhook confere se o grupo está em `grupos_monitorados` e grava o payload completo em `mensagens_cruas`. Ele é rápido e não interpreta nada.
2. **Processamento (`processador.py`).** Busca as mensagens ainda não processadas, envia só o texto para a IA, recebe um JSON estruturado e grava em `promocoes`. Por fim, marca a mensagem como processada.

### Por que separar em duas fases

- **Velocidade.** O webhook responde em milissegundos. Uma chamada à IA leva segundos, e o WAHA poderia interpretar a demora como falha e reenviar a mensagem.
- **Resiliência.** Se a IA estiver fora do ar, as mensagens continuam sendo guardadas e esperam na fila.
- **Reprocessamento.** Como a mensagem original fica salva, é possível melhorar as instruções da IA e reprocessar o histórico.

---

## Stack

| Peça | Tecnologia | Papel |
|---|---|---|
| Conexão com o WhatsApp | [WAHA](https://waha.devlike.pro/) (Docker) | Expõe o WhatsApp como API e dispara webhooks |
| Banco de dados | PostgreSQL 16 (Docker) | Armazena mensagens e promoções |
| Webhook | Python + Flask | Recebe e filtra as mensagens |
| Driver do banco | psycopg 3 | Conexão Python ↔ Postgres |
| IA | Groq (`openai/gpt-oss-120b`) | Extrai os dados estruturados do texto |
| Configuração | python-dotenv | Lê segredos do `.env` |

---

## Banco de dados

| Tabela | Conteúdo |
|---|---|
| `grupos_monitorados` | Grupos cujas mensagens devem ser salvas. A coluna `ativo` liga ou desliga o monitoramento sem apagar o registro. |
| `mensagens_cruas` | Cópia fiel de cada mensagem recebida (`payload` em `jsonb`), com a flag `processada`. |
| `promocoes` | Dados extraídos pela IA. A `url` é única: repostagens atualizam a promoção existente. |
| `categorias` | Categorias de produtos. |

A estrutura completa está em [`migrations/`](migrations/). Cada mudança no banco é um arquivo numerado (`001_inicial.sql`, `002_...sql`), aplicado em ordem.

### Decisões de desenho

- **Idempotência.** `wa_message_id` é `UNIQUE`, e o `INSERT` usa `ON CONFLICT DO NOTHING`. Se o WAHA reenviar uma mensagem, ela não é duplicada.
- **Dado cru preservado.** O payload inteiro é guardado. Só o `body` é enviado à IA, o que reduz custo, ruído e exposição de dados pessoais.
- **Repostagens atualizam.** `ON CONFLICT (url) DO UPDATE` mantém a promoção com o preço mais recente e registra a mudança em `atualizada_em`.
- **Promoção exige preço.** Mensagens sem preço são marcadas como processadas, mas não entram em `promocoes`.

---

## Como rodar

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- Uma chave de API do [Groq](https://console.groq.com/keys) (o plano gratuito é suficiente)

### 1. Configurar o ambiente

```bash
cp .env.example .env
```

Preencha o `.env`:

```
POSTGRES_PASSWORD=troque_aqui
DATABASE_URL=postgresql://waha:troque_aqui@localhost:5432/waha_app
GROQ_API_KEY=sua_chave_aqui
```

### 2. Subir o WAHA e o Postgres

```bash
docker compose up -d
```

Na primeira inicialização, o Postgres executa os arquivos de `migrations/` e cria as tabelas.

Acesse o WAHA em `http://localhost:3000`, inicie uma sessão e leia o QR code com o WhatsApp.

### 3. Instalar as dependências Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Cadastrar os grupos monitorados

```bash
docker compose exec postgres psql -U waha -d waha_app
```

```sql
INSERT INTO grupos_monitorados (chat_id, nome) VALUES ('ID_DO_GRUPO@g.us', 'Nome do grupo');
```

Para descobrir o ID de um grupo, mande uma mensagem nele com o webhook rodando e veja o campo `from` no log.

### 5. Rodar

```bash
python app.py          # webhook, fica escutando na porta 8080
python processador.py  # processa as mensagens pendentes
```

---

## Consultas úteis

Últimas mensagens recebidas:

```sql
SELECT id, payload->>'body' AS texto, recebida_em
FROM mensagens_cruas
ORDER BY id DESC
LIMIT 10;
```

Promoções mais baratas da semana:

```sql
SELECT nome_item, preco_desconto, cupom, url
FROM promocoes
WHERE criada_em > now() - interval '7 days'
ORDER BY preco_desconto;
```

---

## Roadmap

- [x] WAHA conectado e disparando webhooks
- [x] Webhook Flask recebendo mensagens
- [x] Filtro por grupos cadastrados no banco
- [x] Gravação idempotente em `mensagens_cruas`
- [x] Segredos fora do código (`.env`)
- [x] Migrações versionadas
- [x] Extração estruturada com IA (JSON)
- [ ] Gravação em `promocoes` com atualização de repostagens
- [ ] Processador rodando automaticamente, respeitando o limite de requisições por minuto
- [ ] Extração de `deadline` e classificação em `categorias`
- [ ] Pool de conexões no webhook (resistir a reinícios do Postgres)
- [ ] Webhook e processador rodando em containers
- [ ] Interface de consulta ou alertas de preço

---

## Segurança

- **Nunca faça commit** do `.env` nem da pasta `sessions/`. Ela contém a sessão logada do WhatsApp e dá acesso à conta.
- `postgres-data/` e `.venv/` também ficam fora do repositório (ver `.gitignore`).
- Consultas SQL usam parâmetros (`%s`), nunca concatenação de strings, para evitar SQL injection.
