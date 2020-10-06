from django.shortcuts import render, redirect, get_object_or_404
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
from django.http import HttpResponse
# Create your views here.

def item_save(image_url,name):
    blank_model = itemsaved()
    image_url = 'images/'+name
    blank_model.image = image_url
    blank_model.save()

def item_list_save(image_url,name):
    blank_search_model = wear_mywear()
    image_url = 'images/shoplist/'+name
    blank_search_model.shopping_want_wear = image_url
    blank_search_model.save()


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
    try:
        image = Image.open("media/images/temp/opencv_frame_0.png")
    except Exception as e:
        print(str(e))
        sys.exit(0)

    image_list = []
    draw = ImageDraw.Draw(image)
    for obj in detection_result['result']['objects']:
        x1 = int(obj['x1']*image.width)
        y1 = int(obj['y1']*image.height)
        x2 = int(obj['x2']*image.width)
        y2 = int(obj['y2']*image.height)
        draw.rectangle([(x1,y1), (x2, y2)], fill=None, outline=(255,0,0,255))
        draw.text((x1+5,y1+5), obj['class'], (255,0,0))
        area = (x1,y1,x2,y2)
        croped_image = image.crop(area)
        image_list.append(croped_image)
        croped_image.show() #내컴퓨터에서 사진파일 실행
        
    del draw

    

    image_path = 'media/images/'
    image_name = str(itemsaved.objects.all().count())+'.jpeg'
    image_path = image_path + image_name
    image.save(image_path)
    item_save(image_path,image_name)
    return image

def kakaoproduct(request):
    image_name = "media/images/temp/opencv_frame_0.png"  # 여기에 카메라로 찍은 사진이 들어옴
    detection_result = detect_product(image_name)
    image_name = Image.open(image_name)
    image = show_products(image_name, detection_result)
    image.show()
    item_all = itemsaved.objects.all()
    search_list_all = wear_mywear.objects.all()
    return render(request, 'myapp/kakaoproduct.html',{'item_all':item_all, 'item_list':search_list_all})

def camera():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("사진을 찍어주세요.")
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
            img_name = 'media/images/temp/'+"opencv_frame_0.png" # user이름을 이름에 넣자
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
            break
    cam.release()
    cv2.destroyAllWindows()
    return redirect('kakaoproduct',img_name)

def captureimage(request):
    return render(request, 'myapp/camera.html')