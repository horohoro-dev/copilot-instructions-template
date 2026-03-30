---
applyTo: "**/pyproject.toml"
description: "pyproject.toml のツール設定推奨"
---

# pyproject.toml 設定ガイド

## ruff 推奨設定

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]
ignore = ["E501"]  # 行長は formatter に任せる
```

## 型チェッカー設定

型ヒントの静的検証には mypy または ty を使用する。新規プロジェクトでは strict モードを推奨する。

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

既存プロジェクトでは per-module override で段階的に strict 化する。
