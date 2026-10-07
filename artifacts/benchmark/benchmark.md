# Benchmark двух LLM

Обе модели анализировали один и тот же набор источников. Поиск выполнен один раз.

| Model | Sources | Reviewer passed | Rejected | Runtime, s |
|---|---:|---:|---:|---:|
| mistral/mistral-small-latest | 14 | 1 | 13 | 123.09 |
| deepseek/deepseek-v4-flash | 14 | 8 | 6 | 604.88 |

> Это сравнение стабильности/проходимости pipeline, а не accuracy: без ручного gold set нельзя утверждать, какая LLM научно точнее.