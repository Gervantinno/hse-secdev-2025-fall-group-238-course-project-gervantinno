# ADR-002: Rate Limiting and Login Protection

Дата: 2025-11-03
Статус: Accepted

## Context

- Сервис имеет критичные эндпоинты (/login), которые требуют защиты от атак brute-force.
- Необходимо предотвратить DoS-атаки на API через чрезмерное количество запросов.
- В STRIDE.md идентифицирован риск R1 для потока F1 /login.

## Decision

- Внедрить многоуровневую систему rate limiting:
  - Глобальный лимит: 1000 запросов/минуту на IP
  - /login: 5 попыток/15 минут на IP+username
  - Остальные API: 100 запросов/минуту на токен
- Использовать Redis для хранения счётчиков.
- Возвращать заголовки `X-RateLimit-*` в ответах.
- При превышении - код 429 с Retry-After.

## Alternatives

- Использовать nginx rate limiting (минус - нет гибкости по username).
- In-memory счётчики (минус - не работает при масштабировании).
- WAF/API Gateway (минус - дополнительные затраты и сложность).

## Consequences

**Плюсы:**

- Защита от brute-force и DoS атак.
- Предсказуемое поведение при нагрузке.
- Прозрачность для клиентов через заголовки.

**Минусы:**

- Дополнительная зависимость (Redis).
- Возможны ложные срабатывания при NAT.

## Security impact

- Снижение риска R1 (brute-force атаки на /login).
- Соответствие NFR-01 (защита аутентификации).
- Улучшение общей отказоустойчивости API.

## Rollout plan

1. Добавить middleware для rate limiting с Redis.
2. Настроить конфигурацию лимитов по окружениям.
3. Реализовать тесты в tests/test_rate_limit.py.
4. Мониторинг false positives в течение недели.

## Links

- **NFR:** [NFR-01](https://github.com/hse-secdev-2025-fall/course-project-Gervantinno/pull/4)
- **Threat Model:** Поток [F1 /login] → Риск [R1]
- **Тесты:** `tests/test_rate_limit.py`
- **RISKS.md:** R1 — Brute-force атаки на аутентификацию
  - Критерий закрытия: Успешное прохождение тестов на rate limiting и MFA
