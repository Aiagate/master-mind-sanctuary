# 開発レシピ集 (Development Recipes)

このドキュメントでは、開発時によく発生するタスクの手順を「レシピ」としてまとめます。

## レシピ1: 新しいチャットコマンドを追加する

Discordで新しいコマンド（例: `!chat analyze <text>`）を追加し、独自のロジックで処理させる場合の手順です。

### 手順
1.  **UseCaseの作成**:
    -   `app/usecases/chat/` 配下に新しいファイルを作成（例: `analyze_text.py`）。
    -   `Request` (Query/Command) クラスと `RequestHandler` クラスを定義。
    -   必要なドメインロジックやAI呼び出しを実装。
2.  **DIコンテナへの登録**:
    -   `app/container.py` を開き、作成した `RequestHandler` を `Injector` にバインド（通常は自動解決されるが、明示的なバインドが必要な場合を確認）。
3.  **Botコマンドの追加**:
    -   `app/bot/cogs/chat_cog.py` を開く。
    -   `@chat.command` デコレータを使って新しいメソッドを追加。
    -   `Mediator.send_async(NewQuery(...))` を呼び出して実装したUseCaseを実行。
    -   結果を `ctx.send()` で返信。

## レシピ2: データベースに新しいテーブルを追加する

新しいデータを永続化するためのテーブル（例: `UserProfile`）を追加する手順です。

### 手順
1.  **ドメインエンティティの作成**:
    -   `app/domain/aggregates/` にファイルを作成（例: `user_profile.py`）。
    -   純粋なPythonクラス（データクラス）としてエンティティを定義。識別子、属性、振る舞いを持たせる。
2.  **ORMモデルの作成**:
    -   `app/infrastructure/orm_models/` にファイルを作成（例: `user_profile_orm.py`）。
    -   `SQLModel` を継承し、テーブル定義（カラム、型）を記述。`table=True` を設定。
3.  **マッピングの定義**:
    -   `app/infrastructure/orm_mapping.py` を開く。
    -   `registry.map()` を使用して、ドメインエンティティとORMモデルの相互変換ルールを登録。
4.  **マイグレーションの作成と適用**:
    -   コマンドを実行してマイグレーションファイルを生成:
        ```bash
        uv run alembic revision --autogenerate -m "add user_profile table"
        ```
    -   生成されたファイル (`alembic/versions/`) を確認。
    -   DBに適用:
        ```bash
        uv run alembic upgrade head
        ```

## レシピ3: 新しいAIプロバイダーを追加する

Gemini, GPTに加えて、新しいAIサービス（例: Claude）を追加する手順です。

### 手順
1.  **Value Objectの更新**:
    -   `app/domain/value_objects/ai_provider.py` の `AIProvider` Enumに新しい値を追加。
2.  **サービスの実装**:
    -   `app/infrastructure/services/` にファイルを作成（例: `claude_service.py`）。
    -   `app/domain/interfaces/ai_service.py` の `IAIService` インターフェースを実装するクラスを作成。
3.  **環境変数の追加**:
    -   `.env` と `.env.example` にAPIキーなどの設定を追加。
    -   `app/core/config.py` の `Settings` クラスにフィールドを追加。
4.  **DI設定の更新**:
    -   `app/container.py` で、条件に応じて新しいサービスクラスを注入するように設定を変更（またはファクトリパターンを使用）。
