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

- **N+1 問題の防止**（最重要）:
  - `ForeignKey` / `OneToOneField` → `select_related()`（JOIN）
  - `ManyToManyField` / 逆参照 → `prefetch_related()`（別クエリ）
- 部分取得: `only()`, `defer()` で必要なフィールドのみ
- 大規模イテレーション: `iterator()` でメモリ節約
- 集約: `annotate()`, `aggregate()` でDB側計算
- DB レベル操作: `F()` 式、`Q()` オブジェクト

```python
from django.db.models import Count, Avg, F, Q

# カスタムマネージャーで共通クエリを定義
class ArticleManager(models.Manager):
    def published(self) -> QuerySet["Article"]:
        return self.filter(status="published").select_related("author")

    def with_related(self) -> QuerySet["Article"]:
        return self.select_related("author").prefetch_related("tags", "comments")

# 集約・アノテーション
Category.objects.annotate(article_count=Count("articles")).filter(article_count__gt=0)
Product.objects.update(price=F("price") * 1.1)  # DB レベルで一括更新
```

### 一括操作（大量データ処理）

```python
# bulk_create: batch_size を指定して分割挿入
Article.objects.bulk_create(articles, batch_size=1000)

# bulk_update: 更新フィールドを明示
Article.objects.bulk_update(articles, ["status", "updated_at"], batch_size=1000)

# QuerySet.update(): 条件一括更新（最速）
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
