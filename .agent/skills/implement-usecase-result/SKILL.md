---
name: implement-usecase-result
description: Guide for returning Result types and handling errors in UseCases.
---

# Implement UseCase Result

このスキルは、Use Case層での戻り値として `Result` 型を使用し、エラーハンドリングを統一するためのガイドラインです。

## 概要

すべてのUse Caseの `execute` メソッド（またはそれに準ずるメインメソッド）は、`app.core.result.Result` 型を返す必要があります。
成功時は `Ok`、失敗時は `Err` を返し、エラー内容は `app.usecases.result.UseCaseError` でラップします。

## 必要なインポート

```python
from app.core.result import Result, Ok, Err
from app.usecases.result import UseCaseError, ErrorType
```

## 実装ルール

1. **戻り値の型ヒント**: `Result[SuccessType, UseCaseError]` とします。
2. **成功時**: `return Ok(value)` を返します。
3. **失敗時**: `return Err(UseCaseError(type=ErrorType.TYPE, message="メッセージ"))` を返します。
    * 生じた例外をそのまま `Err(e)` で返さないでください。必ず `UseCaseError` に変換します。

## ErrorType の選び方

| ErrorType | 用途 |
| :--- | :--- |
| `NOT_FOUND` | リソースが見つからない場合 (404相当) |
| `VALIDATION_ERROR` | 入力値が不正な場合、ビジネスルール違反 (400相当) |
| `UNEXPECTED` | 想定外のエラー、システムエラー (500相当) |
| `CONCURRENCY_CONFLICT` | 排他制御エラー、楽観的ロックの衝突 (409相当) |

## 実装例

```python
from dataclasses import dataclass
from app.core.result import Result, Ok, Err
from app.usecases.result import UseCaseError, ErrorType

@dataclass
class MyUseCaseInput:
    id: str
    amount: int

class MyUseCase:
    def execute(self, input: MyUseCaseInput) -> Result[str, UseCaseError]:
        # バリデーション例
        if input.amount < 0:
            return Err(UseCaseError(
                type=ErrorType.VALIDATION_ERROR,
                message="Amount must be positive"
            ))

        try:
            # 処理ロジック (例)
            result_value = f"Processed {input.id} with {input.amount}"

            # リソースがない場合の例
            if not result_value:
                 return Err(UseCaseError(
                    type=ErrorType.NOT_FOUND,
                    message=f"Resource {input.id} not found"
                ))

            return Ok(result_value)

        except Exception as e:
            # 予期せぬエラーの捕捉
            return Err(UseCaseError(
                type=ErrorType.UNEXPECTED,
                message=f"Unexpected error: {str(e)}"
            ))
```
