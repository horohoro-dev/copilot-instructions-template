---
applyTo: "**/*.py"
description: "Python 設定管理・環境変数・シークレット"
---

# Python 設定管理規約

## 基本原則

- 設定値はすべて環境変数で管理する（ハードコード禁止）
- `pydantic-settings` で型安全な設定クラスを定義する
- `.env` ファイルは Git にコミットしない
- `.env.example` でテンプレートを共有する

## pydantic-settings による設定

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """アプリケーション設定。"""

    # DB
    database_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")

    # API
    api_key: str = Field(alias="API_KEY")
    api_timeout: int = Field(default=30, alias="API_TIMEOUT")

    # アプリ
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

## .env ファイル構成

```bash
# .env.example（Git にコミット）
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
API_KEY=your-api-key-here
DEBUG=true
LOG_LEVEL=DEBUG

# .env（Git にコミットしない）
DATABASE_URL=postgresql://prod-user:secret@prod-db:5432/app
API_KEY=sk-actual-key
DEBUG=false
LOG_LEVEL=INFO
```

## 環境別設定パターン

```python
class Settings(BaseSettings):
    env: str = Field(default="development", alias="APP_ENV")

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_testing(self) -> bool:
        return self.env == "testing"
```

## アンチパターン

| 禁止 | 代替 |
|------|------|
| 設定値のハードコード | 環境変数 + `pydantic-settings` |
| `.env` を Git にコミット | `.gitignore` に追加、`.env.example` で共有 |
| `os.environ.get()` の散在 | `Settings` クラスに集約 |
| 型なし設定（全て `str`） | `pydantic-settings` で型バリデーション |
| 本番シークレットをログ出力 | シークレットは `SecretStr` 型を使用 |
| 環境別の if 分岐の散在 | `Settings` のプロパティに集約 |

## シークレット管理

```python
from pydantic import SecretStr

class Settings(BaseSettings):
    api_key: SecretStr = Field(alias="API_KEY")

# 値にアクセスするには明示的に get_secret_value() を呼ぶ
key = settings.api_key.get_secret_value()

# str(settings.api_key) → "**********"（ログに漏れない）
```
