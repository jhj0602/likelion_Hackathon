from django.db import models

# Create your models here.
class itemsaved(models.Model):
    image = models.ImageField(upload_to='images/', blank=True)