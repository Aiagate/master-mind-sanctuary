# master-mind-sanctuary

## 概要

個人用AIエージェントプロジェクト

## 特徴

### 1. **クリーンアーキテクチャ**

- ユースケース層 (`usecases/`) とドメイン層 (`domain/`) を明確に分離。
- ビジネスロジックとインフラストラクチャの独立性を確保。
- ドメイン層 (`domain/`) とインフラストラクチャ層 (`infrastructure/`) を完全分離。

### 2. **型安全性**

- Pythonの型ヒントを活用し、静的解析ツールによるエラー検出を強化。

### 3. **コード品質管理**

- `Ruff`: 高速なコードフォーマッターとリンター。
- `Pyright`: 厳格な型チェック (strict モード)。
- `pre-commit`: Git コミット前の自動チェック。

## ディレクトリ構成

```text
.
├── app/                           # アプリケーション本体
│   ├── bot/                       # Discord Bot層
│   │   ├── __main__.py            # Botエントリーポイント (start-bot)
│   │   └── cogs/                  # Cogモジュール
│   ├── core/                      # アプリケーションコア (Result, Mediatorなど)
│   ├── container.py               # DIコンテナ設定
│   ├── domain/                    # ドメイン層
│   │   ├── aggregates/            # ドメイン集約 (user.py, team.py)
│   │   ├── interfaces/            # 抽象インターフェース
│   │   ├── repositories/          # リポジトリインターフェース
│   │   └── value_objects/         # 値オブジェクト
│   ├── infrastructure/            # インフラストラクチャ層
│   │   ├── database.py            # DB設定・セッション管理
│   │   ├── orm_models/            # ORMモデル (user_orm.py, team_orm.py)
│   │   └── repositories/          # リポジトリ実装
│   └── usecases/                  # ユースケース層
│       ├── users/                 # ユーザー関連ユースケース
│       └── teams/                 # チーム関連ユースケース
├── alembic/                       # Alembicマイグレーション
│   └── versions/                  # マイグレーションファイル
├── docs/                          # ドキュメント
├── tests/                         # テストコード
├── .pre-commit-config.yaml        # Pre-commit設定
├── pyproject.toml                 # プロジェクト設定
└── README.md                      # このファイル
```

## 必要な環境

- Python 3.13 以上
- パッケージ管理 [uv](https://github.com/astral-sh/uv)
- 必要な依存関係は`pyproject.toml`に記載されています。

## セットアップ

1. 仮想環境を作成:

   ```bash
   uv venv -p 3.13 .venv
   source .venv/bin/activate  # Windows(PS)の場合は .venv\Scripts\activate
   ```

2. 依存関係をインストール:

   ```bash
   uv sync
   ```

3. Pre-commit フックをインストール:

   ```bash
   uv run pre-commit install
   ```

4. 環境変数を設定:

   `.env.example`を`.env`または`.env.local`にコピーして編集:

   ```bash
   # .env.local を作成
   cp .env.example .env.local
   ```

   `.env.local`の内容を編集:

   ```bash
   # Discord Bot Token
   DISCORD_BOT_TOKEN=your_discord_bot_token_here

   # Database URL
   DATABASE_URL=sqlite+aiosqlite:///./bot.db
   ```

5. データベースマイグレーションを実行:

   ```bash
   # マイグレーション適用
   uv run alembic upgrade head

   # マイグレーション状態確認
   uv run alembic current
   ```

6. アプリケーションを起動:

   Discord Botを起動:

   ```bash
   uv run start-bot
   ```

## データベース管理

### マイグレーション操作

```bash
# スキーマ変更後、マイグレーションを自動生成
uv run alembic revision --autogenerate -m "Add new field"

# マイグレーション適用
uv run alembic upgrade head

# 1つ前に戻す
uv run alembic downgrade -1

# 現在のマイグレーション確認
uv run alembic current

# マイグレーション履歴表示
uv run alembic history
```

### データベース構造

- **使用DB**: SQLite (開発時) / PostgreSQL (本番推奨)
- **ORM**: SQLModel
- **マイグレーション**: Alembic
- **非同期対応**: aiosqlite

## テスト実行

```bash
# 全テスト実行
uv run pytest

# カバレッジ付きで実行
uv run pytest --cov=app --cov-report=term-missing

# 特定のテストファイルのみ実行
uv run pytest tests/infrastructure/test_repositories.py

# 詳細な出力
uv run pytest -v
```

## コード品質チェック

```bash
# フォーマット
uv run ruff format .

# リントチェック
uv run ruff check .

# リント自動修正
uv run ruff check . --fix

# 型チェック
uv run pyright
```

## アーキテクチャ

このテンプレートは以下のレイヤーで構成されています：

```text
┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│  Presentation Layer (Discord Bot)   │  │      Presentation Layer (WIP)       │
│           (discord.py)              │  │                                     │
└──────────────────┬──────────────────┘  └──────────────────┬──────────────────┘
                   │                                        │
┌──────────────────▼────────────────────────────────────────▼──────────────────┐
│                        Application Layer (UseCases)                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                         Domain Layer (Aggregates)                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                     Infrastructure Layer (Repository)                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 依存関係の方向

- 上位層から下位層への依存のみ許可
- ドメイン層はインフラストラクチャに依存しない
- リポジトリパターンで永続化を抽象化

## ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で公開されています。
