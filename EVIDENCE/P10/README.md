# P10 - SAST & Secrets Evidence

Эта папка содержит артефакты SAST (Semgrep SARIF) и сканирования секретов (Gitleaks JSON), создаваемые CI.

Файлы, которые создаёт CI (на каждый прогон / коммит):
- `semgrep.sarif` — SARIF от Semgrep (конфиг: `p/ci` + `security/semgrep/rules.yml`)
- `gitleaks.json` — отчёт Gitleaks, использующий `security/.gitleaks.toml`
- `sast_summary.md` — краткая сводка, генерируемая CI
- `triage.md` — заметки/ссылки на Issue и действия команды

Как использовать:
- Откройте `semgrep.sarif` в SARIF viewer или подключите к GitHub Code Scanning.
- Просмотрите `gitleaks.json` и определите, какие находки — реальные секреты. Ложноположительные необходимо добавить в `security/.gitleaks.toml` с комментарием и обоснованием.

Триаж и дальнейшие действия:
1. Для реальных секретов: удалить секрет, выполнить ротацию, создать Issue с ссылкой на `EVIDENCE/P10/gitleaks.json`.
2. Для критичных/High Semgrep findings: создать Issue(ы), назначить ответственных и сроки.
3. Документировать ложноположительные в `security/.gitleaks.toml` и записать причину принятия в `EVIDENCE/P10/triage.md`.

См. также: `security/semgrep/rules.yml`, `security/.gitleaks.toml`
