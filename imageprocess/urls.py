from django.contrib import admin
from django.conf import settings
import myapp.views
import imageprocess.views
import api_test.urls
import deeplearning.urls
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('', imageprocess.views.imagecutter, name='imagecut'),
    path('avhash/', imageprocess.views.avhash, name='avhash'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)