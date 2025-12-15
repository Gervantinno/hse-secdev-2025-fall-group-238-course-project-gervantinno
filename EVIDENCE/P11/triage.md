# P11 DAST triage notes

Заполните этот файл после прогона ZAP baseline и просмотра отчёта.

Пример записи:

- Commit: $COMMIT_SHA
- Date: YYYY-MM-DD
- Target: http://localhost:8080/
- Alerts: High=X, Medium=Y, Low=Z
- Actions:
  - High: create Issue https://github.com/<owner>/<repo>/issues/NN
  - Medium: add to backlog
  - False positives: added allowlist / documented rationale
