import myapp.views
import api_test.views 
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('', api_test.views.kakaoproduct , name = 'cameratest'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
