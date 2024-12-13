from django.db import models
from base import models as base_models

# Create your models here.
class Messages(models.Model):
    # group = models.ForeignKey(base_models.Groups, on_delete=models.CASCADE)
    # club = models.ForeignKey(base_models.Club, on_delete=models.CASCADE, null=True, blank=True)
    room_name = models.TextField(null=True, blank=True)
    sender = models.TextField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.content

