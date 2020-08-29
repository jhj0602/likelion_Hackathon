from django.shortcuts import render,get_object_or_404
import sys
import os,glob
import argparse
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .models import itemsaved
from matplotlib import pyplot as plt

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
    print(image_url)
    image_url = 'images/'+name
    blank_model.image = image_url
    blank_model.save()


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
        image_resp = requests.get('https://newsimg.sedaily.com/2018/07/22/1S26NWYDVG_1.jpg')
        image_resp.raise_for_status()
        file_jpgdata = BytesIO(image_resp.content)
        image = Image.open(file_jpgdata)
    except Exception as e:
        print(str(e))
        sys.exit(0)


    draw = ImageDraw.Draw(image)
    for obj in detection_result['result']['objects']:
        x1 = int(obj['x1']*image.width)
        y1 = int(obj['y1']*image.height)
        x2 = int(obj['x2']*image.width)
        y2 = int(obj['y2']*image.height)
        draw.rectangle([(x1,y1), (x2, y2)], fill=None, outline=(255,0,0,255))
        draw.text((x1+5,y1+5), obj['class'], (255,0,0))
    del draw



    print(image.format)
    # image.thumbnail((600,600))
    image_path = 'media/images/'
    image_name = str(itemsaved.objects.all().count())+'.jpeg'
    image_path = image_path + image_name
    image.save(image_path)
    item_save(image_path,image_name)
    return image

def kakaoproduct(request):
    parser = argparse.ArgumentParser(description='Detect Products.')
    parser.add_argument('https://newsimg.sedaily.com/2018/07/22/1S26NWYDVG_1.jpg', type=str, nargs='?',
        default="http://t1.daumcdn.net/alvolo/_vision/openapi/r2/images/06.jpg",
        help='image url to show product\'s rect')

    args = parser.parse_args()
    print(args)

    detection_result = detect_product("https://newsimg.sedaily.com/2018/07/22/1S26NWYDVG_1.jpg")
    image = show_products("https://newsimg.sedaily.com/2018/07/22/1S26NWYDVG_1.jpg", detection_result)
    print(type(image))
    image.show()
    item_all = itemsaved.objects.all()
    return render(request, 'myapp/kakaoproduct.html',{'item_all':item_all})