from django.shortcuts import render, redirect
from urllib.request import urlopen,urlretrieve
from .models import lotteData
from urllib.parse import quote_plus #아스키 코드로 변환해준다

from bs4 import BeautifulSoup

from selenium import webdriver #selenium 크롤링 크롬드라이버

import time
from django.core.paginator import Paginator

def lotte_Data(searchtitle,lotte_image_name,buyurl,Lottetitle,Lotteprice,product_dir,category):
  
    lotte = lotteData()
    if category == "아우터":
        category = "outer"
    elif category == "백팩":
        category = "backpack"
    elif category == "캐리어":
        category = "baggage"
    elif category == "모자":
        category = "hat"
    elif category == "원피스":
        category = "one-piece"
    elif category == "바지":
        category = "pants"
    elif category == "신발":
        category = "shoes"
    elif category == "샌달":
        category = "sandals"
    elif category == "셔츠":
        category = "shirts"
    elif category == "치마":
        category = "skirt"
    elif category == "티셔츠":
        category = "t-shirts"
    elif category == "토트백":
        category = "tote bag"
    lotte.category = category
    lotte.search_lotte =searchtitle#검색어
    lotte.lotteUrl = buyurl #구매 페이지
    image_url = 'images/'+product_dir+lotte_image_name
    lotte.lotteImage = image_url #이미지 저장 경로
    lotte.lotteName = Lottetitle #제목
    lotte.lottePrice = Lotteprice #가격
    lotte.save()


def lotteproduct(request):
    if request.method =='POST':
        gender = request.POST['search']
        product_dir = str('tote bag'+'/')
        baseUrl1 = '&page='
        baseUrl = 'https://www.lotteon.com/search/search/search.ecn?render=search&platform=pc&q='
        search_Image = "토트백"
        plusUrl = "토트백"
        category = search_Image
       
        url = baseUrl + quote_plus(plusUrl) + baseUrl1 + str(1)

        driver = webdriver.Chrome('chromedriver.exe')

        driver.get(url)

        time.sleep(3)  # 위에서 불러오고 1초 기다린후에 분석을 시작



        pageString = driver.page_source

        soup = BeautifulSoup(pageString, features="html.parser")

        LotteProductList = soup.find(name = 'ul', attrs ={'class':'srchProductList'}) #롯데 상품리스트

        Lotteimageurl = LotteProductList.find_all("div", class_ = "srchThumbImageWrap") #이미지 URL
        Lottebuyurl = LotteProductList.find_all("div",class_="srchProductUnitImageArea")
        # print(Lottebuyurl)
        Lottetitle = LotteProductList.find_all("div",class_="srchProductUnitTitle")
        # print(Lottetitle)
        Lotteprice = LotteProductList.find_all("div", class_="srchProductUnitPriceArea")
        n=1
        for i,b,t,p in zip(Lotteimageurl,Lottebuyurl,Lottetitle,Lotteprice):

            # try:
            print(str(n)+"번째")

            image = i.select_one("img")
            image2 = image.attrs['src']
            print("이미지"+str(image2))

            lotte_image_name =str(n) +'.jpg'#이미지 이름
            buyurl = b.select_one("a")
            buyurl2 = buyurl.attrs['href']
            print("구매링크"+str(buyurl2))

            Lottetitle = t.get_text()
            print("상품 이름"+str(Lottetitle))


            Lotteprice = p.select_one("span.srchCurrentPrice").get_text()
            print("가격"+str(Lotteprice).replace(',','')[:-1])
            Lotteprice2 = str(Lotteprice).replace(',','')[:-1]
            Lotteprice3 = int(Lotteprice2)
            print()
            # lotte_path = 'media/images/'
            searchtitle = search_Image+str(n)#검색어

            urlretrieve(image2,'media/images/'+product_dir + lotte_image_name)
        
            lotte_Data(searchtitle,lotte_image_name,buyurl2,Lottetitle,Lotteprice3,product_dir,category)
          
            n=n+1
            # except:
            #     print('media/images/'+product_dir + lotte_image_name)
            #     continue
        driver.close()


    lotte = lotteData.objects.all()
    paginator = Paginator(lotte,3)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request, 'Lotte_datasetApp/lotteproduct.html',{ 'lotteposts' : lotteposts })

def lowprice(request):#낮은 가격순
    lotte = lotteData.objects.all().order_by('lottePrice')
    paginator = Paginator(lotte,3)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request, 'Lotte_datasetApp/lotteproduct.html',{ 'lotteposts' : lotteposts })


def highprice(request):#높은 가격순
    lotte = lotteData.objects.all().order_by('-lottePrice')
    paginator = Paginator(lotte,3)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request, 'Lotte_datasetApp/lotteproduct.html',{ 'lotteposts' : lotteposts })


#    for i in range(1,6):

#     lotteproduct(i) #수현이가 말한 크롤링 함수 반복문


def search(request):
    q= request.GET['q']
    if q:
        lotteposts = lotteData.objects.filter(lotteName__icontains=q).order_by('-id')
    else:
        return redirect('search')

    paginator = Paginator(lotteposts,20)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request,'Lotte_datasetApp/search.html', {'lotteposts':lotteposts,'q':q} )

def searchlowprice(request,s_data):#낮은 가격순
    print(s_data)
    q= s_data
    print("되나용 씹ㄹ란여")
    if q:
        lotteposts = lotteData.objects.filter(lotteName__icontains=q).order_by('lottePrice')
    else:
        return redirect('search')
   
    paginator = Paginator(lotteposts,20)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request, 'Lotte_datasetApp/search.html',{ 'lotteposts' : lotteposts ,'q':q})


def searchhighprice(request,s_data):#높은 가격순
    q= s_data
    if q:
        lotteposts = lotteData.objects.filter(lotteName__icontains=q).order_by('-lottePrice')
    else:
        return redirect('search')

    paginator = Paginator(lotteposts,20)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return render(request, 'Lotte_datasetApp/search.html',{ 'lotteposts' : lotteposts ,'q':q})


def save_test():
    # Celery로 비동기적으로 30초마다 모델이 저장되는 지 확인하기 위함
    temp_lt_data = lotteData()
    temp_lt_data.search_lotte = 'Test'
    # lotteImage = 이미지는 없이 저장
    temp_lt_data.lotteUrl = 'Test'
    temp_lt_data.lotteName = 'Test'
    temp_lt_data.lottePrice = 'Test'
    temp_lt_data.category = 'Test'
    temp_lt_data.save()

