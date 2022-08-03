from rest_framework import viewsets, mixins

from .models import Queue
from .serializers import QueueSerializer


class QueueViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer
