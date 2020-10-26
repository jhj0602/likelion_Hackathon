from django.shortcuts import render, redirect, get_object_or_404,reverse
import sys
import os,glob
import argparse
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from myapp.models import itemsaved,wear_mywear
from matplotlib import pyplot as plt
from myapp.models import CustomUser
from django.contrib.auth import login, authenticate
import cv2
from myapp.forms import  UserForm
from .forms import MediaForm
from django.http import HttpResponse
# Create your views here.

def detect_product(image):
    headers = {'Authorization': 'KakaoAK {}'.format("1b93fbec9c5f4fdefb40d20a47f2e888")}
    print(type(image))

    try:
        files = {'image' : open(image,"rb")}
        resp = requests.post('https://dapi.kakao.com/v2/vision/product/detect', headers=headers, files=files)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(str(e))
        sys.exit(0)

def show_products(image_url, detection_result):
    image = image_url
    image_list = []
    image_path_list=[]
    draw = ImageDraw.Draw(image)
    classname_list = []
    for obj in detection_result['result']['objects']:
        x1 = int(obj['x1']*image.width)
        y1 = int(obj['y1']*image.height)
        x2 = int(obj['x2']*image.width)
        y2 = int(obj['y2']*image.height)
        draw.rectangle([(x1,y1), (x2, y2)], fill=None, outline=(255,0,0,255))
        draw.text((x1+5,y1+5), obj['class'], (255,0,0))
        classname_list.append(obj['class'])
        area = (x1,y1,x2,y2)
        croped_image = image.crop(area)
        image_list.append(croped_image)
        image_path = 'media/images/temp/' + str(obj['class']) + '.jpeg'
        image_path_list.append(image_path)
        croped_image.save(image_path)
        # croped_image.show() #내컴퓨터에서 사진파일 실행
    del draw


    return image_path_list,classname_list # 지금 경로리턴하게 바꿈 원래는 image그 자체를 반환함.

def camera_kakaoproduct(request):
    image_name = camera()
    detection_result = detect_product(image_name)
    image_name = Image.open(image_name)
    image = show_products(image_name, detection_result)
    print("여기?")
    print(image)
    return redirect('imagecut',image)

def media_kakaoproduct(request):
    if request.method=="POST":
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.image.name = request.user.username + '.jpg'
            image_name = form.image.name
            print(image_name)
            form.save()
            print(image_name) 
            # image_name = "media/images/temp/opencv_frame_0.png"  # 여기에 카메라로 찍은 사진이 들어옴
            # image_name = 'media/'+image_name
            image_name = 'media/images/temp/'+image_name
            detection_result = detect_product(image_name)
            print('여긴가?')
            image_name = Image.open(image_name)
            image = show_products(image_name, detection_result)
            
            return redirect('imagecut',image)
    else:
        form = MediaForm()
        return render(request, 'api_test/media.html',{'form':form})

def camera():
    cam = cv2.VideoCapture(0)
    # cv2.namedWindow("please see front of camera")
    img_counter = 0
    while True:
        ret, frame = cam.read()
        cv2.imshow("test", frame)
        if not ret:
            break
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = 'media/images/temp/'+"opencv_frame_0.jpeg" # user이름을 이름에 넣자
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            break
    cam.release()
    cv2.destroyAllWindows()
    return img_name



# def choose_search(request):
#     if request.method == "POST":
#         temp_image = MediaForm(request.POST,request.FILES)
#         if temp_image.is_valid():
#             temp_image= temp_image.save(commit=False)
#             temp_image.username = request.user
#             # temp_image.image =str(request.user)+".jpg"
#             temp_image= temp_image.save()
#             return redirect('mediatest',request.user.pk)
#     blank_media = MediaForm()    
#     return render(request, 'api_test/search.html',{'mediaform':blank_media})

# def content_file_name(instance, filename):
#     filename = "%s.jpg" % (instance.user.pk)
#     return os.path.join('uploads', filename)