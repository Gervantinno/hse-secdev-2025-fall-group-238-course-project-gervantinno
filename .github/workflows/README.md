# GitHub Actions Workflows

## CI Workflow (`.github/workflows/ci.yml`)

Основной CI workflow для тестирования и деплоя.

**Триггеры:**
- `push` — на всех ветках
- `pull_request` — на все PR

**Jobs:**
- `tests` — запускает линтеры и тесты для Python 3.11 и 3.12
- `deploy` — собирает Docker образ и деплоит (только для ветки `main`)

## Security - SBOM & SCA (`.github/workflows/ci-sbom-sca.yml`)

Workflow для генерации SBOM и сканирования уязвимостей.

**Триггеры:**
- `workflow_dispatch` — ручной запуск
- `push` — при изменении файлов:
  - `**/*.py`
  - `requirements*.txt`
  - `.github/workflows/ci-sbom-sca.yml`
  - `scripts/**`
- `pull_request` — при изменении тех же файлов

**Jobs:**
- `sbom_sca` — генерирует SBOM (Syft) и выполняет SCA сканирование (Grype)

## Важные замечания

⚠️ **GitHub Actions запускаются только при push в удаленный репозиторий!**

Локальные коммиты (без `git push`) не запускают workflows. Для запуска нужно:
1. Сделать коммит: `git commit -m "message"`
2. Запушить в удаленный репозиторий: `git push`

Если workflow не запускается после push:
- Проверьте, что файлы изменены в указанных путях (для `ci-sbom-sca.yml`)
- Убедитесь, что workflow файлы находятся в `.github/workflows/`
- Проверьте логи в разделе Actions на GitHub

