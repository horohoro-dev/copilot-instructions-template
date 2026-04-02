---
applyTo: "**/*.py"
description: "Python ロギング・構造化ログ・ログ設計"
---

# Python ロギング規約

## 基本ルール

- `logging.getLogger(__name__)` でモジュールごとにロガーを取得する
- `print()` をログ代わりに使わない
- ログメッセージにはコンテキスト情報（ID、件数等）を含める

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_id: str) -> None:
    logger.info("注文処理開始", extra={"order_id": order_id})
    try:
        # 処理...
        logger.info("注文処理完了", extra={"order_id": order_id, "items": count})
    except PaymentError as e:
        logger.error("決済失敗", extra={"order_id": order_id, "error": str(e)})
        raise
```

## ログレベルの使い分け

| レベル | 用途 | 例 |
|--------|------|-----|
| `DEBUG` | 開発時の詳細情報 | SQL クエリ、変数値 |
| `INFO` | 正常な動作の記録 | リクエスト処理開始/完了 |
| `WARNING` | 潜在的な問題 | 非推奨 API 使用、リトライ発生 |
| `ERROR` | 処理の失敗 | API 呼び出し失敗、バリデーションエラー |
| `CRITICAL` | システム停止レベルの障害 | DB 接続不可、設定ファイル欠損 |

## 構造化ログ（本番推奨）

```python
# structlog を使用した構造化ログ
import structlog

logger = structlog.get_logger()

logger.info("ユーザー作成", user_id=user.id, email=user.email)
# 出力: {"event": "ユーザー作成", "user_id": 123, "email": "..."}
```

### structlog 設定例

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| `print()` でログ出力 | `logger.info()` 等を使用 |
| f-string でログメッセージ構築 | `extra={}` または structlog のキーワード引数 |
| 例外を握りつぶしてログのみ | `raise` で再送出、または明示的なリカバリ |
| ルートロガーへの直接設定 | `logging.config.dictConfig()` で一括設定 |
| ログにパスワード・トークン出力 | 機密情報はマスク or 除外 |
| 全レベルを `INFO` で出力 | レベルを適切に使い分ける |

## リクエストトレーシング

```python
import structlog
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# ミドルウェアで request_id をバインド
structlog.contextvars.bind_contextvars(request_id=request_id)
# 以降のすべてのログに request_id が自動付与される
```
