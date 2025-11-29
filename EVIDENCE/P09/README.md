# P09 - SBOM & SCA Evidence

Этот каталог содержит артефакты, сгенерированные workflow `Security - SBOM & SCA`.

## Файлы

- **sbom.json** — Software Bill of Materials в формате CycloneDX JSON, сгенерированный с помощью Syft
- **sca_report.json** — отчёт о сканировании уязвимостей (SCA) от Grype на основе SBOM
- **sca_summary.md** — краткая сводка по уязвимостям, сгруппированная по severity

## Генерация

Артефакты автоматически генерируются при:
- Push в ветки с изменениями в `**/*.py`, `requirements*.txt` или самом workflow
- Ручном запуске через `workflow_dispatch`

## Использование

Артефакты доступны через:
1. GitHub Actions artifacts (название: `P09_EVIDENCE`)
2. Локально в этом каталоге после успешного прогона workflow

## Связь с коммитами

Каждый прогон workflow привязан к конкретному коммиту. Ссылка на успешный job доступна в описании PR.

