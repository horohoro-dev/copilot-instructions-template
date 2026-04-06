---
globs: "**/*.py"
description: "Python セキュリティ・脆弱性防止・依存関係監査"
---

# Python セキュリティ規約

## 入力バリデーション（最重要）

- 外部入力（API リクエスト、ファイル、環境変数）は必ずバリデーションする
- バリデーションはシステム境界（API エンドポイント等）で即座に行う
- 内部コードでは型付きオブジェクトのみを扱う

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserInput(BaseModel):
    email: str = Field(max_length=255)
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("無効なメールアドレス")
        return v.lower()
```

## SQL インジェクション防止

```python
# 禁止: 文字列結合による SQL 構築
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# 必須: パラメータ化クエリ
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ORM を使用する場合は自動的にパラメータ化される
User.objects.filter(id=user_id)
```

## シークレット管理

| 禁止 | 対策 |
|------|------|
| コード内にパスワード・トークン・API キーを記述 | 環境変数で管理 |
| `.env` を Git にコミット | `.gitignore` に追加 |
| ログにシークレットを出力 | `SecretStr` 型を使用 |
| URL にトークンを含める | ヘッダーで送信 |

## 依存関係のセキュリティ

```bash
# 脆弱性スキャン
pip-audit

# シークレット混入検出
detect-secrets scan

# Dependabot で自動アップデート（.github/dependabot.yml）
```

## ファイル操作

```python
from pathlib import Path

# パストラバーサル防止
def safe_read(base_dir: Path, filename: str) -> str:
    filepath = (base_dir / filename).resolve()
    if not filepath.is_relative_to(base_dir.resolve()):
        raise ValueError("不正なファイルパス")
    return filepath.read_text()
```

## シリアライズ

| 禁止 | 代替 |
|------|------|
| `pickle.loads(untrusted_data)` | `json.loads()` を使用 |
| `yaml.load(data)` | `yaml.safe_load(data)` |
| `eval()` / `exec()` に外部入力 | 絶対に使用しない |

## パスワードハッシュ

```python
# bcrypt または argon2 を使用する（MD5, SHA は禁止）
from argon2 import PasswordHasher

ph = PasswordHasher()
hashed = ph.hash(password)
ph.verify(hashed, password)  # 検証
```

## HTTPS / 通信

- 外部 API 通信は必ず HTTPS を使用する
- TLS 証明書の検証を無効にしない（`verify=False` 禁止）
- タイムアウトを必ず設定する

```python
import httpx

# Good: HTTPS + タイムアウト + 証明書検証
response = httpx.get("https://api.example.com/data", timeout=30)
```
