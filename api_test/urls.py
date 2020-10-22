import myapp.views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

appname='api_test'

urlpatterns = [
    path('camera/', views.camera_kakaoproduct , name = 'cameratest'), #카메라로 찍은 사진에 해당
    path('media/', views.media_kakaoproduct, name='mediatest'),
    # path('', views.choose_search, name='search'),
    # path('camera/', views.camera, name='camera'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
