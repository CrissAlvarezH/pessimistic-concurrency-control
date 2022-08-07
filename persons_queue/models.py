from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"


class Queue(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.id}: {self.name}"


class PersonInQueue(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
