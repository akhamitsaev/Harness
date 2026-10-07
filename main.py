from __future__ import annotations

import argparse
from pathlib import Path

from config import ARTIFACTS_DIR, BENCHMARK_MODEL, PRIMARY_MODEL
from orchestrator import run_benchmark, run_harness

DEFAULT_QUERY = (
    "LHON: за последние 3-5 лет сравни митохондриально-таргетные терапии "
    "(idebenone, gene therapy, elamipretide) с традиционной поддерживающей терапией/стандартом ведения "
    "и оцени перспективность направлений."
)

DEMO_QUERIES = [
    DEFAULT_QUERY,
    (
        "Болезнь Паркинсона: за последние 3-5 лет сравни митохондриально-таргетные подходы "
        "(MitoQ, elamipretide, urolithin A, NAD+ precursors) со стандартной симптоматической терапией "
        "(например, levodopa) и оцени перспективность направлений."
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Harness для анализа митохондриальной медицины")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--model", default=PRIMARY_MODEL)
    parser.add_argument("--benchmark-model", default=BENCHMARK_MODEL)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Запустить 2 воспроизводимых исследовательских запроса")
    parser.add_argument("--max-pubmed", type=int, default=6, help="Максимум PubMed результатов на каждый search track")
    parser.add_argument("--max-trials", type=int, default=6, help="Максимум ClinicalTrials.gov результатов на каждый search track")
    args = parser.parse_args()

    if args.benchmark:
        if not args.benchmark_model:
            parser.error("Для --benchmark задайте BENCHMARK_MODEL/DEEPSEEK_MODEL")
        metrics = run_benchmark(
            query=args.query,
            primary_model=args.model,
            benchmark_model=args.benchmark_model,
            max_pubmed=args.max_pubmed,
            max_trials=args.max_trials,
        )
        print("\nBENCHMARK DONE")
        for m in metrics:
            print(f"{m.model}: reviewer passed {m.final_review_pass_count}/{m.source_count}")
        print("Artifacts: ./artifacts/benchmark/")
        return

    queries = DEMO_QUERIES if args.demo else [args.query]
    for idx, query in enumerate(queries, 1):
        out = ARTIFACTS_DIR / (f"demo_{idx}" if args.demo else "latest")
        evidence, comparisons, ranking, metrics = run_harness(
            query=query,
            model=args.model,
            max_pubmed=args.max_pubmed,
            max_trials=args.max_trials,
            output_dir=out,
        )
        print(f"\nDONE: {query}")
        print(f"Reviewer-passed evidence: {len(evidence)}")
        print(f"Comparisons: {len(comparisons.comparisons)}")
        print(f"Evaluated directions: {len(ranking)}")
        print(f"Artifacts: {out}")


if __name__ == "__main__":
    main()
