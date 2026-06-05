# SETUP.md — AI-Powered BI Platform (Windows)

## Prerequisites

- Python 3.10+ (already installed)
- PostgreSQL 15+
- Docker Desktop (for Kafka + Airflow)
- Git (optional)

---

## Step 1 — Clone / Open the Project

Open **Command Prompt** or **PowerShell** in the `ai_bi_platform` folder.

---

## Step 2 — Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note on Airflow:** Airflow requires a separate install on Windows.
> Recommended: run Airflow inside Docker (see Step 6).

---

## Step 4 — Set Up PostgreSQL

1. Download & install PostgreSQL from https://www.postgresql.org/download/windows/
2. During install, set a password for the `postgres` superuser.
3. Open **pgAdmin** or **psql** and run:

```sql
CREATE USER bi_user WITH PASSWORD 'your_password_here';
CREATE DATABASE bi_platform OWNER bi_user;
GRANT ALL PRIVILEGES ON DATABASE bi_platform TO bi_user;
```

---

## Step 5 — Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and fill in:
- `DB_PASSWORD` — your PostgreSQL password
- `OPENAI_API_KEY` — from https://platform.openai.com/api-keys

---

## Step 6 — Docker (Kafka + Airflow)

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

Start Kafka:
```bash
docker run -d --name kafka \
  -p 9092:9092 \
  -e KAFKA_CFG_NODE_ID=0 \
  -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@kafka:9093 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  bitnami/kafka:latest
```

---

## Step 7 — Generate Data + Run ETL

```bash
python run.py setup
```

This will:
1. Generate 500 customers, 100 products, 5,000 sales transactions
2. Load everything into PostgreSQL

---

## Step 8 — Start the Platform

Open **three separate terminals** (all with `venv` activated):

**Terminal 1 — API:**
```bash
python run.py api
# → http://localhost:8000/docs
```

**Terminal 2 — Dashboard:**
```bash
python run.py dashboard
# → http://localhost:8501
```

**Terminal 3 — Streaming (optional):**
```bash
python run.py stream
```

---

## Step 9 — Ask a Business Question

```bash
python run.py query "Which region had the highest revenue last quarter?"
python run.py query "What are the top 5 products by profit margin?"
python run.py query "Show me monthly sales trend for Electronics"
```

---

## Project Structure

```
ai_bi_platform/
├── config/               # Settings, logger
├── data_generator/       # Synthetic data (Faker)
├── etl/                  # Extract-Transform-Load pipeline
├── database/             # SQLAlchemy models + connection
├── streaming/            # Kafka producer/consumer
├── orchestration/        # Airflow DAGs
│   └── dags/
├── ai_query/             # LangChain NL→SQL (Phase 4)
├── agents/               # CrewAI multi-agents (Phase 5)
├── api/                  # FastAPI backend (Phase 6)
├── dashboard/            # Streamlit UI (Phase 6)
├── tests/                # pytest test suite
├── data/
│   ├── raw/              # Generated CSVs
│   └── processed/
├── logs/                 # Rotating log files
├── docs/
├── notebooks/
├── reports/
├── .env.example          # Config template
├── requirements.txt
└── run.py                # Master CLI runner
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `psycopg2` install fails | Use `psycopg2-binary` (already in requirements) |
| DB connection refused | Check PostgreSQL service is running in Windows Services |
| Kafka not connecting | Ensure Docker Desktop is running; check port 9092 |
| OpenAI errors | Verify `OPENAI_API_KEY` in `.env` |
| `ModuleNotFoundError` | Make sure `(venv)` is active |
