from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100)


class Queue(models.Model):
    name = models.CharField(max_length=100)


class PersonInQueue(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    position = models.IntegerField(default=1)
