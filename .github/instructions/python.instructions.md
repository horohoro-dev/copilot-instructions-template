---
applyTo: "**/*.py"
description: "Python コーディング規約とベストプラクティス"
---

# Python コーディング規約

## コード構成
- 1ファイル1概念を原則とし、300〜500行を超えたら分割を検討する
- `__all__` で公開インターフェースを明示する
- 絶対インポートを使用する（相対インポートは避ける）

```python
# Good
__all__ = ["UserService", "UserRepository"]

from myproject.domain.models import User
```

## 命名規約
| 対象 | スタイル | 例 |
|------|---------|-----|
| ファイル / モジュール | snake_case | `user_service.py` |
| クラス | PascalCase | `UserService` |
| 関数 / 変数 | snake_case | `get_active_users` |
| 定数 | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |

## 型安全性
- すべての公開関数に型ヒントを付与する
- `T | None` 構文を使用する（`Optional[T]` は使わない）
- `Protocol` でインターフェースを定義する
- ジェネリクスで型情報を保持する
- 型エイリアスで複雑な型に意味のある名前をつける
- `Callable` 型でコールバックの型を明示する

```python
from typing import Protocol
from collections.abc import Callable

class Repository(Protocol[T]):
    def get(self, id: int) -> T | None: ...
    def save(self, entity: T) -> T: ...

# 型エイリアス（Python 3.12+）
type UserId = str
type Handler[T] = Callable[[Request], T]

# コールバック型の定義
ProgressCallback = Callable[[int, int], None]  # (current, total)
```

### ドメイン型への早期変換

外部入力（文字列、dict 等）はシステム境界で直ちにドメイン型に変換する。内部コードは常に型付きオブジェクトを扱う。

```python
from enum import Enum

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"

def parse_output_format(value: str) -> OutputFormat:
    """文字列をドメイン型に変換する。"""
    try:
        return OutputFormat(value.lower())
    except ValueError:
        valid = [f.value for f in OutputFormat]
        raise ValueError(
            f"無効なフォーマット '{value}'。有効な値: {', '.join(valid)}"
        )

# API 境界で変換し、以降は型安全に処理
def export_data(data: list[dict], format_str: str) -> bytes:
    output_format = parse_output_format(format_str)  # ここで変換
    ...
```

## pandas ベストプラクティス
- ベクトル化演算を優先する
- `iterrows()` 禁止 → `apply()` またはベクトル化演算を使用する
- 組み込みメソッド（`sum()`, `mean()`, `groupby()` 等）を活用する
- 大規模データはチャンク読み込みを検討する
- 適切な `dtype` を指定してメモリ効率を確保する

```python
# Bad: iterrows()
for _, row in df.iterrows():
    row["total"] = row["price"] * row["quantity"]

# Good: ベクトル化演算
df["total"] = df["price"] * df["quantity"]
```

## リソース管理
- `with` 文でファイル、DB接続、ロック等のリソースを管理する
- 複数リソースや動的リソースには `ExitStack` を使用する

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in file_paths]
```

## テスト
- pytest を使用する
- AAA パターン（Arrange → Act → Assert）に従う
- `@pytest.mark.parametrize` でパラメータ化テストを記述する
- フィクスチャでセットアップを再利用する
- テスト命名: `test_<対象>_<条件>_<期待結果>`

```python
@pytest.mark.parametrize("age,expected", [
    (17, False),
    (18, True),
    (65, True),
])
def test_is_adult_年齢に応じて正しい結果を返す(age: int, expected: bool) -> None:
    # Arrange
    user = User(age=age)

    # Act
    result = user.is_adult()

    # Assert
    assert result == expected
```

## パフォーマンス

**原則: 計測してから最適化する。** プロファイリングなしに最適化を行わない。`cProfile`、`line_profiler`、`memory_profiler` 等で実際のボトルネックを特定してから改善する。

- リスト内包表記 > `for` ループ
- ジェネレータでメモリ効率を改善する
- 文字列結合には `str.join()` を使用する
- 辞書ルックアップ O(1) > リスト検索 O(n)

```python
# Bad
result = ""
for item in items:
    result += str(item)

# Good
result = "".join(str(item) for item in items)
```

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

## アンチパターン（禁止事項）
- ベアな `except Exception: pass`
- I/O とビジネスロジックの混在
- ORM モデルの直接公開（API レスポンスにそのまま返さない）
- ハードコードされた設定値（環境変数や設定ファイルを使う）
- 5階層以上のネスト（早期リターンやガード句で解消する）
