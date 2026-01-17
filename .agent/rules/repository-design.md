---
trigger: glob
globs: app/domain/repositories/**/*.py
---

## Repositories (`app/domain/repositories`)

Repositories mediate between the domain and data mapping layers. The Domain layer defines **interfaces** only.

- **Location**: `app/domain/repositories/interfaces.py` and `app/domain/repositories/{entity}_repository.py`.
- **Inheritance**: Inherit from `IRepository[T]` or `IRepositoryWithId[T, K]`.
- **Async**: All repository methods must be `async`.
- **Return Types**: Must return `Result[T, RepositoryError]`.
  - Use `RepositoryError` with appropriate `RepositoryErrorType` (NOT_FOUND, ALREADY_EXISTS).
- **No ORM Models**: Methods must accept and return **Domain Entities**, never ORM models/Schemas.

## Unit of Work (`app/domain/repositories/interfaces.py`)

- **Interface**: `IUnitOfWork` defines strict atomic operations.
- **GetRepository**: Use `@overload` to provide type-safe access to specific repositories.
