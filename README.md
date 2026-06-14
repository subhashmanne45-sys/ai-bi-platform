# 🤖 AI-Powered Autonomous Business Intelligence Platform

> An end-to-end Data Engineering + AI platform that replaces manual analytics with autonomous agents, natural language querying, and real-time business insights.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql)](https://postgresql.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.33-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black?logo=ollama)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📸 Screenshots

### Business Intelligence Dashboard
![Dashboard](https://via.placeholder.com/800x400/1565c0/ffffff?text=BI+Dashboard+%7C+Revenue+Charts+%7C+KPI+Cards)

### AI Natural Language Query
![AI Query](https://via.placeholder.com/800x400/0d47a1/ffffff?text=Ask+in+Plain+English+%E2%86%92+Get+Real+Answers)

---

## 🎯 Problem Statement

Organizations generate massive volumes of data daily but face critical challenges:

- 📊 Data scattered across multiple systems
- 🔍 Business users cannot query databases directly
- ⏰ Report generation is manual and slow
- 🚨 Anomaly detection requires human effort
- 💬 Managers need instant answers to business questions

**This platform solves all of the above.**

---

## ✅ Key Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Queries** | Ask *"Which region had the highest revenue?"* — get instant answers |
| 🤖 **Multi-Agent Analytics** | 4 AI agents collaborate to generate executive business reports |
| 📊 **Live Dashboard** | Interactive charts, KPIs, and trend analysis in your browser |
| ⚡ **Automated ETL** | Data generation → transformation → PostgreSQL loading in seconds |
| 🚨 **Smart Alerts** | Automatic detection of inventory issues and anomalies |
| 🔒 **100% Local AI** | Powered by Ollama — no API costs, no data leaves your machine |

---

## 🏗️ Architecture

```
User (Natural Language Question)
         │
         ▼
┌─────────────────────┐
│  Streamlit Dashboard │  ← Interactive UI (port 8501)
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   AI Query Layer    │  ← Ollama (qwen2.5-coder) NL→SQL
└─────────────────────┘
         │
         ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Multi-Agent Crew   │     │  PostgreSQL Database │
│  ┌───────────────┐  │     │  ┌───────────────┐  │
│  │  SQL Agent    │  │────▶│  │   customers   │  │
│  │Analytics Agent│  │     │  │   products    │  │
│  │  Alert Agent  │  │     │  │   sales       │  │
│  │Reporting Agent│  │     │  │  inventory    │  │
│  └───────────────┘  │     │  └───────────────┘  │
└─────────────────────┘     └─────────────────────┘
         ▲
         │
┌─────────────────────┐
│    ETL Pipeline     │  ← Extract → Transform → Load
└─────────────────────┘
         ▲
         │
┌─────────────────────┐
│   Data Generator    │  ← Faker (500 customers, 5000 sales)
└─────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.10+ | Core development |
| **Database** | PostgreSQL 18 | Data warehouse |
| **AI Model** | Ollama + qwen2.5-coder | Local NL→SQL + agents |
| **Dashboard** | Streamlit + Plotly | Interactive UI |
| **ETL** | SQLAlchemy + Pandas | Data pipeline |
| **Data Generation** | Faker | Synthetic business data |
| **Logging** | Loguru | Structured logging |
| **Config** | Pydantic Settings | Environment management |

---

## 📁 Project Structure

```
ai_bi_platform/
├── config/                 # Settings and logger
│   ├── settings.py         # Pydantic config from .env
│   └── logger.py           # Loguru rotating logger
│
├── data_generator/         # Synthetic data generation
│   └── generator.py        # Customers, products, sales, inventory
│
├── etl/                    # Extract-Transform-Load pipeline
│   └── pipeline.py         # Full ETL with upsert logic
│
├── database/               # Database layer
│   ├── models.py           # SQLAlchemy ORM models
│   └── connection.py       # Engine, sessions, helpers
│
├── ai_query/               # Natural language → SQL
│   └── nl_to_sql.py        # Ollama-powered NL→SQL pipeline
│
├── agents/                 # Multi-agent analytics crew
│   └── crew.py             # SQL + Analytics + Alert + Reporting agents
│
├── dashboard/              # Streamlit web application
│   └── app.py              # 5-page interactive dashboard
│
├── streaming/              # Kafka streaming (optional)
│   └── producer.py         # Real-time event producer
│
├── reports/                # AI-generated reports (auto-saved)
├── data/raw/               # Generated CSV files
├── logs/                   # Rotating log files
├── .env.example            # Environment template
├── requirements.txt        # All dependencies
└── run.py                  # Master CLI runner
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- [Ollama](https://ollama.ai) with `qwen2.5-coder` model

### 1. Clone the repository
```bash
git clone https://github.com/subhashmanne45-sys/ai-bi-platform.git
cd ai-bi-platform
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install ollama google-genai
```

### 4. Pull the AI model
```bash
ollama pull qwen2.5-coder
```

### 5. Set up PostgreSQL
```sql
CREATE USER bi_user WITH PASSWORD 'admin123';
CREATE DATABASE bi_platform OWNER bi_user;
GRANT ALL PRIVILEGES ON DATABASE bi_platform TO bi_user;
```

### 6. Configure environment
```bash
cp .env.example .env
# Edit .env and set DB_PASSWORD=admin123
```

### 7. Generate data + load to database
```bash
python run.py setup
```

### 8. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

Open **http://localhost:8501** 🎉

---

## 🤖 Usage Examples

### Natural Language Queries
```bash
python -m ai_query.nl_to_sql
```
```
Your question: Which region had the highest revenue?

💡 Jaipur had the highest revenue among all regions
   with a total revenue of ₹10,081,514.58.
   Focus additional marketing efforts in Jaipur to
   capitalize on this strong performance.

region    total_revenue
Jaipur     10081514.58
```

### Run Multi-Agent Analytics
```bash
python -m agents.crew
```
```
🤖 Agent 1/4: SQL Agent — Gathering metrics...
🧠 Agent 2/4: Analytics Agent — Finding insights...
🚨 Agent 3/4: Alert Agent — Scanning for anomalies...
📝 Agent 4/4: Reporting Agent — Writing executive report...

═══════════════════════════════════════
   AI-GENERATED BUSINESS REPORT
═══════════════════════════════════════
Performance Summary...
Key Findings...
Strategic Recommendations...

ACTIVE ALERTS (2)
⚠️ [HIGH] INVENTORY: 4 products below reorder level
⚠️ [MEDIUM] CANCELLATIONS: High cancellation rate 16.4%
```

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 **Dashboard** | KPI cards, revenue charts, monthly trends, top products |
| 🤖 **AI Query** | Natural language question answering with auto-charts |
| 🚨 **Alerts** | Inventory alerts, cancellation rates, anomalies |
| 📦 **Inventory** | Stock levels by category, reorder tracking |
| 👥 **Customers** | Segment analysis, age distribution, city breakdown |

---

## 📈 Sample Data Generated

| Dataset | Records |
|---------|---------|
| Customers | 500 |
| Products | 100 |
| Sales Transactions | 5,000 |
| Inventory Snapshots | 3,000 |
| **Total** | **8,600** |

---

## 🧠 AI Agents

| Agent | Responsibility |
|-------|---------------|
| **SQL Agent** | Queries PostgreSQL for key business metrics |
| **Analytics Agent** | Identifies trends, patterns, and top performers |
| **Alert Agent** | Detects inventory issues and anomalies |
| **Reporting Agent** | Writes executive business reports |

---

## 🎯 Skills Demonstrated

```
✅ Python Development          ✅ SQL & PostgreSQL
✅ ETL Pipeline Design         ✅ Data Modeling
✅ AI / LLM Integration        ✅ Multi-Agent Systems
✅ Natural Language Processing ✅ Dashboard Development
✅ Data Engineering            ✅ Real-Time Analytics
✅ Software Architecture       ✅ Git & Version Control
```

---

## 🗺️ Roadmap

- [ ] Apache Kafka real-time streaming
- [ ] Apache Airflow DAG orchestration
- [ ] FastAPI REST backend
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] Predictive analytics module

---

## 👨‍💻 Author

**Subhash Manne**
- GitHub: [@subhashmanne45-sys](https://github.com/subhashmanne45-sys)

---

## 📄 License

This project is licensed under the MIT License.

---

⭐ **If you found this project useful, please give it a star!**
