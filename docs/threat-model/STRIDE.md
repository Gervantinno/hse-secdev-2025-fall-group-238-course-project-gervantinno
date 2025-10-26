| Поток/Элемент      | Угроза (STRIDE) | Риск | Контроль                       | Ссылка на NFR  | Проверка/Артефакт  |
| ------------------ | --------------- | ---- | ------------------------------ | -------------- | ------------------ |
| F1 /login          | S: Spoofing     | R1   | MFA + rate-limit на /login     | NFR-01, NFR-04 | e2e + ZAP baseline |
| F2 /recipes/search | I: Information  | R2   | Маскирование ошибок, RFC7807   | NFR-02         | контрактные тесты  |
| F3 /ingredients    | T: Tampering    | R3   | RBAC, валидация входных данных | NFR-01         | unit + e2e тесты   |
