from django.contrib import admin

from .models import Person, PersonInQueue, Queue


class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "id")


admin.site.register(Person, PersonAdmin)


class PersonInQueueInline(admin.TabularInline):
    model = PersonInQueue


class QueueAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    inlines = (PersonInQueueInline,)


admin.site.register(Queue, QueueAdmin)
