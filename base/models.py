from django.db import models
from django.contrib.auth.models import User

# Create your models here. We can create classes - means tables..

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) # Null is allowed, by default is false!
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) # takes snapshot everytime its saved
    created = models.DateTimeField(auto_now_add=True) # only takes snapshot when saved first time
    class Meta:
        ordering = ['-updated', '-created'] # '-' sign makes newer one come at top
    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # This will delete all messages in a room after the room is deleted.
    # to save the messages in a database, on_delete=models.SET_NULL
    body = models.TextField() # required
    updated = models.DateTimeField(auto_now=True) # takes snapshot everytime its saved
    created = models.DateTimeField(auto_now_add=True) # only takes snapshot when saved first time
    

    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.body[0:50] # we want only first 50 messages for preview