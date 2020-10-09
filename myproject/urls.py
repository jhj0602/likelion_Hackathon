"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
import myapp.views
import api_test.urls
import deeplearning.urls
import imageprocess.urls
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin', myapp.views.signin, name = 'signin'),
    path('signup', myapp.views.signup, name = 'signup'),
    path('', myapp.views.main, name = 'main'),
  
    path('kakaoproduct', myapp.views.kakaoproduct, name = 'kakaoproduct'),
    path('camera', myapp.views.camera, name='camera'),
    path('captureimage', myapp.views.captureimage, name='captureimage'),
    path('', include('django.contrib.auth.urls')),
    path('apitest/', include('api_test.urls')),
    path('deep/', include('deeplearning.urls')),
    path('imageprocess/', include('imageprocess.urls')),
    
    #크롤링 부분
    path('crowling', myapp.views.crowling, name='crowling'),
    #장바구니 부분
    path('my_cart', myapp.views.my_cart, name = 'my_cart'),
    path('add_cart/<int:product_pk>', myapp.views.add_cart, name='add_cart'),
    path('delete_cart_item/<int:product_pk>', myapp.views.delete_cart_item, name='delete_cart_item'),
    
    #마이페이지
    path('mypage', myapp.views.mypage, name='mypage'),
    path('mypage_drag', myapp.views.mypage_drag, name='mypage_drag'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
