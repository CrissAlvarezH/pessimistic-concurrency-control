# Pessimistic concurrency control

En aplicaciones altamente concurrentes es necesario tener en cuenta la consistencia de los datos a la hora de hacer funcionalidades que interactuen con la base de datos, ya que se podrían crear registros duplicados e incosistencias debido a que varios hilos de la aplicación acceden a las mismas partes de la base de datos al mismo tiempo en situaciones donde este caso no es el deseado.
En alguno casos querremos que la lectura y escritura de la base de datos sea forzosamente sincrona para evitar duplicados, vemos un ejemplo aquí:

# Caso de uso

En este repositorio tenemos como ejemplo un caso de uso donde es necesario generar un control sobre la concurrencia debido a que el requerimiento así lo exige para evitar duplidad en la base de datos, el caso es el siguiente:

    Se require un programa que agregue personas en una cola, cada persona que sea agregada 
    a la cola se le asignará una posición la cual será una unidad posterior a la de 
    la persona anterior, por ejemplo: para la cola llamada "banco" se forman las personas
    "Carlos", "Juan" y "Cristian", en ese orden, despues de ser agregados a la cola
    cada uno tendra las siguientes posiciones asignadas:
    "Carlos_i1", "Juan_i2", "Cristian_i3"
    IMPORTANTE: No pueden existir dos personas con la misma posición


# Implementación

## Opción 1. No thread safe
Para el primer caso (Sin control sobre la concurrencia) tenemos el siguiente metodo

    def add_person_v1(person_name: str, queue_name: str) -> Person:
        person = Person.objects.create(name=person_name)

        # create queue if not exists
        queue, _ = Queue.objects.get_or_create(name=queue_name)

        last_position = 1
        last_person_in_queue = (
            PersonInQueue.objects.filter(queue_id=queue.id).order_by("-created_at").first()
        )
        if last_person_in_queue:
            last_position = last_person_in_queue.position + 1

        person.name = person_name + "_i" + str(last_position)
        person.save()

        PersonInQueue.objects.create(person=person, queue=queue, position=last_position)

        return person

> *persons_queue/services.py*

El problema con este metodo es que no es seguro cuando es sometido a hilos.
Para probar esto tenemos el seguiente test:

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

> *persons_queue/tests.py*

Este test nos muestra que al correr la función `add_person_v1` en dos hilos genera
una duplicidad en las posiciones, **lo cual es algo que no queremos.**


## Opción 2. Thread safe

Para este caso nos aseguramos de bloquear los registros de la base de datos que
estamos usando para que otros hilos tengan que esperar hasta que se desbloquee para 
poder acceder a ellos. Utilizando `select_for_update` y `transaction.atomic`

    def add_person_v2(person_name: str, queue_name: str) -> Person:
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

> *persons_queue/services.py*

Aquí cada instancia de este metodo que este siendo llamada en diferentes hilos tendran que
encolarse para tener acceso a la base de datos en la cola correspondiente, ya que se hace un lock
al registro del modelo `Queue` mientras se agrega una persona a la cola. El test respectivo es el siguiente:

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

> *persons_queue/tests.py*

Aquí vemos que se evalua que las personas agregadas a la cola se les asigne una posicion diferente
y consistente, siguiente la secuencia que debe llevar la cola.


# Ejecutar tests

Para ejecutar test basta con correr el siguente comando

    make test