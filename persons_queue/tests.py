from threading import Thread

from django.test import TransactionTestCase

from .services import add_person_v1, add_person_v2
from .models import Person, PersonInQueue


class ServiceAddPersonV1SynchronousTest(TransactionTestCase):
    def test_synchronous_add(self):
        """Test add_person_v1 on synchronous case"""
        add_person_v1("cristian", "myqueue")
        add_person_v1("cristian", "myqueue")
        add_person_v1("cristian", "myqueue")
        add_person_v1("cristian", "myqueue")

        persons_in_queue = PersonInQueue.objects.all().order_by("created_at")
        self.assertEqual(persons_in_queue[0].position, 1)
        self.assertEqual(persons_in_queue[1].position, 2)
        self.assertEqual(persons_in_queue[2].position, 3)
        self.assertEqual(persons_in_queue[3].position, 4)

        persons = Person.objects.all().order_by("name")
        self.assertEqual(persons[0].name, "cristian_i1")
        self.assertEqual(persons[1].name, "cristian_i2")
        self.assertEqual(persons[2].name, "cristian_i3")
        self.assertEqual(persons[3].name, "cristian_i4")


class ServiceAddPersonV1AsynchronousTest(TransactionTestCase):
    def test_two_asynchronous_add(self):
        """Test add_person_v1 on asynchronous case

        both will have the same position because the method is not thread safe
        """
        thread1 = Thread(target=add_person_v1, args=["juan", "jqueue"])
        thread2 = Thread(target=add_person_v1, args=["juan", "jqueue"])

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        persons = Person.objects.all().order_by("name")

        self.assertEqual(len(persons), 2)
        self.assertEqual(persons[0].name, f"juan_i1")
        self.assertEqual(persons[1].name, f"juan_i1")


class ServiceAddPersonV2SynchronousTest(TransactionTestCase):
    def test_synchronous_add(self):
        """Testing add_person_v2 on synchronous case"""
        add_person_v2("cristian", "myqueue")
        add_person_v2("cristian", "myqueue")
        add_person_v2("cristian", "myqueue")
        add_person_v2("cristian", "myqueue")

        persons_in_queue = PersonInQueue.objects.all().order_by("created_at")
        self.assertEqual(persons_in_queue[0].position, 1)
        self.assertEqual(persons_in_queue[1].position, 2)
        self.assertEqual(persons_in_queue[2].position, 3)
        self.assertEqual(persons_in_queue[3].position, 4)

        persons = Person.objects.all().order_by("name")
        self.assertEqual(persons[0].name, "cristian_i1")
        self.assertEqual(persons[1].name, "cristian_i2")
        self.assertEqual(persons[2].name, "cristian_i3")
        self.assertEqual(persons[3].name, "cristian_i4")


class ServiceAddPersonV2AsynchronousTest(TransactionTestCase):
    def test_two_asynchronous_add(self):
        """Testing add_person_v2 on asynchronous case

        In that case both must be have different positions because the method
        lock de transaction in on specific slice of the database, in this case
        is the 'queue' selected, and avoid the position duplicity
        """
        thread1 = Thread(target=add_person_v2, args=["juan", "jqueue"])
        thread2 = Thread(target=add_person_v2, args=["juan", "jqueue"])

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        persons = Person.objects.all().order_by("name")
        self.assertEqual(len(persons), 2)
        self.assertEqual(persons[0].name, f"juan_i1")
        self.assertEqual(persons[1].name, f"juan_i2")
