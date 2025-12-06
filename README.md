# Judicial API

API em Python (FastAPI) para consulta e gestão de processos jurídicos, preparada para integração com múltiplos tribunais.

## Requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local sem Docker)

## Como Rodar

1. **Configurar Variáveis de Ambiente**:
   O `docker-compose.yml` já possui valores padrão. Para produção, crie um arquivo `.env` baseando-se nas variáveis do compose.
   
   Variáveis Importantes:
   - `DATABASE_URL`: Connection string PostgreSQL.
   - `JWT_SECRET`: Segredo para assinatura de tokens.
   - `PFX_PATH`: Caminho absoluto para o certificado A1 (.pfx).
   - `PFX_PASSWORD`: Senha do certificado.

2. **Iniciar com Docker**:
   ```bash
   docker-compose up --build
   ```
   A API estará disponível em `http://localhost:8000`.

3. **Rodar Testes**:
   ```bash
   docker-compose run api pytest
   ```

## Endpoints Principais

- `POST /auth/login`: Autenticação (user: fred, pass: secret).
- `POST /processos/cadastrar`: Registra novo processo.
- `GET /processos/{id}`: Detalhes do processo.
- `POST /oab/importar`: Dispara crawler em background.

## Desenvolvimento

Para rodar localmente:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Migrations (Alembic)

Para criar nova revisão:
```bash
alembic revision --autogenerate -m "descricao"
```
Para aplicar:
```bash
alembic upgrade head
```
