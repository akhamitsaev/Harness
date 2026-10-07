from __future__ import annotations

import json
import re
import time
from pathlib import Path

from agents.comparator import compare_with_standard
from agents.evaluator import evaluate_promisingness
from agents.extractor import extract_evidence
from agents.planner import build_research_plan
from agents.reviewer import review_evidence
from agents.searcher import build_search_plan
from config import ARTIFACTS_DIR
from runlog import RunLogger
from schemas import (
    AssessmentBundle,
    ComparisonBundle,
    DirectionAssessment,
    EvidenceRecord,
    ResearchPlan,
    RunMetrics,
    SearchPlan,
    SourceDocument,
)
from skill_loader import get_agent_skill_names
from tools.clinical_trials import search_clinical_trials
from tools.plotting import build_assessment_plot, build_benchmark_plot
from tools.pubmed import search_pubmed


def _dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    if isinstance(data, list):
        data = [x.model_dump() if hasattr(x, "model_dump") else x for x in data]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _model_label(model: str) -> str:
    provider = model.split("/", 1)[0] if "/" in model else model
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", provider).strip("_").lower() or "model"


def _merge_sources(groups: list[list[SourceDocument]]) -> list[SourceDocument]:
    merged: dict[tuple[str, str], SourceDocument] = {}
    for group in groups:
        for source in group:
            key = (source.source_type, source.source_id)
            if key not in merged:
                merged[key] = source
                continue
            current = merged[key]
            if current.evidence_track != source.evidence_track:
                merged[key] = current.model_copy(update={"evidence_track": "mixed"})
    return list(merged.values())


def prepare_research(
    *,
    query: str,
    model: str,
    max_pubmed: int,
    max_trials: int,
    logger: RunLogger,
) -> tuple[ResearchPlan, SearchPlan, list[SourceDocument]]:
    logger.log("delegate", agent="root_orchestrator", model=model)
    research_plan = build_research_plan(query, model=model)
    logger.log("plan", query=query, plan=research_plan.model_dump())

    logger.log(
        "delegate",
        agent="literature_searcher",
        model=model,
        skills=get_agent_skill_names("searcher"),
    )
    search_plan = build_search_plan(query, research_plan, model=model)
    logger.log("search_plan", plan=search_plan.model_dump())

    years = research_plan.time_window_years

    logger.log(
        "tool_call",
        agent="literature_searcher",
        tool="pubmed_search",
        track="mitochondrial",
        query=search_plan.pubmed_mito_query,
        years=years,
    )
    pubmed_mito = search_pubmed(
        search_plan.pubmed_mito_query,
        max_results=max_pubmed,
        years=years,
        evidence_track="mitochondrial",
    )
    logger.log("tool_result", tool="pubmed_search", track="mitochondrial", count=len(pubmed_mito))

    logger.log(
        "tool_call",
        agent="literature_searcher",
        tool="pubmed_search",
        track="standard",
        query=search_plan.pubmed_standard_query,
        years=years,
    )
    pubmed_standard = search_pubmed(
        search_plan.pubmed_standard_query,
        max_results=max_pubmed,
        years=years,
        evidence_track="standard",
    )
    logger.log("tool_result", tool="pubmed_search", track="standard", count=len(pubmed_standard))

    logger.log(
        "tool_call",
        agent="literature_searcher",
        tool="clinical_trials_search",
        track="mitochondrial",
        condition=search_plan.clinical_trials_condition,
        interventions=search_plan.clinical_trials_mito_interventions,
        years=years,
    )
    trials_mito = search_clinical_trials(
        search_plan.clinical_trials_condition,
        intervention_query=search_plan.clinical_trials_mito_interventions,
        max_results=max_trials,
        years=years,
        evidence_track="mitochondrial",
    )
    logger.log("tool_result", tool="clinical_trials_search", track="mitochondrial", count=len(trials_mito))

    logger.log(
        "tool_call",
        agent="literature_searcher",
        tool="clinical_trials_search",
        track="standard",
        condition=search_plan.clinical_trials_condition,
        interventions=search_plan.clinical_trials_standard_interventions,
        years=years,
    )
    trials_standard = search_clinical_trials(
        search_plan.clinical_trials_condition,
        intervention_query=search_plan.clinical_trials_standard_interventions,
        max_results=max_trials,
        years=years,
        evidence_track="standard",
    )
    logger.log("tool_result", tool="clinical_trials_search", track="standard", count=len(trials_standard))

    sources = _merge_sources([pubmed_mito, pubmed_standard, trials_mito, trials_standard])
    logger.log("orchestrator_decision", decision="deduplicate_sources", unique_source_count=len(sources))
    return research_plan, search_plan, sources


def _report(
    *,
    query: str,
    model: str,
    research_plan: ResearchPlan,
    search_plan: SearchPlan,
    evidence: list[EvidenceRecord],
    comparisons: ComparisonBundle,
    assessments: list[DirectionAssessment],
    metrics: RunMetrics,
) -> str:
    ranked = sorted(assessments, key=lambda x: x.score, reverse=True)
    mito_ranked = [x for x in ranked if x.category == "mitochondrial"]

    lines = [
        f"# Экспресс-обзор: {search_plan.disease}",
        "",
        f"**Исследовательский запрос:** {query}",
        f"**Модель:** `{model}`",
        f"**Временное окно:** последние {research_plan.time_window_years} лет",
        f"**Стандарт лечения для сравнения:** {search_plan.standard_of_care}",
        "",
        "## План Root-оркестратора",
        "",
    ]
    lines.extend(f"- {step}" for step in research_plan.steps)

    lines += [
        "",
        "## Качество прогона",
        "",
        f"- Найдено уникальных источников: **{metrics.source_count}**",
        f"- Успешных structured extractions: **{metrics.extraction_success_count}**",
        f"- Прошли reviewer: **{metrics.final_review_pass_count}**",
        f"- Отклонено: **{metrics.rejected_count}**",
        f"- Retry после feedback reviewer: **{metrics.retry_count}**",
        f"- Reviewer pass rate: **{metrics.reviewer_pass_rate:.1%}**",
        f"- Сравнений mito vs standard: **{metrics.comparison_count}**",
        f"- Оценённых направлений: **{metrics.assessment_count}**",
        "",
        "## Рейтинг перспективности",
        "",
        "> Балл 0-100 выставляет LLM-субагент Evaluator по runtime skill `promisingness_criteria`. Это исследовательская оценка, а не клиническая рекомендация.",
        "",
        "| Rank | Категория | Направление | Score | Evidence level | Confidence |",
        "|---:|---|---|---:|---|---|",
    ]
    for i, item in enumerate(ranked, 1):
        lines.append(
            f"| {i} | {item.category} | {item.intervention} | {item.score} | {item.evidence_level} | {item.confidence} |"
        )

    if mito_ranked:
        lines += [
            "",
            "## Самое и наименее перспективное митохондриальное направление",
            "",
            f"- **Топ:** {mito_ranked[0].intervention} - {mito_ranked[0].score}/100. {mito_ranked[0].rationale}",
            f"- **Аутсайдер:** {mito_ranked[-1].intervention} - {mito_ranked[-1].score}/100. {mito_ranked[-1].rationale}",
        ]

    lines += ["", "## Сравнение с традиционным лечением", ""]
    if comparisons.comparisons:
        for c in comparisons.comparisons:
            lines += [
                f"### {c.mitochondrial_intervention} vs {c.standard_comparator}",
                f"- Относительная доказательная база: **{c.relative_evidence}**",
                f"- Вывод: {c.summary}",
                f"- Источники: {', '.join(c.supporting_source_ids) or 'нет'}",
                f"- Ограничения: {'; '.join(c.limitations) or 'не указаны'}",
                "",
            ]
    else:
        lines.append("Сопоставимых reviewer-passed данных недостаточно; Harness не выдумывает сравнение.")

    lines += ["", "## Проверенные данные", ""]
    for r in evidence:
        ids = [f"[{r.source_id}]({r.source_url})"]
        if r.doi:
            ids.append(f"DOI: `{r.doi}`")
        lines += [
            f"### {r.intervention or 'Без терапевтического вмешательства'}",
            f"- Track: {r.evidence_track}",
            f"- Source: {'; '.join(ids)}",
            f"- Disease: {r.disease or 'не указано'}",
            f"- Target: {r.target or 'не указано'}",
            f"- Study type: {r.study_type}",
            f"- Evidence level: {r.evidence_level}",
            f"- Phase: {r.phase or 'не указано'}",
            f"- n: {r.n if r.n is not None else 'не указано'}",
            f"- Outcome: {r.outcome or 'не указано'}",
            f"- Effect: {r.effect or 'не указано'}",
            f"- Effect class: {r.effect_class}",
            f"- Supporting quote: “{r.source_quote or 'нет'}”",
            "",
        ]

    lines += [
        "## Ограничения",
        "",
        "- Это экспресс-обзор, а не систематический обзор или метаанализ.",
        "- PubMed abstracts и записи ClinicalTrials.gov могут не содержать всех деталей для полноценной risk-of-bias оценки.",
        "- Cross-study сравнение не эквивалентно head-to-head исследованию.",
        "- Reviewer сочетает LLM-семантическую проверку с детерминированными guardrails по provenance, quote и n.",
        "- Оценка перспективности зависит от полноты найденных данных и rubric skill; это не медицинская рекомендация.",
        "- Временное окно применяется к PubMed и к first-posted ClinicalTrials.gov приблизительно за последние 3-5 лет.",
        "",
    ]
    return "\n".join(lines)


def analyze_sources(
    *,
    query: str,
    model: str,
    research_plan: ResearchPlan,
    search_plan: SearchPlan,
    sources: list[SourceDocument],
    output_dir: Path,
    logger: RunLogger,
) -> tuple[list[EvidenceRecord], ComparisonBundle, list[DirectionAssessment], RunMetrics]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    accepted: list[EvidenceRecord] = []
    rejected: list[dict] = []
    extraction_success_count = 0
    first_pass_review_count = 0
    retry_count = 0

    for source in sources:
        record: EvidenceRecord | None = None
        final_issues: list[str] = []
        feedback: str | None = None
        extracted_once = False

        for attempt in (1, 2):
            if attempt == 2:
                retry_count += 1

            logger.log(
                "delegate",
                agent="extractor",
                model=model,
                source_id=source.source_id,
                attempt=attempt,
                skills=get_agent_skill_names("extractor"),
            )
            try:
                record = extract_evidence(
                    source,
                    model=model,
                    reviewer_feedback=feedback,
                )
                if not extracted_once:
                    extraction_success_count += 1
                    extracted_once = True
            except Exception as exc:
                feedback = str(exc)
                final_issues = [str(exc)]
                logger.log(
                    "agent_error",
                    agent="extractor",
                    source_id=source.source_id,
                    attempt=attempt,
                    error=str(exc),
                )
                continue

            logger.log(
                "tool_result",
                tool="pydantic_structured_parser",
                agent="extractor",
                source_id=source.source_id,
                status="valid",
            )
            logger.log(
                "delegate",
                agent="reviewer",
                model=model,
                source_id=source.source_id,
                attempt=attempt,
                skills=get_agent_skill_names("reviewer"),
            )
            review = review_evidence(record, source, model=model)
            final_issues = review.issues
            logger.log(
                "review",
                model=model,
                source_id=source.source_id,
                attempt=attempt,
                passed=review.passed,
                deterministic_passed=review.deterministic_passed,
                llm_passed=review.llm_passed,
                issues=review.issues,
            )
            if review.passed:
                if attempt == 1:
                    first_pass_review_count += 1
                accepted.append(record)
                break

            feedback = review.feedback_to_extractor or "; ".join(review.issues)
            logger.log(
                "feedback",
                from_agent="reviewer",
                to_agent="extractor",
                source_id=source.source_id,
                feedback=feedback,
            )

        else:
            rejected.append(
                {
                    "source_id": source.source_id,
                    "title": source.title,
                    "issues": final_issues,
                }
            )

    logger.log(
        "delegate",
        agent="comparator",
        model=model,
        skills=get_agent_skill_names("comparator"),
        evidence_count=len(accepted),
    )
    comparisons = compare_with_standard(accepted, search_plan, model=model)
    logger.log("comparison_complete", count=len(comparisons.comparisons))

    logger.log(
        "delegate",
        agent="evaluator",
        model=model,
        skills=get_agent_skill_names("evaluator"),
        evidence_count=len(accepted),
    )
    assessment_bundle: AssessmentBundle = evaluate_promisingness(
        accepted,
        comparisons,
        search_plan,
        model=model,
    )
    assessments = sorted(assessment_bundle.assessments, key=lambda x: x.score, reverse=True)
    logger.log("evaluation_complete", count=len(assessments))

    runtime = time.perf_counter() - started
    metrics = RunMetrics(
        model=model,
        source_count=len(sources),
        extraction_success_count=extraction_success_count,
        first_pass_review_count=first_pass_review_count,
        final_review_pass_count=len(accepted),
        rejected_count=len(rejected),
        retry_count=retry_count,
        comparison_count=len(comparisons.comparisons),
        assessment_count=len(assessments),
        reviewer_pass_rate=(len(accepted) / len(sources)) if sources else 0.0,
        total_runtime_sec=runtime,
    )

    _dump(output_dir / "evidence.json", accepted)
    _dump(output_dir / "rejected.json", rejected)
    _dump(output_dir / "comparisons.json", comparisons)
    _dump(output_dir / "ranking.json", assessments)
    _dump(output_dir / "metrics.json", metrics)

    plot_path = output_dir / "comparison.png"
    logger.log("tool_call", tool="plotting_sandbox", path=str(plot_path))
    build_assessment_plot(
        assessments,
        plot_path,
        title=f"{search_plan.disease}: mitochondrial vs standard-of-care directions",
    )
    logger.log("tool_result", tool="plotting_sandbox", path=str(plot_path))

    report = _report(
        query=query,
        model=model,
        research_plan=research_plan,
        search_plan=search_plan,
        evidence=accepted,
        comparisons=comparisons,
        assessments=assessments,
        metrics=metrics,
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    logger.log("model_run_complete", model=model, output_dir=str(output_dir), metrics=metrics.model_dump())

    return accepted, comparisons, assessments, metrics


def run_harness(
    *,
    query: str,
    model: str,
    max_pubmed: int = 6,
    max_trials: int = 6,
    output_dir: Path | None = None,
) -> tuple[list[EvidenceRecord], ComparisonBundle, list[DirectionAssessment], RunMetrics]:
    output_dir = output_dir or (ARTIFACTS_DIR / "latest")
    logger = RunLogger(output_dir / "run.jsonl")
    research_plan, search_plan, sources = prepare_research(
        query=query,
        model=model,
        max_pubmed=max_pubmed,
        max_trials=max_trials,
        logger=logger,
    )
    _dump(output_dir / "research_plan.json", research_plan)
    _dump(output_dir / "search_plan.json", search_plan)
    _dump(output_dir / "sources.json", sources)
    return analyze_sources(
        query=query,
        model=model,
        research_plan=research_plan,
        search_plan=search_plan,
        sources=sources,
        output_dir=output_dir,
        logger=logger,
    )


def run_benchmark(
    *,
    query: str,
    primary_model: str,
    benchmark_model: str,
    max_pubmed: int = 6,
    max_trials: int = 6,
) -> list[RunMetrics]:
    benchmark_root = ARTIFACTS_DIR / "benchmark"
    benchmark_root.mkdir(parents=True, exist_ok=True)
    logger = RunLogger(benchmark_root / "run.jsonl")

    research_plan, search_plan, sources = prepare_research(
        query=query,
        model=primary_model,
        max_pubmed=max_pubmed,
        max_trials=max_trials,
        logger=logger,
    )
    _dump(benchmark_root / "sources.json", sources)
    _dump(benchmark_root / "research_plan.json", research_plan)
    _dump(benchmark_root / "search_plan.json", search_plan)

    metrics: list[RunMetrics] = []
    for model in (primary_model, benchmark_model):
        label = _model_label(model)
        _, _, _, model_metrics = analyze_sources(
            query=query,
            model=model,
            research_plan=research_plan,
            search_plan=search_plan,
            sources=sources,
            output_dir=benchmark_root / label,
            logger=logger,
        )
        metrics.append(model_metrics)

    _dump(benchmark_root / "benchmark.json", metrics)
    build_benchmark_plot(metrics, benchmark_root / "benchmark.png")
    md = [
        "# Benchmark двух LLM",
        "",
        "Обе модели анализировали один и тот же набор источников. Поиск выполнен один раз.",
        "",
        "| Model | Sources | Reviewer passed | Rejected | Runtime, s |",
        "|---|---:|---:|---:|---:|",
    ]
    for m in metrics:
        md.append(
            f"| {m.model} | {m.source_count} | {m.final_review_pass_count} | {m.rejected_count} | {m.total_runtime_sec:.2f} |"
        )
    md += [
        "",
        "> Это сравнение стабильности/проходимости pipeline, а не accuracy: без ручного gold set нельзя утверждать, какая LLM научно точнее.",
    ]
    (benchmark_root / "benchmark.md").write_text("\n".join(md), encoding="utf-8")
    logger.log("benchmark_complete", models=[m.model for m in metrics])
    return metrics
