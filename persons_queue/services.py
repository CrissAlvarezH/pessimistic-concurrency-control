from turtle import position
from django.db import transaction

from .models import Person, Queue, PersonInQueue


def add_person(person_name: str, queue_name: str) -> Person:
    person = Person.objects.create(name=person_name)

    # create queue if not exists
    Queue.objects.get_or_create(name=queue_name)

    with transaction.atomic():
        queue = Queue.objects.select_for_update().filter(name=queue_name).first()

        last_position = 1
        last_person_in_queue = (
            PersonInQueue.objects.filter(queue_id=queue.id)
            .order_by("-created_at")
            .first()
        )
        if last_person_in_queue:
            last_position = last_person_in_queue.position + 1

        person.name = person_name + "_i" + str(last_position)
        person.save()

        PersonInQueue.objects.create(person=person, queue=queue, position=last_position)

    return person
