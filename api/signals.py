from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Topic, Activity
from datetime import date, timedelta

@receiver(post_save, sender=Topic)
def revision_plan(sender, instance, created, **kwargs):
    if created: 
        user = instance.user
        topic = instance
        datas = [
            date.today() + timedelta(days=1),
            date.today() + timedelta(days=4),
            date.today() + timedelta(days=11),
            date.today() + timedelta(days=32),
            date.today() + timedelta(days=62),
        ]
        tipos = ["resumo+flashcards"] * 5  
        for i in range(5):
            Activity.objects.create(
                user=user,
                topic=topic,
                type=type[i],
                data=datas[i],
                status="pendente"
            )