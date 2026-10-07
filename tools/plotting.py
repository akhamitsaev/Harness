from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt

from schemas import DirectionAssessment, RunMetrics


def _label(assessment: DirectionAssessment) -> str:
    prefix = "MITO" if assessment.category == "mitochondrial" else "STD"
    text = f"[{prefix}] {assessment.display_name}"
    return "\n".join(textwrap.wrap(text, width=34))


def build_assessment_plot(
    assessments: list[DirectionAssessment],
    path: Path,
    *,
    title: str,
) -> None:
    if not assessments:
        return
    ordered = sorted(assessments, key=lambda x: x.score)
    labels = [_label(x) for x in ordered]
    scores = [x.score for x in ordered]

    fig, ax = plt.subplots(figsize=(11, max(5, 0.75 * len(labels))))
    ax.barh(labels, scores)
    ax.set_xlabel("Оценка перспективности LLM-оценщика (0-100)")
    ax.set_title(title)
    ax.set_xlim(0, 100)
    fig.subplots_adjust(left=0.34, right=0.97, top=0.90, bottom=0.12)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def build_benchmark_plot(metrics: list[RunMetrics], path: Path) -> None:
    if not metrics:
        return
    labels = [m.model for m in metrics]
    passed = [m.final_review_pass_count for m in metrics]
    rejected = [m.rejected_count for m in metrics]
    x = list(range(len(labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar([v - width / 2 for v in x], passed, width=width, label="Reviewer passed")
    ax.bar([v + width / 2 for v in x], rejected, width=width, label="Rejected")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Количество источников")
    ax.set_title("Сравнение LLM на одном наборе источников")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
