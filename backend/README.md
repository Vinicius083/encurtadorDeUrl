# Backend FastAPI - Encurtador de URL



## Subir Cassandra

```bash
docker build -f Dockerfile.cassandra -t encurtador-cassandra .
docker run -d --name encurtador-cassandra -p 9042:9042 encurtador-cassandra
```

O schema e criado automaticamente quando a API inicia. Tambem existe uma copia em `backend/cassandra/schema.cql`.

## Rodar API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Rotas principais

- `POST /usuarios` cria usuario.
- `POST /register` cria usuario e retorna token.
- `POST /login` autentica e retorna token.
- `GET /usuarios`, `GET /usuarios/{id}`, `PUT /usuarios/{id}`, `DELETE /usuarios/{id}`.
- `POST /url-encurtadas` ou `POST /url` cria URL encurtada com `{ "url_original": "...", "alias": "opcional", "ttl": 7 }`.
- `GET /url` lista URLs do usuario autenticado.
- `GET /url/{codigo}` busca URL do usuario autenticado.
- `PUT /url/{codigo}` altera redirecionamento, TTL ou disponibilidade.
- `DELETE /url/{codigo}` remove uma URL.
- `DELETE /url/batch` remove varias URLs do usuario.
- `GET /u/{codigo}` rota publica que valida TTL/status, registra acesso e redireciona.
- `GET /acessos/{codigo}` lista acessos do dia atual para uma URL do usuario.

Use `Authorization: Bearer <token>` nas rotas protegidas.
