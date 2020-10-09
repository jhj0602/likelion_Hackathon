from django.shortcuts import render, redirect, get_object_or_404
import sys
import os,glob
import argparse
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .models import itemsaved,wear_mywear
from matplotlib import pyplot as plt
from .models import musinsaData ,CartItem # 무신사 데이터 ,장바구니
from .models import CustomUser
from django.contrib.auth import login, authenticate
import cv2
from .forms import  UserForm
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen,urlretrieve
from urllib.parse import quote_plus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




#날씨
# Create your views here.

def base(request):
    users = CustomUser.objects.all()
    return render(request, 'myapp/base.html') 

def main(request):
    if not request.user.is_active:
        return redirect('signin')
    else:
        users = CustomUser.objects.all()
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=1acc16a96aa8764e33997f3c2ac1a09c'
        city = 'busan'
        city_weather = requests.get(url.format(city)).json() #request the API data and convert the JSON to Python data types
        weather = {
            'city' : city,
            'temperature' : round((city_weather['main']['temp'] - 32)/1.8,1),
            'description' : city_weather['weather'][0]['description'],
            'icon' : city_weather['weather'][0]['icon']
        }
        context = {'weather' : weather,
        'users': users}
        
        return render(request, 'myapp/main2.html',context)
    
    


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'myapp/signin.html')
    else:
        return render(request, 'myapp/signin.html')

def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = CustomUser.objects.create_user(username=form.cleaned_data['username'],
            password = form.cleaned_data['password'],
            name = form.cleaned_data['name'],
            address = form.cleaned_data['address'],
            phone_number = form.cleaned_data['phone_number'],
            gender = form.cleaned_data['gender'])
            login(request, new_user)
            return redirect('main')
    else:
        form = UserForm()
        return render(request, 'myapp/signup.html', {'form': form})


def logout(request):
    auth.logout(request)
    return redirect('main')

def musinsa_Data(searchtitle,detail_url,musinsa_path,musinsa_image_name,M_title,M_price,product_dir):
    musin = musinsaData()
    musin.search_musinsa =searchtitle
    musin.musinsaUrl = detail_url
    image_url = 'images/'+product_dir+musinsa_image_name
    musin.musinsaImage = image_url
    musin.musinName = M_title
    musin.musinPrice = M_price
    musin.save()
    

def crowling(request):
    if request.method =='POST':
        search_Image = request.POST['search']
        product_dir = str(search_Image+'/')
       
        baseUrl = 'https://store.musinsa.com/app/product/search?search_type=1&q='
        counting_search =2
        plusUrl = search_Image
        crawl_num = counting_search
        
        url = baseUrl + quote_plus(plusUrl) # 한글 검색 자동 변환
        html = urlopen(url)

        soup = bs(html, "html.parser")
        
        
        img = soup.find_all(class_='lazyload lazy')
        title = soup.find_all(class_='list_info')
        price = soup.find_all(class_='price')
        
        # print(img)
        n = 1
        urlist=[]
        for i,t,p in zip(img,title,price):#이미지 , 상품 이름 , 상품 가격  변수
            
            
            #상품 가격 가져오는 구문 :  문자열 html 코드 가격이외에 자르는 처리 코드
            pp = str(p).replace(',','')
            tmp = []
            ttt = False
            for char in pp:
                if char.isdigit():
                    if not ttt:
                        ttt = True
                        ts = char
                    else:
                        ts+=char
                elif ttt:
                    tmp.append(ts)
                    ttt = False
          
            if len(tmp) >1:
                M_price = str(tmp[1]+"원")
            else:
                M_price =str(tmp[0]+"원")
                
        
            a=t.select_one("p > a")#상품명 html태그에 title속성 가져오기
            M_title = a['title']#상품명 출력
            
            imgUrl = i['data-original']#이미지 속성 data-original
            urllist = imgUrl.split('/')
            musinsa_image_name =str(urllist[6]) +'.jpg'#이미지 이름
            urlretrieve("http:"+imgUrl,'media/images/'+product_dir + musinsa_image_name)
            searchtitle = search_Image+str(n)#검색어 
            detail_url =  "https://store.musinsa.com/app/product/detail/"+urllist[6]
            musinsa_path = 'media/images/' #이미지 저장할 경로
            musinsa_Data(searchtitle,detail_url,musinsa_path,musinsa_image_name,M_title,M_price,product_dir)
            
            
            n += 1
            if n > crawl_num:
                break
    
    musinsa = musinsaData.objects.all().order_by('-id')
    return render(request, 'myapp/crowling.html',{'musinsa': musinsa } )
        

def add_cart(request, product_pk):
	# 상품을 담기 위해 해당 상품 객체를 product 변수에 할당
    product = musinsaData.objects.get(pk=product_pk)

    try:
    	# 장바구니는 user 를 FK 로 참조하기 때문에 save() 를 하기 위해 user 가 누구인지도 알아야 함
        cart = CartItem.objects.get(product__id=product.pk, user__id=request.user.pk)
        if cart:
            if cart.product.musinName == product.musinName:
                cart.quantity += 1
                cart.save()
    except CartItem.DoesNotExist:
        user = CustomUser.objects.get(pk=request.user.pk)
        cart = CartItem(
            user=user,
            product=product,
            quantity=1,
        )
        cart.save()
    return redirect('my_cart')
     
def delete_cart_item(request, product_pk):
    
    cart_item = CartItem.objects.filter(product__id=product_pk)
    product = musinsaData.objects.get(pk=product_pk)
    cart_item.delete()
    return redirect('my_cart')
    
    

#각 유저의 장바구니
def my_cart(request):
    
    cart_item = CartItem.objects.filter(user__id=request.user.pk)
    # 장바구니에 담긴 상품의 총 합계 가격
    # total_price = 0
    # for loop 를 순회하여 각 상품 * 수량을 total_price 에 담는다
    # for each_total in cart_item:
    #     total_price += each_total.product.price * each_total.quantity
    if cart_item is not None:
        context = {
        	# 없으면 없는대로 빈 conext 를 템플릿 변수에서 사용
            'cart_item': cart_item,
            # 'total_price': total_price,
        }
        return render(request, 'myapp/cart.html', {'cart_item': cart_item,})
    return redirect('my_cart')










def mypage(request):
    
    return render(request, 'myapp/mypage.html')

def mypage_drag(request):
    cart_item = CartItem.objects.all().order_by('-id')
    return render(request, 'myapp/mypage_drag.html',{'cart_item': cart_item})

def draganddrop(request):
    cart_item = CartItem.objects.all().order_by('-id')
    return render(request, 'myapp/draganddrop.html',{'cart_item': cart_item})


