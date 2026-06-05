# run.py
# ============================================================
# Master runner — use this to control every part of the platform.
#
# Usage examples:
#   python run.py setup          → generate data + run ETL
#   python run.py generate       → generate CSV data only
#   python run.py etl            → run ETL pipeline only
#   python run.py api            → start FastAPI server
#   python run.py dashboard      → start Streamlit dashboard
#   python run.py stream         → start Kafka producer
#   python run.py query "..."    → ask a natural language question
#   python run.py report         → generate an AI business report
# ============================================================

import sys
import argparse


def cmd_setup(args):
    """Generate data + run ETL pipeline."""
    from data_generator.generator import generate_all_data
    from etl.pipeline import run_full_pipeline

    print("\n[1/2] Generating business data...")
    generate_all_data()

    print("\n[2/2] Running ETL pipeline...")
    run_full_pipeline()

    print("\n✅ Setup complete! Database is ready.")
    print("   Next: python run.py dashboard  (or api)")


def cmd_generate(args):
    """Generate synthetic CSV data."""
    from data_generator.generator import generate_all_data
    generate_all_data()


def cmd_etl(args):
    """Run the ETL pipeline."""
    from etl.pipeline import run_full_pipeline
    run_full_pipeline()


def cmd_api(args):
    """Start FastAPI backend."""
    import uvicorn
    from config import settings
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


def cmd_dashboard(args):
    """Launch Streamlit dashboard."""
    import subprocess
    subprocess.run(["streamlit", "run", "dashboard/app.py"], check=True)


def cmd_stream(args):
    """Start Kafka producer."""
    from streaming.producer import get_producer, stream_sales_events
    from config import settings
    producer = get_producer()
    if producer:
        stream_sales_events(producer, topic=settings.kafka_topic_sales)
    else:
        print("❌ Kafka not available. Start Kafka broker first.")


def cmd_query(args):
    """Ask a natural language business question."""
    question = " ".join(args.question) if args.question else input("Enter question: ")
    try:
        from ai_query.nl_to_sql import ask_question
        result = ask_question(question)
        print("\n" + "=" * 60)
        print(f"Q: {question}")
        print("=" * 60)
        print(f"\n{result['explanation']}")
        if result.get("data"):
            import pandas as pd
            df = pd.DataFrame(result["data"])
            print("\nData:\n", df.to_string(index=False))
    except ImportError:
        print("AI query module not ready yet. Complete Phase 4 first.")


def cmd_report(args):
    """Generate an AI business report."""
    try:
        from agents.crew import run_analytics_crew
        report = run_analytics_crew()
        print(report)
    except ImportError:
        print("Agents module not ready yet. Complete Phase 5 first.")


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Business Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup        Generate data + run ETL (start here)
  generate     Generate CSV data only
  etl          Run ETL pipeline only
  api          Start FastAPI backend (port 8000)
  dashboard    Start Streamlit dashboard (port 8501)
  stream       Start Kafka streaming producer
  query        Ask a natural language question
  report       Generate AI business report
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("setup",     help="Generate data + run ETL")
    subparsers.add_parser("generate",  help="Generate CSV data only")
    subparsers.add_parser("etl",       help="Run ETL pipeline")
    subparsers.add_parser("api",       help="Start FastAPI server")
    subparsers.add_parser("dashboard", help="Start Streamlit dashboard")
    subparsers.add_parser("stream",    help="Start Kafka producer")
    subparsers.add_parser("report",    help="Generate AI report")

    q_parser = subparsers.add_parser("query", help="Ask a business question")
    q_parser.add_argument("question", nargs="*", help="The question to ask")

    args = parser.parse_args()

    commands = {
        "setup":     cmd_setup,
        "generate":  cmd_generate,
        "etl":       cmd_etl,
        "api":       cmd_api,
        "dashboard": cmd_dashboard,
        "stream":    cmd_stream,
        "query":     cmd_query,
        "report":    cmd_report,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
