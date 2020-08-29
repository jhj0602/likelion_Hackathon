from django.db import models

# Create your models here.
class itemsaved(models.Model):  ## 스타일 저장 모델
    image = models.ImageField(upload_to='images/', blank=True)

class wear_mywear(models.Model):
    shopping_want_wear = models.ImageField(upload_to='images/shoplist',blank=True)