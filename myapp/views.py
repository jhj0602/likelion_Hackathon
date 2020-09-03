from django.shortcuts import render,get_object_or_404
import sys
import os,glob
import argparse
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .models import itemsaved,wear_mywear
from matplotlib import pyplot as plt
import cv2

# Create your views here.
def homelogin(request):
    return render(request, 'myapp/homelogin.html')

def mypage(request):
    return render(request, 'myapp/mypage.html')

def myportfolio(request):
    return render(request, 'myapp/myportfolio.html')




def create(request):
    return render(request, 'myapp/create.html')


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


def detect_product(image_url):
    headers = {'Authorization': 'KakaoAK {}'.format("1b93fbec9c5f4fdefb40d20a47f2e888")}

    try:
        data = { 'image_url' : image_url}
        resp = requests.post('https://dapi.kakao.com/v2/vision/product/detect', headers=headers, data=data)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(str(e))
        sys.exit(0)

def show_products(image_url, detection_result):
    try:
        image_resp = requests.get(image_url)
        image_resp.raise_for_status()
        file_jpgdata = BytesIO(image_resp.content)
        print(file_jpgdata)
        image = Image.open(file_jpgdata)
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
        croped_image.show()
        
    del draw



    
    for x in image_list:
        image_path = 'media/images/shoplist/'
        image_name = str(wear_mywear.objects.all().count())+'.jpeg'
        image_path = image_path + image_name
        x.save(image_path)
        item_list_save(image_path,image_name)

    image_path = 'media/images/'
    image_name = str(itemsaved.objects.all().count())+'.jpeg'
    image_path = image_path + image_name
    image.save(image_path)
    item_save(image_path,image_name)
    return image

def kakaoproduct(request):
    parser = argparse.ArgumentParser(description='Detect Products.')
    image_url_home = 'https://th.bing.com/th/id/OIP.NbJQhkLhgAHlnqDIAbqDwQHaHa?w=196&h=196&c=7&o=5&dpr=1.25&pid=1.7'
    parser.add_argument(image_url_home, type=str, nargs='?',
        default="http://t1.daumcdn.net/alvolo/_vision/openapi/r2/images/06.jpg",
        help='image url to show product\'s rect')

    args = parser.parse_args()
    print(args)

    detection_result = detect_product(image_url_home)
    image = show_products(image_url_home, detection_result)
    image.show()
    item_all = itemsaved.objects.all()
    search_list_all = wear_mywear.objects.all()
    return render(request, 'myapp/kakaoproduct.html',{'item_all':item_all, 'item_list':search_list_all})

def camera(request):
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("test")
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
            img_name = 'media/images/temp/'+"opencv_frame_0.png"
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            img_counter += 1
    cam.release()
    cv2.destroyAllWindows()
    return render(request,'myapp/camera.html',{'image_name':img_name})

def captureimage(request):
    return render(request, 'myapp/camera.html')













