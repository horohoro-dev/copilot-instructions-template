"""タスク API シリアライザ定義.

タスクデータの入出力変換とバリデーションを提供する。
"""

from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """タスクモデル用シリアライザ.

    作成時に期限日が過去でないことをバリデーションする。
    更新時は過去の期限日も許容する（既存データの修正を可能にするため）。

    Attributes:
        is_overdue: タスクが期限切れかどうかの読み取り専用フィールド。
    """

    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "estimated_hours",
            "due_date",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_is_overdue(self, obj: Task) -> bool:
        """タスクが期限切れかどうかを返す.

        Args:
            obj: シリアライズ対象のタスクインスタンス。

        Returns:
            期限切れなら True。
        """
        return obj.is_overdue()

    def validate_due_date(self, value):
        """期限日のバリデーション.

        作成時のみ過去の日付を拒否する。更新時は許容する。

        Args:
            value: バリデーション対象の期限日。

        Returns:
            バリデーション済みの期限日。

        Raises:
            serializers.ValidationError: 作成時に過去の日付が指定された場合。
        """
        if value is None:
            return value

        # 更新時（インスタンスが存在する場合）は過去の日付を許容する
        if self.instance is not None:
            return value

        if value < timezone.now().date():
            raise serializers.ValidationError("期限日に過去の日付は指定できません。")
        return value
