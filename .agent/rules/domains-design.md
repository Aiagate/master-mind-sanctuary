---
trigger: glob
globs: app/domain/aggregates/**/*.py
---

## Aggregates & Entities (`app/domain/aggregates`)

Aggregates are clusters of domain objects that can be treated as a single unit. Use them to enforce **invariants**.

* **Data Structure**: Use `@dataclass`.
* **Identity**: Must have a unique identifier (Value Object).
* **Encapsulation**:
* Use **private fields** (e.g., `_content`) for internal state.
* Expose state via **properties** (read-only) or methods (mutators).

* **Construction & Factory Methods**:
* **Domain-Specific Naming**: Avoid generic names like `create()`. Use naming that reflects the ubiquitous language and business intent (e.g., `join()`, `post()`, `assign()`).
* **Internal Init**: Use `__init__` primarily for **reconstitution** (rebuilding objects from storage).
* **Factory Methods**: Provide specialized `@classmethod` factory methods for creating new instances (generating IDs, setting initial business state).

* **Business Logic**: Methods should implement business rules and return a `Result` type.

### Example

```python
@dataclass
class TeamAssignment:
    _id: AssignmentId
    _team_id: TeamId
    _member_id: MemberId

    @property
    def id(self) -> AssignmentId:
        return self._id

    @classmethod
    def join(cls, team_id: TeamId, member_id: MemberId) -> TeamAssignment:
        """
        Creates a new assignment.
        Named 'join' to reflect the actual domain action instead of generic 'create'.
        """
        return cls(
            _id=AssignmentId.generate().unwrap(),
            _team_id=team_id,
            _member_id=member_id
        )

```

---

### Key Improvements

* **Ubiquitous Language**: By using `TeamAssignment.join()`, the code describes the business process itself, making it more readable for both developers and domain experts.
* **Intent-Revealing Interface**: The factory method name clarifies *why* the object is being created, which is a core principle in DDD.
