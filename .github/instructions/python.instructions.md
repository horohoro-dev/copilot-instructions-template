---
applyTo: "**/*.py"
description: "Python コード構成・命名・型・リソース管理"
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

## リソース管理
- `with` 文でファイル、DB接続、ロック等のリソースを管理する
- 複数リソースや動的リソースには `ExitStack` を使用する

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in file_paths]
```
