---
trigger: glob
globs: app/usecases/**/*.py
---

# UseCase Design Skill

アプリケーションのビジネスロジック（ユースケース）を実装する際の設計指針です。
CQRS (Command Query Responsibility Segregation) と Mediator パターンを採用し、各ユースケースを独立したハンドラとして実装します。

## 設計原則

1. **Mediator パターンの適用**:
    * 全てのユースケースは `Request` (Command/Query) と `RequestHandler` のペアで実装します。
    * `injector` を使用して依存関係（Repository, Service, EventBusなど）を注入します。

2. **Result 型の統一とオブジェクト化**:
    * 戻り値は必ず `Result[T, E]` 型を使用します。
    * **重要**: 成功時の型 `T` は、**必ず専用のデータクラス（DTO）**として定義します。
        * たとえ戻り値が単一の値（IDや文字列など）や `None` であっても、直接プリミティブ型や `None` を返さず、フィールドを持ったデータクラスでラップしてください。
        * **理由**: 将来的に戻り値に情報（メタデータ、ステータス、追加のIDなど）を追加する必要が生じた際、Resultクラスにフィールドを追加するだけで済み、呼び出し元の型定義そのものを破壊的に変更せずに済むためです（Open-Closed Principle）。

3. **エラーハンドリング**:
    * ビジネスロジック上のエラーには例外 (`raise`) を使用せず、`Err(UseCaseError(...))` を返却します。
    * `UseCaseError` には `ErrorType` (Enum) と具体的なメッセージを含めます。

4. **トランザクション管理**:
    * `IUnitOfWork` を使用して、ハンドラの `handle` メソッド内でトランザクション境界を明示的に管理します（`async with self._uow:`）。

## 実装テンプレート

1ファイルに `Result`, `Command/Query`, `Handler` をまとめて定義することを推奨します（凝集度を高めるため）。

```python
from dataclasses import dataclass
from injector import inject
from app.core.mediator import Request, RequestHandler
from app.core.result import Ok, Err, Result
from app.usecases.result import UseCaseError, ErrorType
from app.domain.repositories.interfaces import IUnitOfWork

# 1. Result Object (DTO)
# 戻り値が空(None)の場合でも、拡張性のために空のDataclassを定義することを推奨します。
@dataclass(frozen=True)
class DoSomethingResult:
    """Result data for DoSomething command."""
    resource_id: str
    # 将来的に processed_at: datetime などを追加しても、
    # 呼び出し元で resource_id にアクセスしているコードは壊れない。

# 2. Request (Command or Query)
# Request[Result[<ResultClass>, UseCaseError]] を継承
@dataclass(frozen=True)
class DoSomethingCommand(Request[Result[DoSomethingResult, UseCaseError]]):
    """Command to do something."""
    input_param: str
    target_id: int

# 3. Handler
class DoSomethingHandler(
    RequestHandler[DoSomethingCommand, Result[DoSomethingResult, UseCaseError]]
):
    """Handler for DoSomethingCommand."""

    @inject
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, request: DoSomethingCommand
    ) -> Result[DoSomethingResult, UseCaseError]:
        # 1. 入力値検証 (簡易的なものはここで、ドメインルールはドメイン層で)
        if not request.input_param:
             return Err(UseCaseError(ErrorType.VALIDATION_ERROR, "Input param is required"))

        async with self._uow:
            # 2. リポジトリの取得とドメインロジックの実行
            # repo = self._uow.GetRepository(SomeAggregate)
            # ...

            # 3. 永続化
            # await repo.save(entity)
            await self._uow.commit()

        # 4. 結果の返却
        return Ok(DoSomethingResult(
            resource_id="generated_id"
        ))
```

## ディレクトリ構造

`app/usecases/{domain_area}/{action_name}.py` の形式で配置します。

例:

* `app/usecases/chat/generate_content.py`
* `app/usecases/messaging/process_sns_update.py`
