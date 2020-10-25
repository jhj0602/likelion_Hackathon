from django.shortcuts import render, redirect, get_object_or_404
import sys
import os,glob
import argparse
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont ,ImageGrab
from io import BytesIO
from .models import itemsaved,wear_mywear
from matplotlib import pyplot as plt
from .models import lotteData ,CartItem # 무신사 데이터 ,장바구니
from .models import CustomUser
from django.contrib.auth import login, authenticate
import cv2
from .forms import  UserForm
from django.http import HttpResponse
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen,urlretrieve
from urllib.parse import quote_plus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Lotte_datasetApp.models import lotteData



#날씨
# Create your views here.

def base(request):
    users = CustomUser.objects.all()
    return render(request, 'myapp/base.html') 

def main2(request):
    if not request.user.is_active:
        return redirect('signin')
    else:
        users = CustomUser.objects.all()
        index = [1,1,1]
        context = {
        'users': users,
        'index':index}
        return render(request, 'myapp/main2.html',context)
    
    


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('main2')
        else:
            return render(request, 'myapp/login.html')
    else:
        return render(request, 'myapp/login.html')

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
            return redirect('main2')
    else:
        form = UserForm()
        return render(request, 'myapp/signup.html', {'form': form})


def logout(request):
    auth.logout(request)
    return redirect('signin')

def lotte_Data(searchtitle,detail_url,lotte_path,lotte_image_name,M_title,M_price,product_dir):
    lotte = lotteData()
    lotte.search_lotte =searchtitle
    lotte.lotteUrl = detail_url
    image_url = 'images/'+product_dir+lotte_image_name
    lotte.lotteImage = image_url
    lotte.lotteName = M_title
    lotte.lottePrice = M_price
    lotte.save()
    

def crowling(request):
    return render(request, 'myapp/crowling.html' )
        

def add_cart(request, product_pk):
    
	# 상품을 담기 위해 해당 상품 객체를 product 변수에 할당
    product = lotteData.objects.get(pk=product_pk)
    print(product.lotteImage)

    try:
    	# 장바구니는 user 를 FK 로 참조하기 때문에 save() 를 하기 위해 user 가 누구인지도 알아야 함
        cart = CartItem.objects.get(product=product, user=request.user)
       
        if cart:
            if cart.product.lotteName == product.lotteName:
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
    product = lotteData.objects.get(pk=product_pk)
    cart_item.delete()
    return redirect('my_cart')
    
    

#각 유저의 장바구니
def my_cart(request):
    
    cart_item = CartItem.objects.filter(user__id=request.user.pk)
    # 장바구니에 담긴 상품의 총 합계 가격
    total_price = 0
    # for loop 를 순회하여 각 상품 * 수량을 total_price 에 담는다
    for each_total in cart_item:
        total_price += each_total.product.lottePrice
    if cart_item is not None:
        context = {
        	# 없으면 없는대로 빈 conext 를 템플릿 변수에서 사용
            'cart_item': cart_item,
            'total_price': total_price,
        }
        return render(request, 'myapp/cart.html', {'cart_item': cart_item,'total_price': total_price})
    return redirect('my_cart')


def warningone(request):
    return render(request, 'myapp/warningone.html')


def warningtwo(request):
    return render(request, 'myapp/warningtwo.html')

def mypage(request):
    return render(request, 'myapp/mypage.html')

def draganddrop(request):
    if request.method == "POST":
        user = request.user
        bbox=(20,300,562,905) #x1 y1 x2 y2
        img = ImageGrab.grab(bbox)
        imagename = './{}.png'.format(user)
        img.save(imagename)
        imagename = './{}.png'.format(user)
        return redirect('main2',{'imagename':imagename})
    cart_item = CartItem.objects.all()
    return render(request, 'myapp/draganddrop.html',{'cart_item':cart_item})

def imagenaming(request,data):
    print(data)
    print("여기?")
    return data

def inform(request):
    if request.method =='POST':
        user = request.user
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username')
        new_user_pw = request.POST.get('password')
        name = request.POST.get('name')
        
        user.phone_number = phone_number
        user.username = username
        user.name = name
        user.set_password(new_user_pw)
        user.save()


        return redirect('main2')

  
    return render(request, 'myapp/inform.html')

def introduce(request):
    return render(request, 'myapp/introduce.html')








