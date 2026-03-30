"""Task API ビューのテスト."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from tasks.models import Task


@pytest.mark.django_db
class TestTaskListAPI:
    """タスク一覧取得 API のテスト."""

    def test_list_tasks_returns_200(self, api_client: APIClient) -> None:
        """タスク一覧の取得が 200 を返すことを検証する."""
        response = api_client.get("/api/tasks/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_tasks_returns_all_tasks(
        self, api_client: APIClient, multiple_tasks: list[Task]
    ) -> None:
        """全タスクが一覧に含まれることを検証する."""
        response = api_client.get("/api/tasks/")
        assert response.data["count"] == 3

    def test_filter_by_status(
        self, api_client: APIClient, multiple_tasks: list[Task]
    ) -> None:
        """ステータスでフィルタリングできることを検証する."""
        response = api_client.get("/api/tasks/", {"status": "todo"})
        assert response.data["count"] == 1
        assert response.data["results"][0]["status"] == "todo"

    def test_filter_by_priority(
        self, api_client: APIClient, multiple_tasks: list[Task]
    ) -> None:
        """優先度でフィルタリングできることを検証する."""
        response = api_client.get("/api/tasks/", {"priority": "high"})
        assert response.data["count"] == 1
        assert response.data["results"][0]["priority"] == "high"


@pytest.mark.django_db
class TestTaskCreateAPI:
    """タスク作成 API のテスト."""

    def test_create_task_returns_201(self, api_client: APIClient) -> None:
        """タスク作成が 201 を返すことを検証する."""
        data = {
            "title": "新しいタスク",
            "description": "テスト用",
            "status": "todo",
            "priority": "medium",
        }
        response = api_client.post("/api/tasks/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_task_persists_data(self, api_client: APIClient) -> None:
        """作成したタスクがデータベースに保存されることを検証する."""
        data = {
            "title": "永続化テスト",
            "description": "保存確認",
            "status": "todo",
            "priority": "high",
        }
        api_client.post("/api/tasks/", data, format="json")
        assert Task.objects.filter(title="永続化テスト").exists()

    def test_create_task_with_future_due_date(self, api_client: APIClient) -> None:
        """将来の期限でタスクを作成できることを検証する."""
        future_date = (timezone.now().date() + timedelta(days=7)).isoformat()
        data = {
            "title": "将来のタスク",
            "due_date": future_date,
        }
        response = api_client.post("/api/tasks/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_task_with_past_due_date_fails(self, api_client: APIClient) -> None:
        """過去の期限でタスクを作成するとバリデーションエラーになることを検証する."""
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        data = {
            "title": "過去のタスク",
            "due_date": past_date,
        }
        response = api_client.post("/api/tasks/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "due_date" in response.data

    def test_create_task_with_estimated_hours(self, api_client: APIClient) -> None:
        """見積もり時間付きでタスクを作成できることを検証する."""
        data = {
            "title": "見積もりタスク",
            "estimated_hours": 3.0,
        }
        response = api_client.post("/api/tasks/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["estimated_hours"] == 3.0

    def test_create_task_without_title_fails(self, api_client: APIClient) -> None:
        """タイトルなしでタスクを作成するとエラーになることを検証する."""
        data = {"description": "タイトルなし"}
        response = api_client.post("/api/tasks/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTaskRetrieveAPI:
    """タスク詳細取得 API のテスト."""

    def test_retrieve_task_returns_200(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """タスク詳細の取得が 200 を返すことを検証する."""
        response = api_client.get(f"/api/tasks/{sample_task.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "サンプルタスク"

    def test_retrieve_includes_readonly_fields(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """読み取り専用フィールドがレスポンスに含まれることを検証する."""
        response = api_client.get(f"/api/tasks/{sample_task.pk}/")
        assert "id" in response.data
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert "is_overdue" in response.data

    def test_retrieve_nonexistent_returns_404(self, api_client: APIClient) -> None:
        """存在しないタスクの取得が 404 を返すことを検証する."""
        response = api_client.get("/api/tasks/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskUpdateAPI:
    """タスク更新 API のテスト."""

    def test_update_task_returns_200(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """タスク更新が 200 を返すことを検証する."""
        data = {"title": "更新されたタスク"}
        response = api_client.patch(
            f"/api/tasks/{sample_task.pk}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "更新されたタスク"

    def test_update_allows_past_due_date(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """更新時は過去の期限を許容することを検証する（既存タスクの修正のため）."""
        past_date = (timezone.now().date() - timedelta(days=1)).isoformat()
        data = {"due_date": past_date}
        response = api_client.patch(
            f"/api/tasks/{sample_task.pk}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTaskDeleteAPI:
    """タスク削除 API のテスト."""

    def test_delete_task_returns_204(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """タスク削除が 204 を返すことを検証する."""
        response = api_client.delete(f"/api/tasks/{sample_task.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_task_removes_from_db(
        self, api_client: APIClient, sample_task: Task
    ) -> None:
        """タスク削除後にデータベースから消えることを検証する."""
        task_id = sample_task.pk
        api_client.delete(f"/api/tasks/{task_id}/")
        assert not Task.objects.filter(pk=task_id).exists()
