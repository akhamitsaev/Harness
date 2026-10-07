from __future__ import annotations

import json

from llm import call_structured_llm
from schemas import ResearchPlan


def build_research_plan(query: str, *, model: str) -> ResearchPlan:
    system = """You are the Root Orchestrator of a mitochondrial-medicine research Harness.
Build a concise executable research plan. The Harness MUST follow this sequence:
search -> extraction -> comparison -> evaluation -> visualization -> report.
Delegate work to five specialized LLM sub-agents: literature_searcher, extractor,
comparator, evaluator, reviewer. Keep the scope to 1-4 diseases and a 3-5 year window.
This is an express research review, not patient-specific medical advice.
"""
    return call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=f"Research request:\n{query}",
        response_model=ResearchPlan,
    )
