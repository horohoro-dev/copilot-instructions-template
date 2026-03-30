---
applyTo: "**/models.py,**/views.py,**/serializers.py,**/forms.py,**/admin.py,**/urls.py,**/managers.py,**/signals.py"
description: "DRF シリアライザー・認証・テスト"
---

# DRF・認証・テスト規約

## DRF シリアライザー
- 読み取り用と書き込み用でシリアライザーを分離する（必要に応じて）
- フィールドレベルバリデーション: `validate_<field>()` メソッド
- オブジェクトレベルバリデーション: `validate()` メソッド
- ネストされたシリアライザーには `create()` / `update()` をカスタム実装する
- `SerializerMethodField` でカスタム算出フィールドを定義する
- `PrimaryKeyRelatedField(source=...)` で書き込み用 FK フィールドを定義する

```python
class ArticleReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_recent = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "title", "author", "is_recent", "created_at"]

    def get_is_recent(self, obj: Article) -> bool:
        from django.utils import timezone
        return obj.created_at >= timezone.now() - timezone.timedelta(days=7)


class ArticleWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Article
        fields = ["title", "body", "tags", "category_id"]

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

## テスト
- pytest-django を使用する
- テストデータの生成には **Factory Boy** を推奨する（fixtures JSON より保守性が高い）
- API テストでは `rest_framework.test.APIClient` を使用する
- 認証が必要なテストでは `force_authenticate()` でスキップする
