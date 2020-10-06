
from django.conf import settings
import deeplearning.views
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('', deeplearning.views.learning, name = 'learning'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)