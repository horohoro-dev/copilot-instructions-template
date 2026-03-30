"""タスク API ビュー定義.

DRF の ModelViewSet を使用してタスクの CRUD 操作を提供する。
ビジネスロジックはモデルに委譲し、ビューはリクエスト処理に専念する。
"""

from rest_framework import viewsets

from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """タスクの CRUD 操作を提供する ViewSet.

    フィルタリング:
        - status: ステータスでフィルタリング（例: ?status=todo）
        - priority: 優先度でフィルタリング（例: ?priority=high）
    """

    serializer_class = TaskSerializer

    def get_queryset(self):
        """フィルタリングパラメータを適用したクエリセットを返す.

        Returns:
            フィルタリング済みの Task クエリセット。
        """
        queryset = Task.objects.all()

        # ステータスでフィルタリング
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 優先度でフィルタリング
        priority_filter = self.request.query_params.get("priority")
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        return queryset
