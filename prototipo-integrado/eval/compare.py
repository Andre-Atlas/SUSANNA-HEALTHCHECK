import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "eval" / "results"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eval_compare")


def generate_comparison_table(results_dir: Path = RESULTS_DIR) -> str:
    if not results_dir.exists():
        return "Nenhum resultado de benchmark encontrado."

    model_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if not model_dirs:
        return "Nenhum diretório de modelo encontrado em eval/results/."

    summaries = []
    for model_dir in sorted(model_dirs):
        summary_file = model_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file, "r", encoding="utf-8") as f:
                summaries.append(json.load(f))

    if not summaries:
        return "Nenhum arquivo summary.json encontrado para comparação."

    headers = [
        "Modelo",
        "Hit@K",
        "Faithfulness",
        "Correctness",
        "Relevance",
        "Abstention",
        "Policy Compliance",
        "Context",
        "Latência (ms)",
    ]

    rows = []
    for s in summaries:
        model_name = s.get("model_name", "Desconhecido")
        m = s.get("metrics_summary", {})
        row = [
            model_name,
            f"{m.get('hit_at_k', 0.0):.2f}",
            f"{m.get('faithfulness', 0.0):.2f}",
            f"{m.get('correctness', 0.0):.2f}",
            f"{m.get('relevance', 0.0):.2f}",
            f"{m.get('abstention_accuracy', 0.0):.2f}",
            f"{m.get('policy_compliance', 0.0):.2f}",
            f"{m.get('conversational_context', 0.0):.2f}",
            f"{m.get('avg_latency_ms', 0.0):.1f}",
        ]
        rows.append(row)

    # Formatar tabela Markdown
    col_widths = [max(len(headers[i]), max(len(row[i]) for row in rows)) for i in range(len(headers))]

    header_line = "| " + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
    separator_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    row_lines = [
        "| " + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]

    table_md = "\n".join([header_line, separator_line] + row_lines)
    return table_md


if __name__ == "__main__":
    table = generate_comparison_table()
    print("\n=== RESUMO COMPARATIVO DE BENCHMARK ===\n")
    print(table)
    print("\n")

    output_file = RESULTS_DIR / "comparison.md"
    if RESULTS_DIR.exists():
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Resumo Comparativo de Modelos — Benchmark Susana\n\n" + table + "\n")
        print(f"Resumo salvo em: {output_file}")
