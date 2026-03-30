---
paths:
  - "**/models.py"
  - "**/views.py"
  - "**/serializers.py"
  - "**/forms.py"
  - "**/admin.py"
  - "**/urls.py"
  - "**/managers.py"
  - "**/signals.py"
---

# Django / DRF 開発規約

## モデル設計
- `__str__` メソッドを必ず定義する
- `Meta` クラスで `ordering`, `verbose_name`, `verbose_name_plural` を設定する
- 頻繁にクエリされるフィールドには `db_index=True` を設定する
- `ForeignKey` / `ManyToManyField` には明示的な `related_name` を指定する
- マイグレーションファイルはレビュー対象とする

```python
class Article(models.Model):
    title = models.CharField("タイトル", max_length=200, db_index=True)
    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="著者",
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "記事"
        verbose_name_plural = "記事"

    def __str__(self) -> str:
        return self.title
```

## クエリ最適化
- **N+1 問題の防止**:
  - `ForeignKey` / `OneToOneField` → `select_related()`
  - `ManyToManyField` / 逆参照 → `prefetch_related()`
- 大規模データには `only()`, `defer()`, `iterator()` を使用する
- 一括操作には `bulk_create()`, `bulk_update()`, `.update()` を使用する
- カスタムマネージャーで共通クエリパターンを定義する

```python
class ArticleManager(models.Manager):
    def published(self) -> QuerySet["Article"]:
        return self.filter(status="published").select_related("author")

    def with_comments(self) -> QuerySet["Article"]:
        return self.prefetch_related("comments")
```

## ビュー
- クラスベースビューを推奨する
- ビジネスロジックはサービス層またはモデルメソッドに分離する
- `ViewSet` の `get_queryset()` で `select_related` / `prefetch_related` を適用する

```python
class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Article]:
        return (
            Article.objects.published()
            .select_related("author")
            .prefetch_related("tags")
        )
```

## DRF シリアライザー
- 読み取り用と書き込み用でシリアライザーを分離する（必要に応じて）
- フィールドレベルバリデーション: `validate_<field>()` メソッド
- オブジェクトレベルバリデーション: `validate()` メソッド
- ネストされたシリアライザーには `create()` / `update()` をカスタム実装する

```python
class ArticleReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "author", "created_at"]


class ArticleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "body", "tags"]

    def validate_title(self, value: str) -> str:
        if len(value) < 5:
            raise serializers.ValidationError("タイトルは5文字以上必要です")
        return value
```

## 認証・認可
- JWT トークンの有効期限: アクセストークン 15分、リフレッシュトークン 7日
- トークンは httpOnly Cookie に保存する（localStorage 禁止）
- カスタムパーミッションで `has_permission()` と `has_object_permission()` を実装する
- リソース変更前に所有権を必ず確認する

```python
class IsArticleOwner(BasePermission):
    def has_object_permission(
        self, request: Request, view: View, obj: Article
    ) -> bool:
        return obj.author == request.user
```

## セキュリティ
- CSRF トークンを必ず設定する
- フォーム / シリアライザーで入力バリデーションを行う
- XSS 対策: ユーザー入力をサニタイズする
- CSP（Content Security Policy）ヘッダーを設定する

## マイグレーション
- すべてのスキーマ変更はマイグレーションで管理する
- 本番データベースを手動で変更しない
- NULL 許容カラムの追加はテーブルロックなしで実行可能
- ゼロダウンタイムデプロイ: Expand-Contract パターンを使用する
- データマイグレーションとスキーママイグレーションは分離する

```python
# Expand-Contract パターンの例
# Step 1: 新カラムを NULL 許容で追加（Expand）
# Step 2: データマイグレーションで値を埋める
# Step 3: NOT NULL 制約を追加（Contract）
```

## API 設計
- リソース URL: 複数形、小文字、ケバブケース（例: `/api/v1/user-profiles`）
- バージョニング: URL パス方式（`/api/v1/`）
- ページネーション: 大規模データにはカーソルベースを使用する
- 適切な HTTP ステータスコードを使用する

| ステータス | 用途 |
|-----------|------|
| 200 | 成功（取得・更新） |
| 201 | 作成成功 |
| 204 | 削除成功 |
| 400 | バリデーションエラー |
| 401 | 未認証 |
| 403 | 権限不足 |
| 404 | リソース未発見 |
| 409 | 競合（楽観的ロック等） |

```python
# urls.py
router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("api/v1/", include(router.urls)),
]
```
