from __future__ import annotations

from datetime import date
import xml.etree.ElementTree as ET

import httpx

from config import NCBI_EMAIL, NCBI_TOOL
from schemas import EvidenceTrack, SourceDocument

import time

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def search_pubmed(
    query: str,
    *,
    max_results: int = 6,
    years: int = 5,
    evidence_track: EvidenceTrack,
) -> list[SourceDocument]:
    current_year = date.today().year
    common = {"tool": NCBI_TOOL}
    if NCBI_EMAIL:
        common["email"] = NCBI_EMAIL

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        search = client.get(
            f"{BASE}/esearch.fcgi",
            params={
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
                "datetype": "pdat",
                "mindate": str(current_year - years),
                "maxdate": str(current_year),
                "sort": "pub date",
                **common,
            },
        )
        search.raise_for_status()
        time.sleep(0.5)
        
        ids = search.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        fetched = client.get(
            f"{BASE}/efetch.fcgi",
            params={
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "xml",
                **common,
            },
        )
        fetched.raise_for_status()
        time.sleep(0.5)

    root = ET.fromstring(fetched.text)
    docs: list[SourceDocument] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article.find(".//MedlineCitation/PMID"))
        title = _text(article.find(".//Article/ArticleTitle"))
        abstract_parts = [
            _text(x) for x in article.findall(".//Article/Abstract/AbstractText") if _text(x)
        ]
        abstract = "\n".join(abstract_parts).strip()
        if not pmid or not abstract:
            continue

        doi = None
        for aid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = _text(aid) or None
                break

        docs.append(
            SourceDocument(
                source_type="pubmed",
                source_id=pmid,
                title=title or f"PubMed {pmid}",
                text=abstract,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                doi=doi,
                evidence_track=evidence_track,
            )
        )
    return docs
