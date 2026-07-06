# Backend FastAPI - Encurtador de URL

Backend em Python/FastAPI para o encurtador de URL, com persistencia em Cassandra.

Escopo deste modulo:

- Integracao com Cassandra.
- CRUD de usuarios.
- Autenticacao com JWT.
- CRUD de URLs encurtadas.
- Redirect publico da URL encurtada.
- Registro e consulta de acessos.

Fora deste modulo:

- Frontend.
- Cache Redis.
- QR Code visual no frontend.

## Estrutura

```text
backend/app/routes/        rotas HTTP
backend/app/controllers/   entrada/saida das requisicoes
backend/app/services/      regras de negocio
backend/app/repositories/  acesso ao Cassandra
backend/app/schemas/       validacao e modelos de request/response
backend/app/db/            conexao e schema Cassandra
backend/app/core/          config e seguranca
backend/cassandra/         copia do schema CQL
backend/docs/              OpenAPI/Swagger gerado
```

## Subir Cassandra

Na raiz do projeto:

```bash
docker build -f Dockerfile.cassandra -t encurtador-cassandra .
docker run -d --name encurtador-cassandra -p 9042:9042 encurtador-cassandra
```

Para verificar:

```bash
docker ps --filter name=encurtador-cassandra
docker exec encurtador-cassandra cqlsh -e "DESCRIBE KEYSPACES" localhost 9042
```

O schema e criado automaticamente quando a API inicia. Tambem existe uma copia em `backend/cassandra/schema.cql`.

## Rodar API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API local:

```text
http://127.0.0.1:8000
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/
```

## Editor / VS Code / Cursor

O projeto tem `pyrightconfig.json` na raiz apontando para `backend/.venv`.

Se aparecer erro como `Cannot find module fastapi`, selecione o interpretador:

```text
backend/.venv/bin/python
```

Depois recarregue a janela do editor.

## Documentacao Swagger

Com a API rodando:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

Arquivo gerado para entrega: `backend/docs/openapi.json`.

## Autenticacao

As rotas protegidas usam JWT no header:

```http
Authorization: Bearer <token>
```

O token e retornado por:

- `POST /register`
- `POST /login`

## Rotas de usuarios

- `POST /usuarios` cria usuario.
- `POST /register` cria usuario e retorna token.
- `POST /login` autentica e retorna token.
- `GET /usuarios` lista usuarios.
- `GET /usuarios/{id}` busca usuario especifico.
- `PUT /usuarios/{id}` atualiza nome/senha.
- `DELETE /usuarios/{id}` remove usuario.

## Rotas de URLs

- `POST /url` cadastra URL encurtada.
- `POST /url-encurtadas` cadastra URL encurtada no formato combinado.
- `GET /url` lista URLs do usuario autenticado, com parametro `limit`.
- `GET /url/{codigo}` busca uma URL do usuario autenticado.
- `PUT /url/{codigo}` atualiza redirecionamento, TTL ou status.
- `DELETE /url/{codigo}` remove uma URL do usuario autenticado.
- `DELETE /url/batch` remove varias URLs do usuario autenticado.
- `GET /u/{codigo}` rota publica que valida TTL/status, registra acesso e redireciona.
- `GET /acessos/{codigo}` lista acessos do dia atual para uma URL do usuario.

Exemplo de cadastro:

```json
{
  "url_original": "https://example.com",
  "alias": "meu-alias",
  "ttl": 7
}
```

Exemplo de delete em lote:

```json
{
  "codigos": ["abc123", "xyz789"]
}
```

## Observacoes

- O identificador usado nas rotas de URL e `codigo`, que pode ser alias ou NanoID.
- O CRUD de URL valida o dono pelo token JWT.
- Redis/cache fica para outro modulo/dev.
- Cassandra nao usa auto increment; IDs inteiros sao gerados pela aplicacao.
