from rest_framework import serializers

from .models import Person, Queue, PersonInQueue


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class PersonInQueueSerializer(serializers.ModelSerializer):
    person = PersonSerializer()

    class Meta:
        model = PersonInQueue
        fields = "__all__"


class QueueSerializer(serializers.ModelSerializer):
    persons_in_queue = PersonInQueueSerializer(source="personinqueue_set")

    class Meta:
        model = Queue
        fields = "__all__"
