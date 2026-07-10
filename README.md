# Encurtador de URL

Aplicacao para encurtar URLs, gerenciar links cadastrados e redirecionar acessos por codigos curtos. A API possui autenticacao JWT, persistencia em Cassandra, suporte a alias personalizado, expiracao por TTL e registro de acessos.

## Recursos

- Cadastro e login de usuarios.
- Autenticacao com JWT.
- Cadastro de URLs encurtadas.
- Alias personalizado ou codigo gerado automaticamente com NanoID.
- TTL para expiracao de links.
- Listagem, busca, edicao e remocao de URLs.
- Remocao de URLs em lote.
- Redirecionamento publico por codigo curto.
- Registro de acessos por URL.
- Documentacao Swagger/OpenAPI.

## Stack

- Python 3.12+
- FastAPI
- Apache Cassandra 5.0
- Redis
- Docker
- PyJWT
- bcrypt
- NanoID
- Pydantic v2

## Estrutura do projeto

```text
.
├── Dockerfile.cassandra
├── README.md
├── pyrightconfig.json
└── backend/
    ├── README.md
    ├── requirements.txt
    ├── .env.example
    ├── app/
    │   ├── routes/        # Rotas HTTP
    │   ├── controllers/   # Entrada e saida das requisicoes
    │   ├── services/      # Regras de negocio
    │   ├── repositories/  # Acesso ao Cassandra
    │   ├── schemas/       # Validacao e modelos Pydantic
    │   ├── models/        # Modelos de dominio
    │   ├── db/            # Conexao e schema Cassandra
    │   └── core/          # Configuracao e seguranca
    ├── cassandra/         # Schema CQL
    └── docs/              # OpenAPI gerado
```

## Pre-requisitos

- Python 3.12+
- Docker

## Cassandra

Na raiz do projeto, construa e suba o container:

```bash
docker build -f Dockerfile.cassandra -t encurtador-cassandra .
docker run -d --name encurtador-cassandra -p 9042:9042 encurtador-cassandra
```

Verifique se o Cassandra esta acessivel:

```bash
docker ps --filter name=encurtador-cassandra
docker exec encurtador-cassandra cqlsh -e "DESCRIBE KEYSPACES" localhost 9042
```

O schema e criado automaticamente quando a API inicia. Tambem existe uma copia em `backend/cassandra/schema.cql`.

## Backend

Instale as dependencias e rode a API:

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

Resposta esperada:

```json
{"status":"ok","app":"Encurtador de URL"}
```

## Frontend (Web)

O frontend foi desenvolvido em Angular. Para rodar a aplicação web localmente:

### Pré-requisitos
- Node.js 18+
- npm

### Rodando o Frontend

Acesse a pasta `web`, instale as dependências e inicie o servidor de desenvolvimento:

```bash
cd web
npm install
npm run start
```

O servidor de desenvolvimento iniciará em:

```text
http://localhost:4200
```

> [!NOTE]
> Certifique-se de que o backend está rodando localmente na porta `8000` para que o frontend consiga se comunicar com a API.

## Variaveis de ambiente

Copie `backend/.env.example` para `backend/.env` e ajuste conforme necessario.

| Variavel | Padrao | Descricao |
|---|---|---|
| `APP_NAME` | `Encurtador de URL` | Nome da API |
| `API_BASE_URL` | `http://localhost:8000` | Base usada para montar a URL encurtada |
| `JWT_SECRET` | `troque-este-segredo` | Segredo para assinar tokens JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo do token |
| `JWT_EXPIRES_MINUTES` | `10080` | Validade do token em minutos |
| `CASSANDRA_HOSTS` | `127.0.0.1` | Hosts do Cassandra separados por virgula |
| `CASSANDRA_PORT` | `9042` | Porta do Cassandra |
| `CASSANDRA_KEYSPACE` | `url_shortener` | Keyspace usado pela aplicacao |
| `CASSANDRA_DATACENTER` | `datacenter1` | Datacenter local do Cassandra |

## Autenticacao

Rotas protegidas exigem o header:

```http
Authorization: Bearer <token>
```

O token e retornado por:

- `POST /register`
- `POST /login`

## Endpoints

### Usuarios

| Metodo | Rota | Auth | Descricao |
|---|---|---|---|
| `POST` | `/usuarios` | Nao | Cria usuario |
| `POST` | `/register` | Nao | Cria usuario e retorna token |
| `POST` | `/login` | Nao | Autentica e retorna token |
| `GET` | `/usuarios` | Sim | Lista usuarios |
| `GET` | `/usuarios/{id}` | Sim | Busca usuario especifico |
| `PUT` | `/usuarios/{id}` | Sim | Atualiza nome/senha |
| `DELETE` | `/usuarios/{id}` | Sim | Remove usuario |

### URLs

| Metodo | Rota | Auth | Descricao |
|---|---|---|---|
| `POST` | `/url` | Sim | Cadastra URL encurtada |
| `POST` | `/url-encurtadas` | Sim | Cadastra URL encurtada |
| `GET` | `/url` | Sim | Lista URLs do usuario autenticado |
| `GET` | `/url/{codigo}` | Sim | Busca URL do usuario autenticado |
| `PUT` | `/url/{codigo}` | Sim | Atualiza redirecionamento, TTL ou status |
| `DELETE` | `/url/{codigo}` | Sim | Remove URL do usuario autenticado |
| `DELETE` | `/url/batch` | Sim | Remove varias URLs |
| `GET` | `/u/{codigo}` | Nao | Redireciona URL publica |
| `GET` | `/acessos/{codigo}` | Sim | Lista acessos do dia atual |

Exemplo de criacao de URL:

```json
{
  "url_original": "https://example.com/pagina-longa",
  "alias": "meu-link",
  "ttl": 30
}
```

Exemplo de delete em lote:

```json
{
  "codigos": ["abc123", "xyz789"]
}
```

## Documentacao

Com a API rodando:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

Arquivo OpenAPI exportado: `backend/docs/openapi.json`.

## Editor

O projeto inclui `pyrightconfig.json` na raiz apontando para `backend/.venv`.

Se aparecer erro como `Cannot find module fastapi`, selecione o interpretador:

```text
backend/.venv/bin/python
```

Depois recarregue a janela do VS Code/Cursor.

## Observacoes tecnicas

- O identificador usado nas rotas de URL e `codigo`, que pode ser alias ou NanoID.
- As rotas de CRUD de URL validam o dono pelo token JWT.
- Cassandra nao tem auto increment; IDs inteiros sao gerados pela aplicacao.
- O valor `qr_code` retornado pela API representa a URL encurtada que pode ser usada para gerar o QR Code.
