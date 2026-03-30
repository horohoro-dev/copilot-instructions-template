"""テスト用フィクスチャ定義."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from tasks.models import Task


@pytest.fixture
def api_client() -> APIClient:
    """DRF テスト用 API クライアントを返す."""
    return APIClient()


@pytest.fixture
def sample_task(db) -> Task:
    """基本的なサンプルタスクを作成して返す."""
    return Task.objects.create(
        title="サンプルタスク",
        description="テスト用のタスクです",
        status="todo",
        priority="medium",
    )


@pytest.fixture
def overdue_task(db) -> Task:
    """期限切れのタスクを作成して返す."""
    return Task.objects.create(
        title="期限切れタスク",
        description="期限が過ぎたタスク",
        status="todo",
        priority="high",
        due_date=timezone.now().date() - timedelta(days=1),
    )


@pytest.fixture
def future_task(db) -> Task:
    """将来の期限を持つタスクを作成して返す."""
    return Task.objects.create(
        title="将来のタスク",
        description="まだ期限が来ていないタスク",
        status="in_progress",
        priority="low",
        due_date=timezone.now().date() + timedelta(days=7),
    )


@pytest.fixture
def multiple_tasks(db) -> list[Task]:
    """複数のタスクを作成して返す."""
    tasks = [
        Task.objects.create(
            title="タスク1",
            status="todo",
            priority="high",
        ),
        Task.objects.create(
            title="タスク2",
            status="in_progress",
            priority="medium",
        ),
        Task.objects.create(
            title="タスク3",
            status="done",
            priority="low",
        ),
    ]
    return tasks
