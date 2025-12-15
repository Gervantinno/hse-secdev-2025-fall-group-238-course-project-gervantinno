# P09 - SBOM & SCA Integration

## Описание

Добавлен автоматический workflow для генерации SBOM (Software Bill of Materials) и проведения SCA (Software Composition Analysis) сканирования зависимостей проекта.

## Что сканируется

- Python-зависимости из `requirements.txt` и `requirements-dev.txt`
- Все Python-файлы проекта (`**/*.py`)
- Транзитивные зависимости всех установленных пакетов

## Инструменты

- **Syft** (latest) — генерация SBOM в формате CycloneDX JSON
- **Grype** (latest) — сканирование уязвимостей на основе SBOM

## Артефакты

Все артефакты генерируются автоматически в каталоге `EVIDENCE/P09/`:

- `sbom.json` — полный SBOM в формате CycloneDX JSON
- `sca_report.json` — детальный отчёт о найденных уязвимостях от Grype
- `sca_summary.md` — краткая сводка по уязвимостям, сгруппированная по severity (Critical, High, Medium, Low, Negligible)

Артефакты также доступны через GitHub Actions artifacts (название: `P09_EVIDENCE`).

## Триггеры workflow

Workflow автоматически запускается при:
- Push в ветки с изменениями в:
  - `**/*.py`
  - `requirements*.txt`
  - `.github/workflows/ci-sbom-sca.yml`
- Ручной запуск через `workflow_dispatch`

## Политика работы с уязвимостями

Создан файл `policy/waivers.yml` для управления исключениями (waivers) по уязвимостям. Структура waivers включает:
- ID уязвимости (CVE)
- Пакет и версия
- Обоснование исключения
- Срок действия waiver
- Утверждающий

Подробности см. в `project/69_sbom-vuln-mgmt.md`.

## Дальнейшие действия

1. После успешного прогона workflow проверить `sca_summary.md` на наличие критических уязвимостей
2. Для найденных уязвимостей:
   - **Фикс**: обновить зависимости до безопасных версий
   - **Waiver**: оформить исключение в `policy/waivers.yml` с обоснованием
3. Использовать артефакты для:
   - Документирования в итоговом отчёте (DS1)
   - Регулярного мониторинга безопасности зависимостей
   - Compliance и аудита

## Ссылки

- Workflow: `.github/workflows/ci-sbom-sca.yml`
- Артефакты: `EVIDENCE/P09/`
- Политика: `policy/waivers.yml`
- GitHub Actions job: [будет добавлена после первого успешного прогона]

