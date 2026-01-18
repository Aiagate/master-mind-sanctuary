---
trigger: glob
globs: app/domain/**/*.py
---

# Domain Layer Implementation Rules

This document outlines the implementation rules and conventions for the Domain layer (`app/domain key`) of the `discord-bot-template` project.
These rules enforce Clean Architecture principles, ensuring the domain layer remains independent, testable, and maintainable.

## 1. General Principles

- **Independence**: The Domain layer must **not** depend on any other layer (Application, Infrastructure, Presentation).
  - Forbidden imports: `app.usecases`, `app.infrastructure`, `app.bot`, `discord`, `sqlalchemy`, `sqlmodel`.
  - Allowed imports: Standard library, `app.core` (Result, basics), `typing`, `dataclasses`.
- **Pure Python**: Use plain Python objects (POPOs) and standard typing.
- **Error Handling**: Use the **Result Pattern** (`app.core.result.Result`) for all operations that can fail. Do not raise exceptions for business logic errors.

## 2. Directory Structure

```text
app/domain/
├── aggregates/       # Domain Entities and Aggregates
├── value_objects/    # Immutable Domain Value Objects
├── repositories/     # Repository Interfaces
└── interfaces/       # Other Domain Interfaces (e.g., Domain Services)
```
