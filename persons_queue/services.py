from django.db import transaction

from .models import Person, Queue, PersonInQueue


def add_person(person_name: str, queue_name: str) -> Person:
    person = Person.objects.create(name=person_name)

    if queue_name:
        # create queue if not exists
        Queue.objects.get_or_create(name=queue_name)

        with transaction.atomic():
            queue = (
                Queue.objects
                .select_for_update()
                .filter(name=queue_name)
                .first()
            )

            last_position = 1
            last_person = (
                PersonInQueue.objects
                .filter(person_id=person.id)
                .order_by("-created_at")
                .first()
            )
            if last_person:
                last_position = last_person

