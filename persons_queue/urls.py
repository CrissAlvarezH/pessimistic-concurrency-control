from rest_framework.routers import SimpleRouter

from .views import QueueViewSet


router = SimpleRouter()

router.register("queues", QueueViewSet)

urlpatterns = router.urls
