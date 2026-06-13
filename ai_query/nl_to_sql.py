# ai_query/nl_to_sql.py
# ============================================================
# Natural Language → SQL using Ollama (local, free, no API key)
# Uses qwen2.5-coder model for best SQL generation
# ============================================================

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ollama
from sqlalchemy import text

from config import logger
from database.connection import engine

# ── Model config ──────────────────────────────────────────────
OLLAMA_MODEL = "qwen2.5-coder"  # Best for SQL generation

# ── Database schema ───────────────────────────────────────────
DB_SCHEMA = """
You are a PostgreSQL expert. Use ONLY these tables:

TABLE: customers
  customer_id (VARCHAR), name (VARCHAR), email (VARCHAR),
  city (VARCHAR), state (VARCHAR), age (INT), gender (VARCHAR),
  segment (VARCHAR - values: Premium/Regular/New),
  registration_date (DATE), is_active (BOOLEAN)

TABLE: products
  product_id (VARCHAR), name (VARCHAR), category (VARCHAR),
  brand (VARCHAR), cost_price (FLOAT), selling_price (FLOAT),
  margin_pct (FLOAT), stock_qty (INT), reorder_level (INT),
  is_active (BOOLEAN)

TABLE: sales
  transaction_id (VARCHAR), customer_id (VARCHAR), product_id (VARCHAR),
  category (VARCHAR), region (VARCHAR), quantity (INT),
  unit_price (FLOAT), discount_pct (FLOAT), revenue (FLOAT),
  payment_method (VARCHAR), channel (VARCHAR),
  status (VARCHAR - values: Completed/Returned/Cancelled/Pending),
  sale_date (DATE), sale_month (VARCHAR), sale_year (INT),
  sale_quarter (VARCHAR)

TABLE: inventory_snapshots
  snapshot_id (VARCHAR), product_id (VARCHAR), product_name (VARCHAR),
  category (VARCHAR), stock_qty (INT), reorder_level (INT),
  needs_reorder (BOOLEAN), snapshot_date (DATE)

RULES:
- Return ONLY the raw SQL query, nothing else
- No markdown, no backticks, no explanation
- Always filter status = 'Completed' for revenue
- Use LIMIT 20 unless asked for more
- Use proper PostgreSQL syntax
"""

# ── SQL Generation ────────────────────────────────────────────

def generate_sql(question: str) -> str:
    """Use Ollama to convert natural language to SQL."""
    prompt = f"""{DB_SCHEMA}

Convert this to a PostgreSQL query:
Question: {question}

Return ONLY the SQL query, nothing else:"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response["message"]["content"].strip()
    # Clean any markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()
    # Take only the first statement if multiple
    if ";" in sql:
        sql = sql.split(";")[0].strip() + ";"
    logger.info(f"Generated SQL: {sql[:100]}...")
    return sql


# ── Query Execution ───────────────────────────────────────────

def execute_sql(sql: str) -> list:
    """Execute SQL and return results as list of dicts."""
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return rows


# ── Explanation Generation ────────────────────────────────────

def generate_explanation(question: str, results: list) -> str:
    """Use Ollama to explain results in plain English."""
    result_summary = str(results[:5]) if results else "No results found."

    prompt = f"""You are a business analyst. A user asked: "{question}"
Database returned: {result_summary}

Write 2-3 sentences of clear business insight. Mention the key finding and one recommended action. Be concise."""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


# ── Main query function ───────────────────────────────────────

def ask_question(question: str) -> dict:
    """Full pipeline: question → SQL → execute → explain."""
    logger.info(f"Question: {question}")
    start = time.time()

    try:
        sql         = generate_sql(question)
        data        = execute_sql(sql)
        explanation = generate_explanation(question, data)
        elapsed     = round((time.time() - start) * 1000, 2)

        logger.success(f"Answered in {elapsed}ms — {len(data)} rows")
        return {
            "question":     question,
            "sql":          sql,
            "data":         data,
            "explanation":  explanation,
            "row_count":    len(data),
            "execution_ms": elapsed,
            "success":      True,
        }

    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)
        logger.error(f"Query failed: {e}")
        return {
            "question":     question,
            "sql":          "",
            "data":         [],
            "explanation":  f"Error: {str(e)}",
            "row_count":    0,
            "execution_ms": elapsed,
            "success":      False,
        }


# ── Interactive CLI ───────────────────────────────────────────

def interactive_query():
    print("\n" + "="*60)
    print("  AI Business Intelligence — Powered by Ollama")
    print(f"  Model: {OLLAMA_MODEL} (running locally)")
    print("  Type 'exit' to quit")
    print("="*60)
    print("\nSample questions:")
    samples = [
        "Which region had the highest revenue?",
        "What are the top 5 products by total revenue?",
        "Show monthly revenue trend for 2024",
        "Which category has the highest profit margin?",
        "How many customers are in each segment?",
    ]
    for i, q in enumerate(samples, 1):
        print(f"  {i}. {q}")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not question:
            continue

        print("\nThinking... (local model, may take 10-30 seconds)")
        result = ask_question(question)

        print("\n" + "="*60)
        print(f"Q: {result['question']}")
        print("="*60)
        print(f"\n💡 {result['explanation']}")

        if result["data"]:
            import pandas as pd
            df = pd.DataFrame(result["data"])
            print(f"\nData ({result['row_count']} rows):")
            print(df.to_string(index=False))

        print(f"\n[{result['execution_ms']}ms]")


if __name__ == "__main__":
    interactive_query()
