```mermaid
flowchart LR
  A[External App] -->|F1: HTTPS (login)| GW[API Gateway]
  A -->|F2: Поиск рецептов| GW
  A -->|F3: Работа с ингредиентами| GW
  subgraph Edge[Trust Boundary: Edge]
    GW -->|F2: Поиск рецептов| SVC[Recipe Service]
    GW -->|F3: Ингредиенты| ING[Ingredient Service]
  end
  subgraph Core[Trust Boundary: Core]
    SVC --> DB[(Recipe Database)]
    ING --> DB
  end
  style GW stroke-width:2px
```
