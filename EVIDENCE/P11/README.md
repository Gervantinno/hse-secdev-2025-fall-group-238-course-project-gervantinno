# P11 - DAST (OWASP ZAP baseline) evidence

Эта папка содержит отчёты, сгенерированные CI-джобой `P11 - DAST (OWASP ZAP baseline)`.

Файлы, которые должен генерировать workflow:

- `zap_baseline.html` — человекочитаемый HTML-отчёт от ZAP;
- `zap_baseline.json` — JSON-версия отчёта (машиночитаемая);
- `p11_summary-<commit>.md` — краткая сводка с указанием target и ссылки на run.

Как использовать:

- скачать артефакт P11_EVIDENCE из Actions или взять файлы из репозитория `EVIDENCE/P11/`;
- открыть `zap_baseline.html` в браузере и прочитать предупреждения;
- в PR указать: Target URL, количество предупреждений (High/Medium/Low), и план действий.
