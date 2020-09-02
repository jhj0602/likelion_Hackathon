from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class itemsaved(models.Model):  ## 스타일 저장 모델
    image = models.ImageField(upload_to='images/', blank=True)

class wear_mywear(models.Model):
    shopping_want_wear = models.ImageField(upload_to='images/shoplist',blank=True)


class CustomUser(AbstractUser):
    def __str__(self):
        return self.username
        
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)

class Post(models.Model):
    def __str__(self):
        return self.title
    title = models.CharField(max_length=200)
    top_bottom = models.TextField()#상의 하의
    content = models.TextField()#아우터#긴팔티#반팔티#반바지#긴바지
    image = models.ImageField(upload_to='images/', blank=True)#옷 사진
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="writer", default="")
    hashtag_field = models.CharField(max_length=200, blank=True)#해시태그별 스타일정리
    hashtags = models.ManyToManyField('Hashtag', blank=True)

class Hashtag(models.Model):
    def __str__(self):
        return self.related_name

    name = models.CharField(max_length=50)