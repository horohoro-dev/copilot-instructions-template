---
applyTo: "**/tasks.py,**/celery.py,**/celeryconfig.py"
description: "Django Celery タスク設計・リトライ・冪等性"
---

# Django Celery 規約

## タスク設計の基本原則

- タスクは必ず**冪等**にする（同じ引数で何度実行しても同じ結果）
- タスク引数はシリアライズ可能な型のみ（`str`, `int`, `dict` 等。ORM モデルは渡さない）
- 1タスク1責任。複雑な処理はタスクチェーンで構成する

```python
from celery import shared_task

# Good: ID を渡して冪等に処理
@shared_task(bind=True, max_retries=3)
def send_notification(self, user_id: int, message: str) -> None:
    try:
        user = User.objects.get(id=user_id)
        notify(user, message)
    except User.DoesNotExist:
        return  # リトライ不要
    except ExternalServiceError as e:
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

# Bad: ORM モデルを直接渡す
@shared_task
def send_notification(user: User, message: str) -> None:  # シリアライズ不可
    ...
```

## リトライ戦略

```python
@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,        # 初回 60秒後
    retry_backoff=True,             # 指数バックオフ
    retry_backoff_max=600,          # 最大 10分
    retry_jitter=True,              # ジッター追加（サンダリングハード防止）
    autoretry_for=(ConnectionError, TimeoutError),
)
def call_external_api(self, endpoint: str) -> dict:
    return httpx.get(endpoint, timeout=30).json()
```

## タスクの冪等性パターン

```python
@shared_task
def process_payment(order_id: int) -> None:
    order = Order.objects.select_for_update().get(id=order_id)
    if order.payment_status == "completed":
        return  # 既に処理済み（冪等性ガード）
    charge_payment(order)
    order.payment_status = "completed"
    order.save(update_fields=["payment_status"])
```

## Beat スケジュール

```python
# celery.py
app.conf.beat_schedule = {
    "cleanup-expired-sessions": {
        "task": "accounts.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=3, minute=0),  # 毎日 3:00
    },
    "send-daily-report": {
        "task": "reports.tasks.send_daily_report",
        "schedule": crontab(hour=9, minute=0, day_of_week="mon-fri"),
    },
}
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| ORM モデルをタスク引数に渡す | ID を渡してタスク内で取得 |
| 冪等性ガードなし | 処理前に状態を確認 |
| 無限リトライ | `max_retries` を設定 |
| タスク内で長いトランザクション | `select_for_update()` で最小限のロック |
| `delay()` を DB トランザクション内で呼ぶ | `transaction.on_commit()` で呼ぶ |

```python
# Good: トランザクション完了後にタスクを発行
from django.db import transaction

with transaction.atomic():
    order = Order.objects.create(**data)
    transaction.on_commit(lambda: send_confirmation.delay(order.id))
```
