# Harness для анализа исследований в митохондриальной медицине

Прототип исследовательского Harness по тестовому заданию ANTEI × ИТМО. Система принимает исследовательский запрос, строит план, ищет свежие источники, извлекает факты, валидирует их отдельным LLM-reviewer, сравнивает митохондриально-таргетные направления со стандартом лечения, оценивает перспективность, строит график и формирует Markdown-отчёт с PMID / DOI / NCT.

Система является исследовательским инструментом и не предназначена для клинических рекомендаций конкретным пациентам.

## Что соответствует must-have требованиям

### 1. Метапромпт и Root-оркестратор

`agents/planner.py` использует LLM как Root-оркестратор. Он получает пользовательский запрос и формирует план по обязательной последовательности:

```text
поиск -> извлечение -> сравнение -> оценка -> визуализация -> отчёт
```

`orchestrator.py` исполняет план, делегирует задачи специализированным субагентам, вызывает инструменты, собирает результат и пишет решения в `run.jsonl`.

### 2. 5 специализированных LLM-субагентов:

1. `literature_searcher` - планирует поиск литературы и отдельно формирует митохондриальный поисковый трек и трек стандартного лечения;
2. `extractor` - извлекает препарат/вмешательство, мишень, заболевание, дизайн, фазу, n, исход, эффект и подтверждающую цитату;
3. `comparator` - сравнивает reviewer-passed митохондриальные направления со стандартом лечения;
4. `evaluator` - оценивает перспективность направлений по динамически загружаемой шкале и выставляет балл 0-100;
5. `reviewer` - отдельная LLM, которая проверяет ссылки, цифры, смысловую согласованность и отсутствие выдуманных выводов.

Дополнительно Root-оркестратор также использует LLM для построения плана.

### 3. Инструменты

Используются 4 атомарных инструмента:

- `tools/pubmed.py` - PubMed E-utilities;
- `tools/clinical_trials.py` - ClinicalTrials.gov API v2;
- Pydantic-парсер структурированного вывода внутри `llm.py` - каждый LLM-ответ валидируется по строгой схеме;
- `tools/plotting.py` - расчёт/визуализация через matplotlib;
- дополнительно `tools/validation.py` - детерминированные защитные проверки происхождения источника, дословной цитаты и размера выборки.

### 4. Динамические Skills

Все назначения skills находятся только в `skills/registry.json`:

```json
{
  "searcher": ["literature_search.md"],
  "extractor": ["evidence_grading.md", "clinical_outcome_extraction.md"],
  "reviewer": ["citation_validation.md", "semantic_validation.md"],
  "comparator": ["comparison_rules.md", "evidence_grading.md"],
  "evaluator": ["promisingness_criteria.md", "evidence_grading.md"]
}
```

Код агента не перечисляет конкретные skill-файлы. Он знает только своё имя роли и вызывает:

```python
render_agent_skills("reviewer")
```

`skill_loader.py` во время выполнения читает `registry.json`, загружает весь набор навыков этой роли и добавляет его в системный промпт субагента.

Поэтому, например, чтобы добавить reviewer новый skill, достаточно изменить `registry.json`; Python-код reviewer менять не нужно.

## Каталог skills

```text
skills/
├── registry.json
├── literature_search.md
├── evidence_grading.md
├── clinical_outcome_extraction.md
├── citation_validation.md
├── semantic_validation.md
├── comparison_rules.md
└── promisingness_criteria.md
```

Видимое влияние skills:

- `clinical_outcome_extraction.md` задаёт правила извлечения данных из статьи или клинического исследования: вмешательство, дизайн исследования, фазу, размер выборки, клинический исход и наблюдаемый эффект. Определяет, как отличать цель исследования от фактически полученного результата и что делать, если данных недостаточно;
- `semantic_validation.md` задаёт правила проверки извлечённых данных. Reviewer сверяет, соответствует ли тип исследования источнику, действительно ли указанное вмешательство является терапией, подтверждаются ли исход и эффект текстом статьи и не сделаны ли выводы сильнее, чем позволяет источник;
- `comparison_rules.md` задаёт правила сравнения терапевтических направлений со стандартным лечением. Comparator учитывает качество и тип доказательств, результаты исследований и наличие прямого сравнения между подходами; если прямого исследования нет, вывод формулируется как непрямое сопоставление, а не как доказанное превосходство;
- `promisingness_criteria.md` задаёт шкалу оценки перспективности направления от 0 до 100 с учётом качества доказательств, клинической зрелости, наблюдаемого эффекта и сравнения со стандартным лечением; отдельно ограничивает слишком высокие оценки для направлений, подтверждённых только доклиническими данными.

## Архитектура

```text
                         Пользовательский запрос
                                  |
                         Root Orchestrator LLM
                                  |
                    план + решения + JSONL log
                                  |
                    Literature Searcher LLM
                      /                       \
        mitochondrial search track      standard-care track
              /          \                 /          \
          PubMed     ClinicalTrials    PubMed     ClinicalTrials
              \          /                 \          /
                       SourceDocument[]
                              |
                         Extractor LLM
                              |
                    Pydantic EvidenceRecord
                              |
             deterministic validation guardrails
                              |
                         Reviewer LLM
                    /                      \
                 PASS                     FAIL
                  |                         |
                  |                feedback -> retry
                  |                         |
                  +-------------------------+
                              |
                     reviewer-passed evidence
                              |
                       Comparator LLM
                 mito therapy vs standard care
                              |
                        Evaluator LLM
                    promisingness score 0-100
                              |
                       Plotting tool
                              |
                     Markdown report
```

## Reviewer и цикл обратной связи

Reviewer теперь является настоящим LLM-субагентом. При этом объективные проверки оставлены как guardrails:

- совпадение `source_id`, URL, типа источника, DOI и поискового трека;
- дословное наличие `source_quote` в тексте источника;
- наличие извлечённого `n` в тексте источника.

После этого LLM-reviewer независимо проверяет:

- корректность `study_type` и уровня доказательности;
- поддерживает ли цитата заявленный effect;
- не перепутаны ли цель исследования и результат;
- не интерпретирован ли патологический механизм как терапевтическая польза;
- не является ли "intervention" диагностическим тестом/registry;
- не сделан ли causal/efficacy вывод из наблюдательной ассоциации.

Если запись не проходит review, reviewer возвращает `feedback_to_extractor`; оркестратор делает одну повторную extraction-попытку и логирует обратную связь.

## Оценщик перспективности

`agents/evaluator.py` - отдельный LLM-субагент. Он получает только:

1. записи `EvidenceRecord`, прошедшие reviewer;
2. результат Comparator;
3. динамически загруженный навык `promisingness_criteria.md`.

Он выставляет score `0-100` по четырём компонентам:

- 35% качество доказательств;
- 25% клиническая зрелость;
- 25% наблюдаемый эффект;
- 15% положение относительно стандарта лечения.

Это исследовательская rubric, а не валидированная клиническая шкала.

## Сравнение со стандартом лечения

Поисковик литературы строит два независимых поисковых трека для одного заболевания:

```text
mitochondrial
standard
```

Каждый `SourceDocument` получает `evidence_track`. После проверки Comparator видит обе группы и формирует осторожный вывод:

```text
stronger / similar / weaker / insufficient
```

Если head-to-head данных нет, Comparator не имеет права утверждать прямое превосходство терапии.

## Защита от вымышленных ссылок

LLM не генерирует PMID, DOI, NCT или URL.

Идентификаторы берутся Python-клиентами PubMed/ClinicalTrials.gov и добавляются к `EvidenceRecord` после extraction. Reviewer затем проверяет, что запись осталась привязана к исходному `SourceDocument`.

## Временное окно

Root-оркестратор выбирает окно 3-5 лет.

- PubMed: фильтрация по дате публикации;
- ClinicalTrials.gov: приблизительная фильтрация по `studyFirstPostDate`.

## Воспроизводимый запуск

Требуется Python 3.11+.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Установка:

```bash
pip install -r requirements.txt
```

Создайте `.env` по примеру `.env.example`:

```env
MISTRAL_API_KEY=...
MISTRAL=mistral-small-latest

DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-v4-flash
```

Один исследовательский запрос:

```bash
python main.py --max-pubmed 6 --max-trials 6
```

Два воспроизводимых запроса для двух заболеваний (LHON и болезнь Паркинсона):

```bash
python main.py --demo --max-pubmed 4 --max-trials 4
```

Свой запрос:

```bash
python main.py --query "Сравни митохондриальные подходы и стандарт лечения при LHON за последние 3-5 лет"
```

## Benchmark двух LLM

Бонусный режим сохранён. Поиск и набор источников формируются один раз, после чего одинаковые sources анализируются двумя моделями:

```bash
python main.py --benchmark --max-pubmed 4 --max-trials 4
```

Benchmark не является тестом точности: без ручной эталонной разметки он показывает стабильность конвейера, долю прохождения reviewer и время выполнения.

## Артефакты

Обычный запуск создаёт:

```text
artifacts/latest/
├── run.jsonl
├── research_plan.json
├── search_plan.json
├── sources.json
├── evidence.json
├── rejected.json
├── comparisons.json
├── ranking.json
├── metrics.json
├── comparison.png
└── report.md
```

`report.md` содержит реальные PMID / DOI / NCT из API, сравнение с традиционным лечением, рейтинг перспективности, топ/аутсайдер и ограничения.

## Пример лога

```text
[delegate] root_orchestrator
[plan] search -> extraction -> comparison -> evaluation -> visualization -> report
[delegate] literature_searcher skills=[literature_search]
[tool_call] pubmed_search track=mitochondrial
[tool_call] pubmed_search track=standard
[delegate] extractor skills=[evidence_grading, clinical_outcome_extraction]
[delegate] reviewer skills=[citation_validation, semantic_validation]
[feedback] reviewer -> extractor
[delegate] comparator skills=[comparison_rules, evidence_grading]
[delegate] evaluator skills=[promisingness_criteria, evidence_grading]
[tool_call] plotting_sandbox
[model_run_complete]
```

## Ограничения

- Это экспресс-обзор, не систематический review и не meta-analysis.
- Данные аннотаций и регистрационных записей могут быть недостаточны для полноценной risk-of-bias оценки.
- Непрямое сравнение разных исследований не равно прямому сравнительному исследованию.
- LLM-reviewer снижает риск смысловых ошибок, но не заменяет ручную экспертную проверку.
- Оценка перспективности зависит от найденной доказательной базы и используемой шкалы.
- Временное окно ClinicalTrials.gov фильтруется по дате первой публикации записи и является приближением.

## Структура проекта

```text
.
├── agents/
│   ├── planner.py
│   ├── searcher.py
│   ├── extractor.py
│   ├── reviewer.py
│   ├── comparator.py
│   └── evaluator.py
├── tools/
│   ├── pubmed.py
│   ├── clinical_trials.py
│   ├── validation.py
│   └── plotting.py
├── skills/
│   ├── registry.json
│   └── *.md
├── config.py
├── llm.py
├── schemas.py
├── skill_loader.py
├── orchestrator.py
├── runlog.py
├── main.py
├── requirements.txt
└── .env.example
```

## Как преодолеть ограничения в production-версии

- Подключить полные тексты из PubMed Central/издательских API и проверять вывод не только по abstract.
- Добавить ручной gold set на 30-50 источников и считать precision/recall для extraction и reviewer.
- Для сравнения терапий отдельно искать прямые сравнительные РКИ и не смешивать непрямое сравнение с прямым сравнением.
- Добавить навык оценки риска систематической ошибки (RoB 2 / ROBINS-I-подобный чек-лист) и отдельный LLM-субагент для методологической оценки.
- Кэшировать PubMed/ClinicalTrials.gov ответы по query+date-window для воспроизводимости и снижения нагрузки.
- Для финальных научных выводов оставлять ручное подтверждение экспертом доказательств, прошедших reviewer.
