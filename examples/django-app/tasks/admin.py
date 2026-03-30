"""タスク管理画面設定.

Django 管理画面でタスクモデルを操作するための設定。
"""

from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """タスクモデルの管理画面設定.

    一覧表示、フィルタリング、検索の設定を提供する。
    """

    list_display = [
        "title",
        "status",
        "priority",
        "due_date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description"]
    ordering = ["-created_at"]
