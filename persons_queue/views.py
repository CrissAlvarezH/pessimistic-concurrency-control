from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .services import add_person
from .models import Queue
from .serializers import PersonSerializer, QueueSerializer


class QueueViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Queue.objects.all()
    serializer_class = QueueSerializer

    @action(detail=False, methods=["POST"])
    def add(self, request):
        person_name = self.request.data.get("person_name")
        queue_name = self.request.data.get("queue_name")

        if not person_name or not queue_name:
            raise ValidationError(
                "person_name and queue_name is required")

        person = add_person(person_name, queue_name)

        return Response(data=PersonSerializer(person).data)
