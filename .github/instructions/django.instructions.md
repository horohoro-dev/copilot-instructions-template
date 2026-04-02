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
        "users.User", on_delete=models.CASCADE, related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = verbose_name_plural = "記事"

    def __str__(self) -> str:
        return self.title
```

## クエリ最適化

- **N+1 問題の防止**（最重要）:
  - `ForeignKey` / `OneToOneField` → `select_related()`（JOIN）
  - `ManyToManyField` / 逆参照 → `prefetch_related()`（別クエリ）
- 部分取得: `only()`, `defer()` で必要なフィールドのみ
- 大規模イテレーション: `iterator()` でメモリ節約
- 集約: `annotate()`, `aggregate()` でDB側計算
- DB レベル操作: `F()` 式、`Q()` オブジェクト

```python
class ArticleManager(models.Manager):
    def published(self) -> QuerySet["Article"]:
        return self.filter(status="published").select_related("author")

    def with_related(self) -> QuerySet["Article"]:
        return self.select_related("author").prefetch_related("tags", "comments")

# 集約: annotate / aggregate / F() / Q()
Category.objects.annotate(count=Count("articles")).filter(count__gt=0)
```

### 一括操作

```python
Article.objects.bulk_create(articles, batch_size=1000)
Article.objects.bulk_update(articles, ["status"], batch_size=1000)
Article.objects.filter(status="draft").update(status="archived")
```

## ビュー

- クラスベースビューを推奨する
- ビジネスロジックはサービス層またはモデルメソッドに分離する
- `get_queryset()` で `select_related` / `prefetch_related` を必ず適用

```python
class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Article]:
        return Article.objects.with_related()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ArticleWriteSerializer
        return ArticleReadSerializer
```

## Signals

- シグナルはビジネスロジックに使わない（副作用の追跡が困難になる）
- 使用を限定する: 監査ログ、キャッシュ無効化、外部システム通知
- シグナルハンドラは軽量に保つ（重い処理は Celery タスクに委譲）

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Article)
def invalidate_article_cache(sender, instance, **kwargs) -> None:
    """記事更新時にキャッシュを無効化する。"""
    cache.delete(f"article:{instance.id}")
```

### Signals のアンチパターン

| 禁止 | 代替 |
|------|------|
| シグナルでビジネスロジック実行 | サービス層のメソッドで明示的に呼ぶ |
| シグナル内で DB 書き込み（循環リスク） | `transaction.on_commit()` で遅延実行 |
| シグナルの過剰使用 | 明示的なメソッド呼び出しを優先 |
