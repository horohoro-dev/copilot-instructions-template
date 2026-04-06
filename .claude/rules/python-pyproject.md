---
globs: "**/pyproject.toml"
description: "pyproject.toml 設定・ツール構成・依存関係管理"
---

# pyproject.toml 規約

## プロジェクト基本設定

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.12"
description = "プロジェクトの説明"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov", "factory-boy"]
docs = ["sphinx", "myst-parser"]
```

## ツール設定

### ruff（リンター / フォーマッター）

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E", "W",     # pycodestyle
    "F",           # pyflakes
    "I",           # isort
    "N",           # pep8-naming
    "UP",          # pyupgrade
    "B",           # flake8-bugbear
    "SIM",         # flake8-simplify
    "S",           # flake8-bandit（セキュリティ）
]
ignore = ["E501"]  # 行長は line-length で制御

[tool.ruff.lint.isort]
known-first-party = ["myproject"]
```

### pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=src/myproject",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
    "--cov-branch",
    "-v",
]
markers = [
    "unit: ユニットテスト",
    "integration: 統合テスト",
]
```

### ty（型チェッカー）

```toml
[tool.ty.environment]
python-version = "3.12"

[tool.ty.rules]
possibly-unresolved-reference = "error"
unused-ignore-comment = "warn"
```

## 依存関係管理のルール

| ルール | 理由 |
|--------|------|
| `uv add <pkg>` で追加する | pyproject.toml を手動編集しない |
| `uv.lock` を Git にコミットする | 再現性を保証 |
| 開発ツールは `[dependency-groups]` に配置 | `[project.optional-dependencies]` は配布用 |
| バージョン指定は `>=X.Y` を基本とする | 厳密なピン留めは `uv.lock` に任せる |
| `uv sync --all-groups` で全グループインストール | グループ指定で部分インストールも可能 |

## Makefile 連携

```makefile
.PHONY: dev lint format test

dev:
	uv sync --all-groups

lint:
	uv run ruff check . && uv run ruff format --check .

format:
	uv run ruff format .

test:
	uv run pytest
```
