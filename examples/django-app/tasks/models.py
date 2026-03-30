"""タスクモデル定義.

タスク管理に必要なデータモデルとビジネスロジックを提供する。
"""

from django.db import models
from django.utils import timezone


class Task(models.Model):
    """タスクを表すモデル.

    Attributes:
        title: タスクのタイトル。
        description: タスクの詳細説明。
        status: タスクの進捗状態。
        priority: タスクの優先度。
        due_date: タスクの期限日。
        created_at: 作成日時。
        updated_at: 更新日時。
    """

    class Status(models.TextChoices):
        """タスクのステータス選択肢."""

        TODO = "todo", "未着手"
        IN_PROGRESS = "in_progress", "進行中"
        DONE = "done", "完了"

    class Priority(models.TextChoices):
        """タスクの優先度選択肢."""

        LOW = "low", "低"
        MEDIUM = "medium", "中"
        HIGH = "high", "高"

    title = models.CharField("タイトル", max_length=255)
    description = models.TextField("説明", blank=True, default="")
    status = models.CharField(
        "ステータス",
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        "優先度",
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    estimated_hours = models.FloatField("見積もり時間", null=True, blank=True)
    due_date = models.DateField("期限日", null=True, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "タスク"
        verbose_name_plural = "タスク"

    def __str__(self) -> str:
        """タスクのタイトルを返す."""
        return self.title

    def is_overdue(self) -> bool:
        """タスクが期限切れかどうかを判定する.

        期限日が設定されていて、かつ現在日を過ぎており、
        ステータスが完了でない場合に True を返す。

        Returns:
            期限切れなら True、そうでなければ False。
        """
        if self.due_date is None:
            return False
        if self.status == self.Status.DONE:
            return False
        return self.due_date < timezone.now().date()

    def mark_as_done(self) -> None:
        """タスクを完了状態に変更して保存する."""
        self.status = self.Status.DONE
        self.save(update_fields=["status", "updated_at"])
