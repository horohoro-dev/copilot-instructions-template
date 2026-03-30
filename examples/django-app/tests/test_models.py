"""Task モデルのテスト."""

from datetime import timedelta

import pytest
from django.utils import timezone

from tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:
    """Task モデルの基本的な動作をテストする."""

    def test_str_returns_title(self, sample_task: Task) -> None:
        """__str__ がタスクのタイトルを返すことを検証する."""
        assert str(sample_task) == "サンプルタスク"

    def test_default_status_is_todo(self, db) -> None:
        """ステータスのデフォルト値が 'todo' であることを検証する."""
        task = Task.objects.create(title="デフォルトテスト")
        assert task.status == "todo"

    def test_default_priority_is_medium(self, db) -> None:
        """優先度のデフォルト値が 'medium' であることを検証する."""
        task = Task.objects.create(title="デフォルトテスト")
        assert task.priority == "medium"

    def test_created_at_auto_set(self, sample_task: Task) -> None:
        """created_at が自動的に設定されることを検証する."""
        assert sample_task.created_at is not None

    def test_updated_at_auto_set(self, sample_task: Task) -> None:
        """updated_at が自動的に設定されることを検証する."""
        assert sample_task.updated_at is not None

    def test_ordering_is_by_created_at_desc(self, multiple_tasks: list[Task]) -> None:
        """デフォルトの並び順が created_at の降順であることを検証する."""
        tasks = list(Task.objects.all())
        assert tasks[0].title == "タスク3"
        assert tasks[1].title == "タスク2"
        assert tasks[2].title == "タスク1"


@pytest.mark.django_db
class TestTaskIsOverdue:
    """Task.is_overdue メソッドのテスト."""

    def test_overdue_when_past_due_date(self, overdue_task: Task) -> None:
        """期限を過ぎたタスクは期限切れと判定されることを検証する."""
        assert overdue_task.is_overdue() is True

    def test_not_overdue_when_future_due_date(self, future_task: Task) -> None:
        """期限が将来のタスクは期限切れではないことを検証する."""
        assert future_task.is_overdue() is False

    def test_not_overdue_when_no_due_date(self, sample_task: Task) -> None:
        """期限が未設定のタスクは期限切れではないことを検証する."""
        assert sample_task.is_overdue() is False

    def test_not_overdue_when_done(self, db) -> None:
        """完了済みタスクは期限切れではないことを検証する."""
        task = Task.objects.create(
            title="完了タスク",
            status="done",
            due_date=timezone.now().date() - timedelta(days=1),
        )
        assert task.is_overdue() is False


@pytest.mark.django_db
class TestTaskMarkAsDone:
    """Task.mark_as_done メソッドのテスト."""

    def test_mark_as_done_changes_status(self, sample_task: Task) -> None:
        """mark_as_done でステータスが 'done' に変更されることを検証する."""
        sample_task.mark_as_done()
        sample_task.refresh_from_db()
        assert sample_task.status == "done"

    def test_mark_as_done_from_in_progress(self, future_task: Task) -> None:
        """進行中のタスクを完了にできることを検証する."""
        assert future_task.status == "in_progress"
        future_task.mark_as_done()
        future_task.refresh_from_db()
        assert future_task.status == "done"


@pytest.mark.django_db
class TestTaskEstimatedHours:
    """Task.estimated_hours フィールドのテスト."""

    def test_default_estimated_hours_is_none(self, db) -> None:
        """見積もり時間のデフォルト値が None であることを検証する."""
        task = Task.objects.create(title="デフォルトテスト")
        assert task.estimated_hours is None

    def test_set_estimated_hours(self, db) -> None:
        """見積もり時間を設定できることを検証する."""
        task = Task.objects.create(title="見積もりテスト", estimated_hours=4.5)
        task.refresh_from_db()
        assert task.estimated_hours == pytest.approx(4.5)
