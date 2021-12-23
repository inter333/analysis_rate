from django.db import models

class Fighter(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    fighter_ja = models.CharField(max_length=100)
    fighter_en = models.CharField(max_length=100)