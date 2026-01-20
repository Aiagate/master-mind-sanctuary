# Gemini Context: master-mind-sanctuary (Japanese Summary)

- **言語設定**: すべての思考、コメント、チャット応答、およびTask UI（TaskName, TaskStatus, TaskSummary）は日本語で行うこと。
- **アーティファクト**: 生成するドキュメント（task.md, walkthrough.md, implementation_plan.mdなど）の本文はすべて日本語で記述すること。ただし、ファイル名やコードブロック内の変数名などは英語のままでよい。

## プロジェクト概要

これは、AIエージェント（Discordボット）開発プロジェクトです。開発を始めるための最小限の情報を以下に示します。

### WHAT（何か）

- **プロダクト**: Python製のDiscordボット。Google GeminiやOpenAI GPTと連携して対話やタスク実行を行います。
- **アーキテクチャ**: クリーンアーキテクチャを採用し、ドメインロジック、アプリケーション制御、インフラ、UIを明確に分離しています。また、非同期処理のためにイベント駆動アーキテクチャを取り入れています。
- **コードベースの構造**:
  - `app/domain`: **[ドメイン層]** ビジネスルール、エンティティ、値オブジェクト。詳細は [ドメイン用語集](docs/domain_glossary.md) を参照。
  - `app/usecases`: **[アプリケーション層]** ユースケース。詳細は [アーキテクチャとデータフロー](docs/architecture_data_flow.md) を参照。
  - `app/infrastructure`: **[インフラ層]** DB、外部API連携。実装手順は [開発レシピ集](docs/development_recipes.md) を参照。
  - `app/bot`: **[プレゼンテーション層]** Discord APIインターフェース。
  - `app/worker`: **[ワーカー]** バックグラウンドタスク処理。
  - `app/core`: Mediator、共通設定などの基盤機能。
- **技術スタック**:
  - Python 3.13
  - discord.py
  - SQLModel (SQLite)
  - Alembic
  - pytest
  - Ruff
  - Pyright
  - uv

### WHY（なぜか）

- **AIモデルの進化への適応**: LLMの進化に合わせ、ビジネスロジックに影響を与えずにプロバイダーを交換可能にするため。
- **プラットフォーム非依存性**: Discord以外のUI展開を見据え、ロジックとインターフェースを分離するため。
- **複雑性の管理**: DDDを用い、AIの人格や文脈管理などの複雑なルールをドメインオブジェクトに集約するため。
- **応答性の確保**: イベント駆動により重いAI生成処理を非同期化し、快適なUXを提供するため。

### HOW（どうやって）

詳細な手順は [開発レシピ集](docs/development_recipes.md) を参照してください。

1. **環境セットアップ**: `uv sync` を実行し、`.env` を設定。
2. **データベース管理**: `uv run alembic upgrade head` でマイグレーション適用。
3. **品質管理**: `uv run pytest`, `uv run pyright`, `uv run ruff check . --fix` を実行。
4. **起動**: ボットは `uv run python -m app.bot`、ワーカーは `uv run python -m app.worker`。

---

### ベストプラクティス

- **規約**: 既存のコードスタイルとアーキテクチャに従ってください。
- **ドキュメントの活用**: 実装に迷った際は `docs/` 配下の詳細ドキュメントを参照してください。
- **検証**: 変更後は必ずテストと型チェックを実行してください。手順: code-lint (Skills)
