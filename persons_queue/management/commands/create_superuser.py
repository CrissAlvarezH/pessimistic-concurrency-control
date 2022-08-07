from typing import Optional

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a superuser"

    def handle(self, *args, **kwargs) -> Optional[str]:
        email = "root@email.com"
        if User.objects.filter(email=email).exists():
            return "Superuser is already created"

        root = User.objects.create(
            email="root@email.com",
            username="root@email.com",
        )

        root.set_password("12345")
        root.is_superuser = True
        root.is_staff = True
        root.save()
