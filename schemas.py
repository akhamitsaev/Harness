from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


EffectClass = Literal[
    "positive_significant",
    "positive_non_significant",
    "neutral_or_no_difference",
    "negative_or_harmful",
    "mixed",
    "unclear",
]
EvidenceTrack = Literal["mitochondrial", "standard", "mixed"]


class ResearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objective: str
    diseases: list[str] = Field(min_length=1, max_length=4)
    time_window_years: int = Field(default=5, ge=3, le=5)
    steps: list[str]
    delegations: list[str]


class SearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    disease: str
    standard_of_care: str
    pubmed_mito_query: str
    pubmed_standard_query: str
    clinical_trials_condition: str
    clinical_trials_mito_interventions: str | None = None
    clinical_trials_standard_interventions: str | None = None


class SourceDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_type: Literal["pubmed", "clinicaltrials"]
    source_id: str
    title: str
    text: str
    url: str
    doi: str | None = None
    evidence_track: EvidenceTrack


class ExtractedEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intervention: str | None = None
    target: str | None = None
    disease: str | None = None
    study_type: Literal[
        "systematic_review",
        "RCT",
        "controlled_trial",
        "clinical_trial",
        "observational",
        "case_series",
        "preclinical",
        "other",
    ]
    evidence_level: Literal["high", "moderate", "low", "very_low", "preclinical", "unclear"]
    phase: str | None = None
    n: int | None = Field(default=None, ge=1)
    outcome: str | None = None
    effect: str | None = None
    effect_class: EffectClass = "unclear"
    source_quote: str | None = None


class EvidenceRecord(ExtractedEvidence):
    source_type: Literal["pubmed", "clinicaltrials"]
    source_id: str
    source_url: str
    doi: str | None = None
    evidence_track: EvidenceTrack


class LLMReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passed: bool
    semantic_consistency: bool
    citation_support: bool
    numeric_support: bool
    issues: list[str]
    feedback_to_extractor: str | None = None


class ReviewResult(BaseModel):
    passed: bool
    deterministic_passed: bool
    llm_passed: bool
    quote_verified: bool
    sample_size_verified: bool
    semantic_consistency: bool
    issues: list[str]
    feedback_to_extractor: str | None = None


class ComparisonResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mitochondrial_intervention: str
    standard_comparator: str
    relative_evidence: Literal["stronger", "similar", "weaker", "insufficient"]
    summary: str
    supporting_source_ids: list[str]
    limitations: list[str]


class ComparisonBundle(BaseModel):
    comparisons: list[ComparisonResult]


class DirectionAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intervention: str
    display_name: str = Field(max_length=60)
    category: Literal["mitochondrial", "standard"]
    score: int = Field(ge=0, le=100)
    evidence_level: Literal["high", "moderate", "low", "very_low", "preclinical", "unclear"]
    confidence: Literal["high", "medium", "low"]
    rationale: str
    main_limitations: list[str]
    supporting_source_ids: list[str]


class AssessmentBundle(BaseModel):
    assessments: list[DirectionAssessment]


class RunMetrics(BaseModel):
    model: str
    source_count: int
    extraction_success_count: int
    first_pass_review_count: int
    final_review_pass_count: int
    rejected_count: int
    retry_count: int
    comparison_count: int
    assessment_count: int
    reviewer_pass_rate: float
    total_runtime_sec: float
