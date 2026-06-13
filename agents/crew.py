# agents/crew.py
# ============================================================
# Multi-Agent Analytics System using Ollama (local, free)
# 4 agents: SQL Agent, Analytics Agent, Alert Agent, Reporting Agent
# ============================================================

import sys
import json
import decimal
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent.parent))

import ollama
from sqlalchemy import text

from config import logger
from database.connection import engine

OLLAMA_MODEL = "qwen2.5-coder"


# ── Shared DB query helper ────────────────────────────────────

def run_query(sql: str) -> list:
    """Execute SQL and return results as list of dicts (JSON-safe)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = []
            for row in result.fetchall():
                clean_row = {}
                for k, v in zip(columns, row):
                    if isinstance(v, (datetime, date)):
                        clean_row[k] = str(v)
                    elif isinstance(v, decimal.Decimal):
                        clean_row[k] = float(v)
                    else:
                        clean_row[k] = v
                rows.append(clean_row)
            return rows
    except Exception as e:
        logger.error(f"Query error: {e}")
        return []


def ask_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response."""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()


# ══════════════════════════════════════════════════════════════
# AGENT 1: SQL Agent
# ══════════════════════════════════════════════════════════════

class SQLAgent:
    name = "SQL Agent"

    def run(self) -> dict:
        logger.info(f"[{self.name}] Gathering business metrics...")
        metrics = {}

        metrics["total_revenue"] = run_query(
            "SELECT ROUND(SUM(revenue)::numeric, 2) as total FROM sales WHERE status='Completed'"
        )

        metrics["revenue_by_region"] = run_query("""
            SELECT region,
                   ROUND(SUM(revenue)::numeric, 2) as revenue,
                   COUNT(*) as transactions
            FROM sales WHERE status='Completed'
            GROUP BY region ORDER BY revenue DESC
        """)

        metrics["revenue_by_category"] = run_query("""
            SELECT category,
                   ROUND(SUM(revenue)::numeric, 2) as revenue,
                   ROUND(CAST(AVG(discount_pct)*100 AS numeric), 1) as avg_discount_pct
            FROM sales WHERE status='Completed'
            GROUP BY category ORDER BY revenue DESC
        """)

        metrics["monthly_trend"] = run_query("""
            SELECT sale_month,
                   ROUND(SUM(revenue)::numeric, 2) as revenue,
                   COUNT(*) as transactions
            FROM sales WHERE status='Completed'
            GROUP BY sale_month ORDER BY sale_month DESC LIMIT 12
        """)

        metrics["top_products"] = run_query("""
            SELECT p.name, p.category,
                   ROUND(SUM(s.revenue)::numeric, 2) as revenue,
                   SUM(s.quantity) as units_sold
            FROM sales s JOIN products p ON s.product_id = p.product_id
            WHERE s.status='Completed'
            GROUP BY p.name, p.category ORDER BY revenue DESC LIMIT 5
        """)

        metrics["customer_segments"] = run_query("""
            SELECT segment, COUNT(*) as count,
                   ROUND(AVG(age)::numeric, 1) as avg_age
            FROM customers GROUP BY segment ORDER BY count DESC
        """)

        metrics["order_status"] = run_query("""
            SELECT status, COUNT(*) as count,
                   ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(), 1) as pct
            FROM sales GROUP BY status ORDER BY count DESC
        """)

        logger.success(f"[{self.name}] Metrics collected!")
        return metrics


# ══════════════════════════════════════════════════════════════
# AGENT 2: Analytics Agent
# ══════════════════════════════════════════════════════════════

class AnalyticsAgent:
    name = "Analytics Agent"

    def run(self, metrics: dict) -> dict:
        logger.info(f"[{self.name}] Analyzing trends and patterns...")

        prompt = f"""You are a senior business analyst. Analyze this business data:

REVENUE BY REGION: {json.dumps(metrics.get('revenue_by_region', [])[:5])}
REVENUE BY CATEGORY: {json.dumps(metrics.get('revenue_by_category', []))}
MONTHLY TREND: {json.dumps(metrics.get('monthly_trend', [])[:6])}
TOP PRODUCTS: {json.dumps(metrics.get('top_products', []))}
CUSTOMER SEGMENTS: {json.dumps(metrics.get('customer_segments', []))}

Provide exactly 4 lines in this format:
TREND: [one key trend]
TOP_PERFORMER: [best region/category/product]
CONCERN: [one area needing attention]
OPPORTUNITY: [one growth opportunity]"""

        analysis_text = ask_ollama(prompt)
        analysis = {"raw": analysis_text, "trend": "", "top_performer": "", "concern": "", "opportunity": ""}

        for line in analysis_text.split("\n"):
            if line.startswith("TREND:"):
                analysis["trend"] = line.replace("TREND:", "").strip()
            elif line.startswith("TOP_PERFORMER:"):
                analysis["top_performer"] = line.replace("TOP_PERFORMER:", "").strip()
            elif line.startswith("CONCERN:"):
                analysis["concern"] = line.replace("CONCERN:", "").strip()
            elif line.startswith("OPPORTUNITY:"):
                analysis["opportunity"] = line.replace("OPPORTUNITY:", "").strip()

        logger.success(f"[{self.name}] Analysis complete!")
        return analysis


# ══════════════════════════════════════════════════════════════
# AGENT 3: Alert Agent
# ══════════════════════════════════════════════════════════════

class AlertAgent:
    name = "Alert Agent"

    def run(self, metrics: dict) -> list:
        logger.info(f"[{self.name}] Scanning for anomalies...")
        alerts = []

        # Low stock alert
        low_stock = run_query("""
            SELECT product_name, stock_qty, reorder_level
            FROM inventory_snapshots
            WHERE needs_reorder = true
              AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
            ORDER BY stock_qty ASC LIMIT 5
        """)
        if low_stock:
            alerts.append({
                "type": "INVENTORY", "severity": "HIGH",
                "message": f"{len(low_stock)} products below reorder level",
                "details": [r["product_name"] for r in low_stock]
            })

        # High cancellation alert
        for s in metrics.get("order_status", []):
            if s["status"] == "Cancelled" and float(s["pct"]) > 10:
                alerts.append({
                    "type": "CANCELLATIONS", "severity": "MEDIUM",
                    "message": f"High cancellation rate: {s['pct']}%",
                    "details": []
                })

        # Revenue concentration alert
        region_data = metrics.get("revenue_by_region", [])
        if region_data and len(region_data) > 1:
            total = sum(float(r["revenue"]) for r in region_data)
            top_pct = float(region_data[0]["revenue"]) / total * 100
            if top_pct > 30:
                alerts.append({
                    "type": "CONCENTRATION", "severity": "LOW",
                    "message": f"{region_data[0]['region']} accounts for {top_pct:.1f}% of revenue",
                    "details": []
                })

        logger.success(f"[{self.name}] Found {len(alerts)} alerts!")
        return alerts


# ══════════════════════════════════════════════════════════════
# AGENT 4: Reporting Agent
# ══════════════════════════════════════════════════════════════

class ReportingAgent:
    name = "Reporting Agent"

    def run(self, metrics: dict, analysis: dict, alerts: list) -> str:
        logger.info(f"[{self.name}] Generating executive report...")

        total_rev_data = metrics.get("total_revenue", [{}])
        total_rev = total_rev_data[0].get("total", 0) if total_rev_data else 0
        top_region = metrics["revenue_by_region"][0] if metrics.get("revenue_by_region") else {}
        top_category = metrics["revenue_by_category"][0] if metrics.get("revenue_by_category") else {}

        prompt = f"""You are a Chief Analytics Officer. Write a professional 3-paragraph executive business report.

KEY METRICS:
- Total Revenue: {total_rev:,.2f}
- Top Region: {top_region.get('region', 'N/A')} ({top_region.get('revenue', 0):,.2f})
- Top Category: {top_category.get('category', 'N/A')} ({top_category.get('revenue', 0):,.2f})

ANALYSIS:
- Key Trend: {analysis.get('trend', 'N/A')}
- Top Performer: {analysis.get('top_performer', 'N/A')}
- Main Concern: {analysis.get('concern', 'N/A')}
- Growth Opportunity: {analysis.get('opportunity', 'N/A')}

ALERTS: {len(alerts)} active
{chr(10).join([f"- [{a['severity']}] {a['message']}" for a in alerts])}

Write 3 paragraphs: 1) Performance summary 2) Key findings 3) Recommendations"""

        report = ask_ollama(prompt)
        logger.success(f"[{self.name}] Report generated!")
        return report


# ══════════════════════════════════════════════════════════════
# CREW COORDINATOR
# ══════════════════════════════════════════════════════════════

def run_analytics_crew() -> str:
    print("\n" + "="*60)
    print("  AI MULTI-AGENT ANALYTICS CREW")
    print("  4 agents collaborating on your business data")
    print("="*60)

    start = datetime.now()

    print("\n🤖 Agent 1/4: SQL Agent — Gathering metrics...")
    metrics = SQLAgent().run()

    print("🧠 Agent 2/4: Analytics Agent — Finding insights...")
    analysis = AnalyticsAgent().run(metrics)

    print("🚨 Agent 3/4: Alert Agent — Scanning for anomalies...")
    alerts = AlertAgent().run(metrics)

    print("📝 Agent 4/4: Reporting Agent — Writing executive report...")
    report = ReportingAgent().run(metrics, analysis, alerts)

    elapsed = (datetime.now() - start).total_seconds()

    output = f"""
{'='*60}
       AI-GENERATED BUSINESS INTELLIGENCE REPORT
       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*60}

{report}

{'='*60}
ACTIVE ALERTS ({len(alerts)})
{'='*60}"""

    for alert in alerts:
        output += f"\n⚠️  [{alert['severity']}] {alert['type']}: {alert['message']}"
        if alert["details"]:
            output += f"\n   Items: {', '.join(str(d) for d in alert['details'][:3])}"

    output += f"\n\n{'='*60}"
    output += f"\nReport generated in {elapsed:.1f}s by 4 AI agents"
    output += f"\n{'='*60}"

    return output


if __name__ == "__main__":
    report = run_analytics_crew()
    print(report)

    import os
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Report saved to {filename}")
