# Skill: семантическая валидация

Reviewer независимо проверяет смысл extraction:

- study_type соответствует фактическому дизайну;
- systematic review не классифицируется как observational только потому, что анализирует клинические образцы;
- intervention действительно является вмешательством, а не диагностическим тестом, registry или измерением;
- отсутствие intervention несовместимо с терапевтическим effect_class, отличным от unclear;
- preclinical mechanism без лечения не интерпретируется как therapeutic benefit;
- effect_class соответствует именно выбранному outcome;
- causal или efficacy вывод не делается из observational association;
- reviewer должен вернуть краткий actionable feedback, который extractor может использовать в retry.
