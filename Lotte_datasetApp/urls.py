
from django.conf import settings
import Lotte_datasetApp.views
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    # path('llcrolling/', Lotte_datasetApp.views.lotteproduct, name = 'lottecrolling'),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)