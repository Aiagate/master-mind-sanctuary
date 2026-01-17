---
trigger: glob
globs: app/domain/value_object/**/*.py
---

## Value Objects (`app/domain/value_objects`)

Value Objects represent descriptive aspects of the domain with no conceptual identity.

- **Base Class**: Use `app.domain.value_objects.base_id.BaseId` for identifiers.
- **Immutability**: MUST use `@dataclass(frozen=True)`.
- **Methods**:
  - `to_primitive() -> T`: Serialize to a primitive type (int, str, etc.).
  - `from_primitive(value: T) -> Result[VO, Exception]`: Factory method to create from a primitive.
  - `create(...) -> Result[VO, Exception]` or `__init__`: For creation with validation.
- **Validation**: Enforce constraints (length, format) during creation. Return `Err` on failure.

**Example (Identifier):**

```python
@dataclass(frozen=True)
class UserId(BaseId):
    """User Identifier Value Object."""
    pass
```
