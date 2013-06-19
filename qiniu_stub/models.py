from django.db import models

class Credential(models.Model):
    access = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)

class Key(models.Model):
    name = models.CharField(max_length=255)
    size = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)

