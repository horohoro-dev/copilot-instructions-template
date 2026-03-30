---
applyTo: "**/models.py,**/views.py,**/serializers.py,**/forms.py,**/admin.py,**/urls.py,**/managers.py,**/signals.py"
description: "Django モデル設計・クエリ最適化・ビュー"
---

# Django 開発規約

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
