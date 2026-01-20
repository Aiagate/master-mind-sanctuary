---
trigger: glob
globs: tests/**/*.py
---

# Test Implementation Guide

このプロジェクトにおけるテストコードの実装方針とベストプラクティスを提供します。

## 1. 概要

本プロジェクトのテストは `pytest` をベースにしており、クリーンアーキテクチャの各レイヤー（Domain, UseCases, Infrastructure）の責務に応じた検証を行います。

## 2. 技術スタックとツール

- **フレームワーク**: `pytest`
- **非同期処理**: `pytest-asyncio`
- **モッキング**: `pytest-mock`
- **データベース**: `sqlite+aiosqlite` (インメモリ)
- **アサーション**: 標準の `assert` 文

## 3. 実装ルール

### 3.1 非同期テスト

非同期関数（`async def`）のテストには、必ず `@pytest.mark.asyncio` デコレータを使用してください。`anyio` マーカーは非推奨です。

**Good:**

```python
import pytest

@pytest.mark.asyncio
async def test_something_async():
    result = await some_async_function()
    assert result == "expected"
```

**Bad:**

```python
# 古い形式やライブラリ依存
@pytest.mark.anyio  # 使用しない
async def test_something():
    ...
```

### 3.2 モック (Mocking)

`unittest.mock` を直接インポートせず、`pytest-mock` が提供する `mocker` フィクスチャを使用してください。これにより、テスト後のクリーンアップが自動化され、`pytest` スタイルの記述が可能になります。

**Good:**

```python
from typing import Any
import pytest

# mockerフィクスチャを受け取る
def test_service_call(mocker: Any):
    # patchの使用
    mock_func = mocker.patch("app.path.to.module.function")
    mock_func.return_value = "mocked"

    # Mockオブジェクトの作成
    mock_obj = mocker.MagicMock()
    mock_async_obj = mocker.AsyncMock()

    ...
```

**Bad:**

```python
from unittest.mock import patch, MagicMock  # 直接インポートしない

@patch("...")
def test_something(mock_obj):
    ...
```

### 3.3 データベーステスト

インフラストラクチャ層やユースケース層でデータベースへのアクセスが必要な場合は、`tests/conftest.py` で定義されている `uow` (Unit of Work) フィクスチャを使用してください。これにより、インメモリのSQLiteデータベースに対してテストが実行され、テストごとにロールバックされるため、副作用がありません。

```python
import pytest
from app.domain.repositories import IUnitOfWork
from app.infrastructure.orm_models import SomeModel

@pytest.mark.asyncio
async def test_repository_save(uow: IUnitOfWork):
    async with uow:
        repo = uow.GetRepository(SomeModel)
        await repo.add(entity)
        await uow.commit()

    # 検証コード...
```

## 4. レイヤー別の方針

### 4.1 Domain層 (`tests/domain`)

- **外部依存なし**: DBやAPIへの依存を持たせず、純粋なPythonオブジェクトとしてテストします。
- **バリデーション**: エンティティやValue Objectの生成時のルール、ビジネスロジックの振る舞いを検証します。

### 4.2 UseCases層 (`tests/usecases`)

- **ロジックの流れ**: 入力（Command/Query）に対して、期待される出力（Result）が得られるかをテストします。
- **依存のモック**: RepositoryやExternal Serviceは `mocker` を使用してモック化し、実際の外部アクセスを行わないようにします。
- **Result型の検証**: 戻り値が `Ok` か `Err` か、エラー型が適切かを検証します。

### 4.3 Infrastructure層 (`tests/infrastructure`)

- **Repository**: インメモリDBを使用して、実際にデータの保存・取得・削除ができるか検証します。
- **External Services**: 外部APIクライアント（OpenAI, Geminiなど）はモック化し、リクエストの形式やレスポンスのハンドリングをテストします。

## 5. 禁止事項

1. **`unittest.mock` の直接使用**: `pytest-mock` に統一するため、`from unittest import mock` や `unittest.mock.patch` は使用しないでください。
2. **`@pytest.mark.anyio` の使用**: プロジェクト設定との整合性のため、`@pytest.mark.asyncio` を使用してください。
3. **テスト間の依存**: 各テストは独立して実行可能である必要があります。DBの状態などは `fixture` を活用して初期化してください。
