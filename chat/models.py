from django.db import models
from django.contrib.auth import get_user_model


# For default user model it give's default user
User = get_user_model()

# Create your models here.

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_message', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username
    
    @staticmethod
    def last_10_messages():
        return Message.objects.order_by('-timestamp')[:10]
