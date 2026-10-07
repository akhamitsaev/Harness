from __future__ import annotations

import json

from llm import call_structured_llm
from schemas import ResearchPlan, SearchPlan
from skill_loader import render_agent_skills


def build_search_plan(
    query: str,
    research_plan: ResearchPlan,
    *,
    model: str,
) -> SearchPlan:
    skills = render_agent_skills("searcher")
    system = f"""You are the literature-search sub-agent for mitochondrial medicine.
Your task is to translate the research request into reproducible PubMed and ClinicalTrials.gov searches.
You do not evaluate efficacy and do not invent results.

Runtime skills assigned to you:
{skills}
"""
    prompt = f"""Research request:
{query}

Root research plan:
{json.dumps(research_plan.model_dump(), ensure_ascii=False, indent=2)}

Create one mitochondrial-therapy search track and one traditional/standard-of-care search track
for the same disease. Keep the PubMed queries specific enough for an express review.
"""
    return call_structured_llm(
        model=model,
        system_prompt=system,
        user_prompt=prompt,
        response_model=SearchPlan,
    )
