import sched
import time

# Создаём планировщик
scheduler = sched.scheduler(time.time, time.sleep)

def periodic_task(name, interval):
    """Периодическая задача, которая перезапускается сама себя"""
    print(f"{name} выполнено в {time.strftime('%X')}")
    # Планируем следующее выполнение
    scheduler.enter(interval, 1, periodic_task, argument=(name, interval))

# Запускаем несколько задач
scheduler.enter(0, 1, periodic_task, argument=('Задача 1', 3))
scheduler.enter(1, 1, periodic_task, argument=('Задача 2', 5))

print("Старт планировщика...")
scheduler.run()