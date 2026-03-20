from django.db import migrations

def create_periodic_tasks(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    
    # Create 1 hour interval
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period='hours',
    )
    
    # Create periodic task
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Task Reminder Sweep (Hourly)',
        task='tasks.run_reminder_sweep',
    )

def remove_periodic_tasks(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    PeriodicTask.objects.filter(name='Task Reminder Sweep (Hourly)').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0002_alter_task_deadline'),
        ('django_celery_beat', '0019_alter_periodictasks_options'),
    ]

    operations = [
        migrations.RunPython(create_periodic_tasks, remove_periodic_tasks),
    ]
