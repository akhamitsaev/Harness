from __future__ import annotations

from datetime import date
import json
import re

import httpx

from schemas import EvidenceTrack, SourceDocument

BASE = "https://clinicaltrials.gov/api/v2/studies"


def _join(values) -> str:
    if not values:
        return ""
    if isinstance(values, list):
        return "; ".join(str(v) for v in values if v)
    return str(values)


def _year(value: str | None) -> int | None:
    if not value:
        return None
    m = re.search(r"(19|20)\d{2}", value)
    return int(m.group(0)) if m else None


def search_clinical_trials(
    condition: str,
    *,
    intervention_query: str | None = None,
    max_results: int = 6,
    years: int = 5,
    evidence_track: EvidenceTrack,
) -> list[SourceDocument]:
    params: dict[str, str | int] = {
        "query.cond": condition,
        "pageSize": max_results,
        "format": "json",
    }
    if intervention_query:
        params["query.intr"] = intervention_query

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(BASE, params=params)
        response.raise_for_status()
        payload = response.json()

    cutoff_year = date.today().year - years
    docs: list[SourceDocument] = []
    for study in payload.get("studies", []):
        protocol = study.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        design = protocol.get("designModule", {})
        interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
        outcomes = protocol.get("outcomesModule", {})
        status = protocol.get("statusModule", {})
        description = protocol.get("descriptionModule", {})

        first_posted = (
            status.get("studyFirstPostDateStruct", {}).get("date")
            or status.get("studyFirstSubmitDate")
        )
        posted_year = _year(first_posted)
        if posted_year is not None and posted_year < cutoff_year:
            continue

        nct = ident.get("nctId")
        if not nct:
            continue
        title = ident.get("briefTitle") or ident.get("officialTitle") or nct

        intervention_lines: list[str] = []
        for item in interventions:
            intervention_lines.append(
                " | ".join(
                    str(x)
                    for x in [item.get("type"), item.get("name"), item.get("description")]
                    if x
                )
            )

        text_parts = [
            f"NCT ID: {nct}",
            f"Title: {title}",
            f"Study type: {design.get('studyType')}",
            f"Phases: {_join(design.get('phases'))}",
            f"Enrollment: {json.dumps(design.get('enrollmentInfo', {}), ensure_ascii=False)}",
            f"Overall status: {status.get('overallStatus')}",
            f"First posted: {first_posted}",
            f"Brief summary: {description.get('briefSummary', '')}",
            "Interventions: " + "\n".join(intervention_lines),
            "Primary outcomes: " + json.dumps(outcomes.get("primaryOutcomes", []), ensure_ascii=False),
            "Secondary outcomes: " + json.dumps(outcomes.get("secondaryOutcomes", []), ensure_ascii=False),
        ]
        docs.append(
            SourceDocument(
                source_type="clinicaltrials",
                source_id=nct,
                title=title,
                text="\n".join(text_parts),
                url=f"https://clinicaltrials.gov/study/{nct}",
                doi=None,
                evidence_track=evidence_track,
            )
        )
    return docs
