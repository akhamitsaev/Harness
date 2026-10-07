# Экспресс-обзор: Leber Hereditary Optic Neuropathy (LHON)

**Исследовательский запрос:** LHON: за последние 3-5 лет сравни митохондриально-таргетные терапии (idebenone, gene therapy, elamipretide) с традиционной поддерживающей терапией/стандартом ведения и оцени перспективность направлений.
**Модель:** `deepseek/deepseek-v4-flash`
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
- Прошли reviewer: **8**
- Отклонено: **6**
- Retry после feedback reviewer: **10**
- Reviewer pass rate: **57.1%**
- Сравнений mito vs standard: **4**
- Оценённых направлений: **4**

## Рейтинг перспективности

> Балл 0-100 выставляет LLM-субагент Evaluator по runtime skill `promisingness_criteria`. Это исследовательская оценка, а не клиническая рекомендация.

| Rank | Категория | Направление | Score | Evidence level | Confidence |
|---:|---|---|---:|---|---|
| 1 | mitochondrial | Lenadogene nolparvovec (gene therapy) | 74 | moderate | medium |
| 2 | mitochondrial | Idebenone | 70 | moderate | medium |
| 3 | mitochondrial | NR082 (rAAV2-ND4) gene therapy | 30 | unclear | low |
| 4 | mitochondrial | Preclinical mitochondrial-targeted approaches (mNP-Mito, AAV2 mitochondrial transfer) | 15 | preclinical | low |

## Самое и наименее перспективное митохондриальное направление

- **Топ:** Lenadogene nolparvovec (gene therapy) - 74/100. A moderate-quality systematic review (39419122) reports a strong positive significant effect (CRR 59% vs 17% untreated), supported by a low-quality observational/other source (39704163) showing sustained bilateral visual improvement compared with published natural history. The clinical program is late-phase. However, the primary comparator in the available evidence is untreated/published natural history, not the configured standard of care, and no supportive-care outcome data were supplied. Therefore relative evidence versus standard of care is insufficient, which limits the score and confidence. The main limiting factor is the lack of head-to-head comparison with supportive care.
- **Аутсайдер:** Preclinical mitochondrial-targeted approaches (mNP-Mito, AAV2 mitochondrial transfer) - 15/100. Both sources are preclinical animal-model studies. mNP-Mito increased complex I activity and promoted ATP restoration but no p-value or statistical significance was reported (effect_class unclear). AAV2 mitochondrial transfer accelerated mitochondrial transfer in a rotenone model but is proposed as an explanation rather than a demonstrated therapy. Per rubric, preclinical-only directions should not exceed 60, and here observed effect is unclear and no human data exist. The main limiting factor is the absence of any clinical evidence and lack of statistical significance.

## Сравнение с традиционным лечением

### Idebenone vs Supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins (e.g., tobacco, alcohol) as the most widely accepted comparator for LHON management
- Относительная доказательная база: **insufficient**
- Вывод: Reviewer-passed evidence includes a systematic review (source 39419122) reporting clinically relevant recovery from nadir (CRR) of 31% [24%; 40%] in idebenone-treated patients versus 17% [7%; 30%] in untreated patients. The comparator is untreated natural history, not the configured standard of care (supportive care, visual rehabilitation, low-vision aids, toxin avoidance). No reviewer-passed evidence on outcomes with supportive care alone was supplied. Therefore the relative evidence for idebenone versus standard of care cannot be determined and is classified as insufficient.
- Источники: 39419122
- Ограничения: No reviewer-passed evidence on supportive care outcomes was provided.; The available comparator is untreated natural history, not the configured standard of care.; No head-to-head randomized comparison of idebenone versus supportive care is available in the supplied evidence.

### Lenadogene nolparvovec (gene therapy) vs Supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins (e.g., tobacco, alcohol) as the most widely accepted comparator for LHON management
- Относительная доказательная база: **insufficient**
- Вывод: Reviewer-passed evidence includes a systematic review (39419122) reporting CRR of 59% [54%; 64%] with lenadogene nolparvovec versus 17% [7%; 30%] untreated, and another source (39704163) reporting sustained bilateral visual improvement compared with published natural history. These comparisons are against untreated/published natural history, not the configured standard of care. No reviewer-passed evidence on supportive care outcomes was supplied, so relative evidence versus standard of care is insufficient.
- Источники: 39419122, 39704163
- Ограничения: No reviewer-passed evidence on supportive care outcomes.; Comparator in available studies is untreated/published natural history, not supportive care.; No head-to-head trial of lenadogene nolparvovec versus supportive care in the supplied evidence.

### NR082 (rAAV2-ND4) gene therapy vs Supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins (e.g., tobacco, alcohol) as the most widely accepted comparator for LHON management
- Относительная доказательная база: **insufficient**
- Вывод: Reviewer-passed evidence includes two registered clinical trials of NR082 (NCT05293626, NCT07406854) but no reported efficacy outcomes or effects. There is no reviewer-passed evidence on supportive care outcomes. Therefore relative evidence versus standard of care is insufficient.
- Источники: NCT05293626, NCT07406854
- Ограничения: No efficacy results reported in the supplied evidence.; No supportive care comparator evidence supplied.; One trial is Phase 3 but effect is null/unclear.

### Preclinical mitochondrial-targeted approaches (mNP-Mito, AAV2 mitochondrial transfer) vs Supportive care including visual rehabilitation, low-vision aids, and avoidance of known optic nerve toxins (e.g., tobacco, alcohol) as the most widely accepted comparator for LHON management
- Относительная доказательная база: **insufficient**
- Вывод: Reviewer-passed preclinical evidence includes mNP-Mito (39807326) and AAV2 mitochondrial transfer (39332508) in animal models, but these are not clinical interventions and no supportive care comparator evidence is supplied. Relative evidence versus standard of care is insufficient.
- Источники: 39807326, 39332508
- Ограничения: Preclinical only; no human efficacy data.; No supportive care comparator evidence.; No direct or indirect comparison with standard of care possible.


## Проверенные данные

### Idebenone; lenadogene nolparvovec (gene therapy)
- Track: mitochondrial
- Source: [39419122](https://pubmed.ncbi.nlm.nih.gov/39419122/); DOI: `10.1016/j.survophthal.2024.10.002`
- Disease: Leber hereditary optic neuropathy (LHON)
- Target: m.11778G>A MT-ND4
- Study type: systematic_review
- Evidence level: moderate
- Phase: Phase 3
- n: не указано
- Outcome: Clinically relevant recovery (CRR) from nadir and final best-corrected visual acuity (BCVA)
- Effect: CRR from nadir [95% CI] at eye level was 17% [7%; 30%] (n=316 eyes) in untreated, 31% [24%; 40%] (n=313) in idebenone-treated, and 59% [54%; 64%] (n=348) in lenadogene nolparvovec-treated patients; a gradient of efficacy was also observed for CRR at patient level and final BCVA.
- Effect class: positive_significant
- Supporting quote: “There was a gradient of efficacy in all assessed visual outcomes, more marked for CRR than for final BCVA, with lenadogene nolparvovec gene therapy superior to idebenone treatment, and both superior to the natural history of the disease.”

### lenadogene nolparvovec gene therapy
- Track: mitochondrial
- Source: [39704163](https://pubmed.ncbi.nlm.nih.gov/39704163/); DOI: `10.1097/WCO.0000000000001343`
- Disease: Leber hereditary optic neuropathy
- Target: m.11778G>A
- Study type: other
- Evidence level: low
- Phase: не указано
- n: не указано
- Outcome: sustained bilateral visual improvement in m.11778G>A LHON patients aged ≥15 years when treated within 1 year of onset
- Effect: a single intravitreal injection of lenadogene nolparvovec can result in sustained bilateral visual improvement; treatment effect is modest but final visual acuity (~1.2 logMAR) significantly differs from the published natural history of LHON
- Effect class: positive_significant
- Supporting quote: “a single intravitreal injection of lenadogene nolparvovec can result in sustained bilateral visual improvement in m.11778G>A LHON patients aged ≥15 years when treated within 1 year of onset. Although the treatment effect is modest, the final visual acuity of treated patients (∼1.2 logMAR) significantly differs from the published natural history of LHON”

### PARKIN mRNA-loaded nanoparticle-engineered mitochondria (mNP-Mito)
- Track: mitochondrial
- Source: [39807326](https://pubmed.ncbi.nlm.nih.gov/39807326/); DOI: `10.1016/j.apsb.2024.08.007`
- Disease: Leber's hereditary optic neuropathy (LHON)
- Target: mitochondrial complex I (via replacement of dysfunctional mitochondria)
- Study type: preclinical
- Evidence level: preclinical
- Phase: не указано
- n: не указано
- Outcome: Complex I activity, restoration of ATP generation, and mitigation of ocular mitochondrial disease-related phenotypes in a rotenone-induced mouse model
- Effect: mNP-Mito increased complex I activity to 76.5% vs 29.5% in the Rot-damaged group and promoted ATP generation restoration and phenotype mitigation; no p-value or statistical significance was reported.
- Effect class: unclear
- Supporting quote: “mNP-Mito enhanced the presence of healthy mitochondria and exhibited a sharp increase in complex I activity (76.5%) compared to the group exposed to Rot damage (29.5%), which greatly promoted the restoration of ATP generation and mitigation of ocular mitochondrial disease-related phenotypes.”

### Gene therapy, RNA-based treatments, antioxidants (e.g., idebenone)
- Track: mitochondrial
- Source: [39766826](https://pubmed.ncbi.nlm.nih.gov/39766826/); DOI: `10.3390/genes15121559`
- Disease: Optic neuropathies (dominant optic atrophy, Leber hereditary optic neuropathy, glaucoma)
- Target: OPA1, mtDNA genes (LHON), MYOC, OPTN, TBK1
- Study type: systematic_review
- Evidence level: low
- Phase: не указано
- n: не указано
- Outcome: не указано
- Effect: не указано
- Effect class: unclear
- Supporting quote: “Innovative therapeutics, including gene therapy, RNA-based treatments, and antioxidants such as idebenone, exhibit promise for alleviating optic nerve damage and safeguarding vision.”

### Gene therapy
- Track: mitochondrial
- Source: [39462921](https://pubmed.ncbi.nlm.nih.gov/39462921/); DOI: `10.4103/IJO.IJO_594_24`
- Disease: Leber's hereditary optic neuropathy
- Target: не указано
- Study type: other
- Evidence level: unclear
- Phase: не указано
- n: не указано
- Outcome: не указано
- Effect: не указано
- Effect class: unclear
- Supporting quote: “Gene therapy, particularly for conditions such as Leber's hereditary optic neuropathy, marks a new frontier in personalized medicine, offering hope for previously untreatable conditions.”

### AAV2 encoding fluorescent proteins targeting mitochondria
- Track: mitochondrial
- Source: [39332508](https://pubmed.ncbi.nlm.nih.gov/39332508/); DOI: `10.1016/j.nbd.2024.106681`
- Disease: Leber hereditary optic neuropathy (rotenone-induced mouse model of retinal damage)
- Target: Mitochondria (mitochondrial transfer along the visual system)
- Study type: preclinical
- Evidence level: preclinical
- Phase: не указано
- n: не указано
- Outcome: Mitochondria travel along the visual system (optic chiasm, primary visual cortex) to the contralateral eye in physiological conditions; in a rotenone-induced model of retinal damage mimicking LHON, mitochondrial transfer from the healthy to the damaged eye was accelerated and enhanced.
- Effect: Mitochondrial transfer from the healthy to the damaged eye was accelerated and enhanced in the rotenone-induced retinal damage model; proposed as an additional explanation for the contralateral beneficial effect observed in clinical studies with lenadogene nolparvovec.
- Effect class: unclear
- Supporting quote: “mitochondrial transfer from the healthy to the damaged eye was accelerated and enhanced”

### NR082 Injection
- Track: mitochondrial
- Source: [NCT05293626](https://clinicaltrials.gov/study/NCT05293626)
- Disease: Leber's hereditary optic neuropathy (LHON) associated with ND4 mutations
- Target: mitochondrial ND4 gene mutation
- Study type: clinical_trial
- Evidence level: low
- Phase: Phase 1/Phase 2
- n: 12
- Outcome: не указано
- Effect: не указано
- Effect class: unclear
- Supporting quote: “The objective of this clinical study is to evaluate the safety and efficacy of NR082 in the treatment of LHON caused by mitochondrial ND4 gene mutation.”

### NR082 (rAAV2-ND4), a single bilateral intravitreal (IVT) injection
- Track: mitochondrial
- Source: [NCT07406854](https://clinicaltrials.gov/study/NCT07406854)
- Disease: Leber's Hereditary Optic Neuropathy (LHON) associated with ND4 mutation
- Target: mitochondrial ND4 gene (G11778A mutation)
- Study type: RCT
- Evidence level: unclear
- Phase: PHASE3
- n: 95
- Outcome: Proportion of ≥ 0.3 LogMAR from baseline in BCVA in the study eye in the NR082 treatment and the sham-injection at Week 52 after treatment
- Effect: не указано
- Effect class: unclear
- Supporting quote: “Proportion of ≥ 0.3 LogMAR from baseline in BCVA in the study eye in the NR082 treatment and the sham-injection at Week 52 after treatment”

## Ограничения

- Это экспресс-обзор, а не систематический обзор или метаанализ.
- PubMed abstracts и записи ClinicalTrials.gov могут не содержать всех деталей для полноценной risk-of-bias оценки.
- Cross-study сравнение не эквивалентно head-to-head исследованию.
- Reviewer сочетает LLM-семантическую проверку с детерминированными guardrails по provenance, quote и n.
- Оценка перспективности зависит от полноты найденных данных и rubric skill; это не медицинская рекомендация.
- Временное окно применяется к PubMed и к first-posted ClinicalTrials.gov приблизительно за последние 3-5 лет.
