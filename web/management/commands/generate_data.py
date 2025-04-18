from datetime import timedelta
from random import randint, choice, random
import time
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from web.models import TimeSlot, TimeSlotTag, User


class Command(BaseCommand):
    help = "Генерирует тестовые данные"
    # это обязательный метод для команды
    def handle(self, *args, **options): # именно он вызывается при вызове команды
        # чтобы время посмотреть
        start = time.time()

        current_date = now()
        user = User.objects.first()
        tags = TimeSlotTag.objects.filter(user=user) # вытаскиваем все теги пользователя

        time_slots = []

        for day_index in range(30):
            current_date -= timedelta(days=1)

            # создадим цикл у таймслота
            for slot_index in range(randint(5, 10)):
                start_date = current_date + timedelta(hours=randint(0, 10))
                end_date = start_date + timedelta(hours=randint(0, 10))

                # делаем тут сохранение модели
                time_slots.append(TimeSlot(
                    title=f"generated {day_index}-{slot_index}",
                    start_date=start_date,
                    end_date=end_date,
                    is_realtime=choice((True, False)),
                    user=user,
                ))

        saved_time_slots = TimeSlot.objects.bulk_create(time_slots)

        time_slot_tags = []
        for time_slot in saved_time_slots:
            count_of_tags = randint(0, len(tags))
            for tag_index in range(count_of_tags):
                time_slot_tags.append(
                    TimeSlot.tags.through(timeslot_id=time_slot.id, timeslottag_id=tags[tag_index].id) # обращаемся к таблице
                )
        TimeSlot.tags.through.objects.bulk_create(time_slot_tags)
        end = time.time()
        print(f"Время выполнения: {end - start:.2f} секунд")