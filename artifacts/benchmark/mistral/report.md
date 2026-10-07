# Экспресс-обзор: Leber Hereditary Optic Neuropathy (LHON)

**Исследовательский запрос:** LHON: за последние 3-5 лет сравни митохондриально-таргетные терапии (idebenone, gene therapy, elamipretide) с традиционной поддерживающей терапией/стандартом ведения и оцени перспективность направлений.
**Модель:** `mistral/mistral-small-latest`
**Временное окно:** последние 5 лет
**Стандарт лечения для сравнения:** Supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins (e.g., tobacco, alcohol) as the most widely accepted comparator for LHON management

## План Root-оркестратора

- search
- extraction
- comparison
- evaluation
- visualization
- report

## Качество прогона

- Найдено уникальных источников: **14**
- Успешных structured extractions: **14**
- Прошли reviewer: **1**
- Отклонено: **13**
- Retry после feedback reviewer: **14**
- Reviewer pass rate: **7.1%**
- Сравнений mito vs standard: **1**
- Оценённых направлений: **2**

## Рейтинг перспективности

> Балл 0-100 выставляет LLM-субагент Evaluator по runtime skill `promisingness_criteria`. Это исследовательская оценка, а не клиническая рекомендация.

| Rank | Категория | Направление | Score | Evidence level | Confidence |
|---:|---|---|---:|---|---|
| 1 | mitochondrial | idebenone | 40 | low | low |
| 2 | standard | supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins | 30 | unclear | low |

## Самое и наименее перспективное митохондриальное направление

- **Топ:** idebenone - 40/100. The only reviewer-passed evidence for idebenone in LHON is a single clinical trial with low evidence level, showing variable and context-dependent outcomes. This yields a score of 40/100: 35% for low-quality clinical trial evidence (12/35), 25% for early clinical maturity (6/25), 25% for unclear/neutral observed effect (6/25), and 15% for being compared against a widely accepted but consensus-based standard (4/15). The main limitation is the lack of robust, reproducible evidence and absence of direct comparator data.
- **Аутсайдер:** idebenone - 40/100. The only reviewer-passed evidence for idebenone in LHON is a single clinical trial with low evidence level, showing variable and context-dependent outcomes. This yields a score of 40/100: 35% for low-quality clinical trial evidence (12/35), 25% for early clinical maturity (6/25), 25% for unclear/neutral observed effect (6/25), and 15% for being compared against a widely accepted but consensus-based standard (4/15). The main limitation is the lack of robust, reproducible evidence and absence of direct comparator data.

## Сравнение с традиционным лечением

### idebenone vs supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins
- Относительная доказательная база: **weaker**
- Вывод: Evidence for idebenone in LHON consists of a single clinical trial with low evidence level, showing variable and context-dependent visual outcomes depending on disease stage and mutation type. The standard comparator (supportive care) is widely accepted but lacks high-quality interventional evidence; however, its use is based on clinical consensus rather than controlled trials.
- Источники: 39704163
- Ограничения: No head-to-head comparison with supportive care; idebenone evidence is limited to a single clinical trial with low evidence level and unclear effect magnitude; Outcomes are highly dependent on LHON stage and mutation type, limiting generalizability; Standard comparator lacks interventional evidence but is based on clinical consensus


## Проверенные данные

### idebenone
- Track: mitochondrial
- Source: [39704163](https://pubmed.ncbi.nlm.nih.gov/39704163/); DOI: `10.1097/WCO.0000000000001343`
- Disease: Leber hereditary optic neuropathy (LHON)
- Target: не указано
- Study type: clinical_trial
- Evidence level: low
- Phase: не указано
- n: не указано
- Outcome: visual outcomes (effect varies by LHON stage and mutation; early initiation and ≥24 months treatment suggested)
- Effect: variable and context-dependent; favorable for m.11778G>A and chronic eyes with m.14484T>C, caution in subacute/dynamic eyes with m.3460G>A due to possible worsening
- Effect class: unclear
- Supporting quote: “Evidence from three clinical studies (RHODOS, RHODOS-OFU, and LEROS) suggest that idebenone should be started early and continued for at least 24 months. Treatment effect varies according to the stage of LHON and the underlying mutation. Favourable outcomes are associated with the m.11778G>A mutation and chronic eyes with the m.14484T>C mutation. Caution should be taken in subacute/dynamic eyes with the m.3460G>A mutation, due to possible clinical worsening with idebenone.”

## Ограничения

- Это экспресс-обзор, а не систематический обзор или метаанализ.
- PubMed abstracts и записи ClinicalTrials.gov могут не содержать всех деталей для полноценной risk-of-bias оценки.
- Cross-study сравнение не эквивалентно head-to-head исследованию.
- Reviewer сочетает LLM-семантическую проверку с детерминированными guardrails по provenance, quote и n.
- Оценка перспективности зависит от полноты найденных данных и rubric skill; это не медицинская рекомендация.
- Временное окно применяется к PubMed и к first-posted ClinicalTrials.gov приблизительно за последние 3-5 лет.
