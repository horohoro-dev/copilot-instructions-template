---
applyTo: "**/*.py"
description: "Python 非同期パターン・例外設計・バッチ処理"
---

# Python 非同期・例外・バッチ処理

## 非同期パターン
- I/O バウンドの並行処理で `async/await` を使用する
- `asyncio.gather()` で複数タスクを並列実行する
- `asyncio.Semaphore` でレート制限を実装する
- async コード内で同期ブロッキング呼び出しを行わない

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    semaphore = asyncio.Semaphore(10)

    async def fetch_with_limit(url: str) -> Response:
        async with semaphore:
            return await client.get(url)

    return await asyncio.gather(*[fetch_with_limit(u) for u in urls])
```

## カスタム例外の設計

アプリケーション固有の例外はベースクラスから階層的に定義し、構造化された情報を持たせる。

```python
class AppError(Exception):
    """アプリケーション例外の基底クラス。"""
    pass

class ApiError(AppError):
    """外部 API 呼び出しの失敗。"""
    def __init__(self, message: str, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(message)

class RateLimitError(ApiError):
    """レートリミット超過。"""
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"レートリミット超過。{retry_after}秒後にリトライ",
            status_code=429,
        )
```

## バッチ処理の部分失敗

バッチ処理では1件の失敗で全体を中断しない。成功と失敗を個別に追跡する。

```python
from dataclasses import dataclass

@dataclass
class BatchResult[T]:
    """バッチ処理の結果。"""
    succeeded: dict[int, T]
    failed: dict[int, Exception]

    @property
    def all_succeeded(self) -> bool:
        return len(self.failed) == 0

def process_batch(items: list[Item]) -> BatchResult[ProcessedItem]:
    succeeded: dict[int, ProcessedItem] = {}
    failed: dict[int, Exception] = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process_single(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded=succeeded, failed=failed)
```
