---
name: tdd
description: 'テスト駆動開発（TDD）の手順。Red → Green → Refactor サイクルに従い、テストファーストで開発を進める。テストのない実装コードは受け入れない。'
---

## TDD の基本原則

- テストのない実装コードは破棄する（Superpowers の核心思想）
- 実装コードを書く前に、必ず失敗するテストを書く
- テストが通る最小限の実装だけを書く
- リファクタリングはテストが通っている状態でのみ行う

## TDD サイクル（Red → Green → Refactor）

### Step 1: Red（失敗するテストを書く）

- 実装したい振る舞いを記述するテストを書く
- テストを実行し、意図した理由で失敗することを確認する
- 失敗理由が想定と異なる場合はテストを修正する

### Step 2: Green（テストを通す最小限の実装）

- テストが通る最小限のコードを書く
- 「正しい」実装ではなく「動く」実装を目指す
- この段階ではコード品質を気にしない

### Step 3: Refactor（テストを維持しながら改善）

- 重複を除去する
- 命名を改善する
- 構造を整理する
- すべてのテストが通ることを常に確認する

## pytest のベストプラクティス

### テスト構造（AAA パターン）

```python
def test_ユーザー作成_有効なデータ_ユーザーが返される():
    # Arrange（準備）
    user_data = {"name": "太郎", "email": "taro@example.com"}

    # Act（実行）
    user = create_user(**user_data)

    # Assert（検証）
    assert user.name == "太郎"
    assert user.email == "taro@example.com"
```

### テスト命名規約

- パターン: `test_<対象>_<条件>_<期待結果>`
- 例: `test_create_user_with_duplicate_email_raises_conflict`

### フィクスチャ

```python
@pytest.fixture
def sample_user(db):
    return User.objects.create(name="太郎", email="taro@example.com")

def test_ユーザー取得(sample_user):
    result = get_user(sample_user.id)
    assert result == sample_user
```

### パラメータ化テスト

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert to_upper(input) == expected
```

### モック

```python
from unittest.mock import patch

@patch("mymodule.external_api")
def test_外部API呼び出し(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = process_data()
    mock_api.assert_called_once()
    assert result["status"] == "ok"
```

### 非同期テスト

```python
import pytest

@pytest.mark.asyncio
async def test_非同期データ取得():
    result = await fetch_data()
    assert result is not None
```

## カバレッジ基準

- 全体: 80% 以上（必須）
- クリティカルパス: 100% を目標
- ブランチカバレッジを有効にする
- `pytest --cov --cov-report=term-missing --cov-fail-under=80`

## テスト種別

| 種別 | 対象 | 実行頻度 |
|------|------|----------|
| ユニットテスト | 個別の関数・クラス | 常時 |
| 統合テスト | API エンドポイント、DB 操作 | PR 時 |
| E2E テスト | 重要なユーザーフロー | リリース前 |

## やってはいけないこと

- 実装の詳細をテストする（振る舞いをテストする）
- テスト間で状態を共有する
- テスト内で例外をキャッチする（`pytest.raises` を使う）
- 過度なモックで偽の安心感を得る
- `@pytest.mark.skip` を本番コードに残す
