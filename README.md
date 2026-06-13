# 🚀 AI-Powered Autonomous Business Intelligence Platform

An intelligent Business Intelligence platform that combines Data Engineering, Artificial Intelligence, Natural Language Processing, and Multi-Agent Analytics to help organizations make data-driven decisions.

The platform allows users to interact with business data using natural language, automatically generates SQL queries, analyzes business performance, detects anomalies, and produces AI-generated executive insights.

---

## 📌 Features

### 📊 Business Intelligence Dashboard
- Revenue KPIs
- Order KPIs
- Customer KPIs
- Average Order Value
- Revenue by Region
- Revenue by Category

### 🤖 AI Natural Language Query
Ask questions in plain English:

Examples:

- Which region had the highest revenue?
- What is the top-performing category?
- Which city generated the most sales?

The system:

1. Understands the question
2. Generates SQL automatically
3. Executes SQL on PostgreSQL
4. Analyzes results
5. Generates business insights

---

### 🚨 Alert Monitoring

Business alerts include:

- Order Status Analysis
- High Cancellation Detection
- Return Rate Monitoring
- Pending Order Monitoring
- Business Anomaly Detection

---

### 👥 Customer Analytics

Customer intelligence includes:

- Top Cities by Active Customers
- Customer Distribution Analysis
- Customer Behavior Insights
- Regional Customer Trends

---

### 🧠 Multi-Agent Analytics Crew

The platform uses four AI agents working together:

#### Agent 1: SQL Agent
Responsibilities:
- Retrieve business metrics
- Execute SQL queries
- Gather data from PostgreSQL

#### Agent 2: Analytics Agent
Responsibilities:
- Analyze trends
- Discover patterns
- Generate business insights

#### Agent 3: Alert Agent
Responsibilities:
- Detect anomalies
- Monitor thresholds
- Generate alerts

#### Agent 4: Reporting Agent
Responsibilities:
- Create executive reports
- Summarize findings
- Generate recommendations

---

## 🏗️ System Architecture

```text
User
 ↓
Streamlit Dashboard
 ↓
AI Query Interface
 ↓
Multi-Agent Analytics Crew
 ├── SQL Agent
 ├── Analytics Agent
 ├── Alert Agent
 └── Reporting Agent
 ↓
Ollama (Qwen2.5-Coder)
 ↓
PostgreSQL Database
```

---

## ⚙️ Technology Stack

### Programming Language
- Python

### Database
- PostgreSQL

### AI / LLM
- Ollama
- Qwen2.5-Coder

### Frontend
- Streamlit

### Data Visualization
- Plotly
- Pandas

### Multi-Agent System
- Custom Agent Architecture

### Version Control
- Git
- GitHub

---

## 📁 Project Structure

```text
ai-bi-platform/
│
├── agents/
├── ai_query/
├── api/
├── config/
├── dashboard/
├── data_generator/
├── database/
├── etl/
├── reports/
├── streaming/
├── tests/
│
├── requirements.txt
├── README.md
└── app.py
```

---

## 🔄 Workflow

### Step 1
Business data is generated and stored in PostgreSQL.

### Step 2
User submits a question in natural language.

Example:

```
Which region had the highest revenue?
```

### Step 3
The AI Query Engine generates SQL.

Example:

```sql
SELECT region,
SUM(revenue) AS total_revenue
FROM sales
WHERE status = 'Completed'
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 1;
```

### Step 4
SQL Agent executes the query.

### Step 5
Analytics Agent interprets results.

### Step 6
Alert Agent checks anomalies.

### Step 7
Reporting Agent generates business insights.

### Step 8
Results are displayed in the dashboard.

---

## 📸 Screenshots

### Dashboard

(Add dashboard screenshot here)

### AI Query

(Add AI query screenshot here)

### Alerts

(Add alerts screenshot here)

### Customers

(Add customers screenshot here)

---

## 🎯 Project Objectives

- Automate business analytics
- Enable natural language data exploration
- Reduce dependency on manual SQL
- Generate AI-powered business insights
- Detect business anomalies automatically
- Demonstrate multi-agent collaboration
- Showcase modern Data Engineering workflows

---

## 🚀 Future Enhancements

- Inventory Analytics
- Predictive Forecasting
- Real-Time Kafka Streaming
- Cloud Deployment
- Role-Based Access Control
- Voice-Based Analytics
- Advanced Agent Collaboration

---

## 👨‍💻 Author

Subhash Manne

M.Tech (Data Engineering)

GitHub:
https://github.com/subhashmanne45-sys

---

## ⭐ Key Highlights

✔ AI-Powered Business Intelligence

✔ Natural Language to SQL

✔ PostgreSQL Analytics

✔ Ollama Integration

✔ Multi-Agent Analytics Crew

✔ Executive Reporting

✔ Business Alert Monitoring

✔ Customer Intelligence Dashboard
