"""タスクアプリケーションの URL 設定.

DRF の DefaultRouter を使用してタスク API のルーティングを定義する。
"""

from rest_framework.routers import DefaultRouter

from tasks.views import TaskViewSet

# DRF ルーター設定
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = router.urls
