# イベント駆動アーキテクチャのイベント・サブスクライバー対応表

## 概要

本プロジェクトでは、`RedisEventBus`（または `PostgresEventBus`）を介したパブリッシュ/サブスクライブモデルを採用しています。
思考ロジック（重い処理）を **Worker プロセス** に、UIおよびAPI連携（軽い処理）を **Bot プロセス** に明確に分離し、高い応答性と拡張性を確保しています。

## 1. イベント対応表（最新設計）

| イベント名 (Topic) | 発行元 (Publisher) | 購読者 (Subscriber) | 処理内容の概要 |
| :--- | :--- | :--- | :--- |
| `system.heartbeat` | `heartbeat_producer`<br>(Worker) | `HeartbeatHandler`<br>(Worker) | 毎分発行されるシステム生存確認。一定の確率でAIの自発的な発言をトリガーします。 |
| `discord.message` | `PublishReceivedMessageHandler`<br>(UseCase / Bot) | `DiscordMessageHandler`<br>(Worker) | Discordメッセージ受信時に発行。**Worker側でAI回答を生成**します。 |
| `discord.direct_message` | `PublishReceivedDirectMessageHandler`<br>(UseCase / Bot) | `DirectMessageResponseCog`<br>(Bot) | DM受信時に発行。現在は固定定型文で応答します。 |
| `bot.speak` | `HandleDiscordMessageHandler`<br>`HandleHeartbeatHandler`<br>(Worker) | `BrainCog`<br>(Bot) | Workerで思考が完了した内容を、BotがDiscordの指定チャンネルへ送信します。 |
| `sns.update` | （外部コンポーネント） | `BrainCog`<br>(Bot) | 外部SNS更新を検知し、Bot経由でDiscordへ通知します。 |

---

## 2. コンポーネント別の役割

### Bot プロセス (`app/bot`)

UI（送信・受信）に特化した軽量なレイヤーです。

- **`BrainCog`**: `bot.speak`（発言依頼）の最終的な送信処理を担当。
- **`ChatCog`**: 将来的なチャットUX（タイピング表示等）のために予約されています。
- **`PublishReceivedMessageHandler`**: 受信した情報をDBに保存し、思考プロセスを開始させるために `discord.message` を発行します。

### Worker プロセス (`app/worker`)

「思考（AI生成）」を担当する高負荷対応レイヤーです。

- **`DiscordMessageHandler`**: `discord.message` を購読し、履歴を含めたAI回答生成を実行。完了後に `bot.speak` を発行します。
- **`HeartbeatHandler`**: 定期的な生存確認をトリガーに、自発的な発言が必要か判断（AI生成）します。

---

## 3. リファクタリングによるメリット

1. **Botプロセスの応答性向上**: 重いAI生成処理が Bot プロセスから完全に排除されたため、メッセージの大量流入時でもコマンド反応などが遅延しません。
2. **設計の一貫性**: すべての「発言」は `bot.speak` イベントという単一の窓口を通じて Bot プロセスに集約されるようになりました。
3. **スケーラビリティ**: AI生成がボトルネックになった場合、Worker プロセスのみをスケールアウトすることが可能です。
