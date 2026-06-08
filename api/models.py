from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings #
from django.db import models

class User(AbstractUser):
    country = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)  
    
    def __str__(self):
        return self.username
   
    

class Subject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    progress = models.IntegerField(default=0)

    def __str__(self):
        return self.subject_name
    
class Topic(models.Model):
    # Adicione esta linha abaixo para ligar o Tópico ao Usuário:
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='topics')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, default='')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)   
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE) 
    type = models.CharField(max_length=50)                      
    data = models.DateField()                                    
    status = models.CharField(max_length=20, default="pendente")  


class TopicFile(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='topic_files/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name