# Scripts

Вспомогательные скрипты для проекта.

## generate_sca_summary.py

Генерирует сводку по уязвимостям из SCA отчёта Grype.

Используется в CI workflow как fallback, если `jq` недоступен.

**Использование:**
```bash
python3 scripts/generate_sca_summary.py
```

Скрипт читает `EVIDENCE/P09/sca_report.json` и создаёт `EVIDENCE/P09/sca_summary.md`.

## test_sbom_sca.sh

Локальный тестовый скрипт для проверки SBOM и SCA сканирования.

**Требования:**
- Docker
- Bash

**Использование:**
```bash
bash scripts/test_sbom_sca.sh
```

Скрипт выполняет:
1. Генерацию SBOM с помощью Syft
2. SCA сканирование с помощью Grype
3. Генерацию сводки по уязвимостям

Артефакты сохраняются в `EVIDENCE/P09/`.

