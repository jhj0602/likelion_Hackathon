from django.shortcuts import render,redirect
import os, re
import numpy as np
import cv2
from PIL import Image
from Lotte_datasetApp.models import lotteData
import matplotlib.pyplot as plt

mouse_is_pressing = False
points = []




def imagecutter(request,image): #모든 크롤링 데이터에 대해 적용해야함. 이미지 전처리 함수를 만들엇음
    step = 0
    global points

    def distanceBetweenTwoPoints(point1, point2):
        
        x1,y1 = point1
        x2,y2 = point2
        
        return int(np.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2)))


    def mouse_callback(event,x,y,flags,param):
        
        global mouse_is_pressing
        global points
        # print(mouse_is_pressing)
        # print(points)
        

        if step != 1:
            return

        if event == cv2.EVENT_MOUSEMOVE: 
            if mouse_is_pressing == True: 

                for i,point in enumerate(points):
                    if distanceBetweenTwoPoints((x,y), point) < 15:
                        points[i][0] = x
                        points[i][1] = y
                        break    
            
        elif event == cv2.EVENT_LBUTTONDOWN:
        
            for point in points:
                if distanceBetweenTwoPoints((x,y), point) < 10:
                    mouse_is_pressing = True
                    break

        elif event == cv2.EVENT_LBUTTONUP: 

            mouse_is_pressing = False


    def angle_between(v0, v1):
        
        angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))

        return np.degrees(angle)


    def sort_points(points):

        points = points.astype(np.float32)

        rect = np.zeros((4, 2), dtype = "float32")
    
        # sort : top left, top right, bottom right, bottom left
        s = points.sum(axis = 1)
        min_index = np.argmin(s)
        rect[0] = points[min_index]
        points = np.delete(points, min_index, axis = 0)

        s = points.sum(axis = 1)
        max_index = np.argmax(s)
        rect[2] = points[max_index]
        points = np.delete(points, max_index, axis = 0)

        v0 = points[0] - rect[0]
        v1 = points[1] - rect[0]

        angle = angle_between(v0, v1)

        if angle < 0:
            rect[1] = points[1]
            rect[3] = points[0]
        else:
            rect[1] = points[0]
            rect[3] = points[1]
    
        return rect


    def transform(img_input, points):

        points = sort_points(points)
        topLeft, topRight, bottomRight, bottomLeft = points
    
        topWidth = distanceBetweenTwoPoints(bottomLeft, bottomRight)
        bottomWidth = distanceBetweenTwoPoints(topLeft, topRight)
        maxWidth = max(int(topWidth), int(bottomWidth))
    
        leftHeight = distanceBetweenTwoPoints(topLeft, bottomLeft)
        rightHeight = distanceBetweenTwoPoints(topRight, bottomRight)
        maxHeight = max(int(leftHeight), int(rightHeight))
    
        # top left, top right, bottom right, bottom left
        dst = np.array([[0, 0],[maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],[0, maxHeight - 1]], dtype = "float32")
    

        H = cv2.getPerspectiveTransform(points, dst)
        img_warped = cv2.warpPerspective(img_input, H, (maxWidth, maxHeight))
    
        return img_warped


    def findMaxArea(contours):
        
        max_contour = None
        max_area = -1


        for contour in contours:
            area = cv2.contourArea(contour)

            x,y,w,h = cv2.boundingRect(contour)

            if area > max_area:
                max_area = area
                max_contour = contour


        return max_area, max_contour


    def process(img_input, debug):

        points = []
        height,width =img_input.shape[:2]

        # Step 1    
        img_mask = np.zeros(img_input.shape[:2],np.uint8)

        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)

        rect = (10,10,width-30,height-30)
        cv2.grabCut(img_input, img_mask, rect, bgdModel,fgdModel,3,cv2.GC_INIT_WITH_RECT)
        img_mask = np.where((img_mask==2)|(img_mask==0), 0, 1).astype('uint8')
        img = img_input*img_mask[:,:,np.newaxis]

        background = img_input - img

        background[np.where((background >= [0,0,0]).all(axis = 2))] = [0,0,0]

        img_grabcut = background + img

        if debug:
            cv2.imshow('grabCut', img_grabcut)


        # Step 2
        img_gray = cv2.cvtColor(img_grabcut, cv2.COLOR_BGR2GRAY)
        img_canny = cv2.Canny(img_gray, 30, 90)

        if debug:
            cv2.imshow('Canny', img_canny)


        # Step 3
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        img_canny = cv2.morphologyEx(img_canny, cv2.MORPH_CLOSE, kernel, 1)

        if debug:
            cv2.imshow('morphology', img_canny)


        # Step 4
        contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        max_area, max_contour = findMaxArea(contours) 
        if max_area < 0:
            return points
        
        if debug:
            img_contour = img_input.copy()
            cv2.drawContours(img_contour, [max_contour], 0, (0, 0, 255), 3)
            cv2.imshow('Contour', img_contour)


        # Step 5
        max_contour = cv2.approxPolyDP(max_contour,0.02*cv2.arcLength(max_contour,True),True)
        hull = cv2.convexHull(max_contour)

        if debug:
            img_convexhull = img_input.copy()
            cv2.drawContours(img_convexhull, [hull], 0, (255,255,0), 5)
            cv2.imshow('convexHull', img_convexhull)


        # Step 6
        size = len(max_contour)

        if size == 4:
            for c in hull:
                points.append(tuple(c[0].tolist()))
                points=np.array(points)
        else:
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            points = np.int0(box.tolist())

        found = False
        for p in points:
            if p[0] < 0 or p[0] > width-1 or p[1] < 0 or p[1] > height -1:
                found = True  
                break

        if found:
            points = np.array([[10,10], [width-11, 10], [width-11, height-11], [10, height-11]])

        return points
        

    def channel_cut(image):
        # 3-channel image (no transparency)
        if image.shape[2] == 3:
            b,g,r = cv2.split(image)
            image[:,:,0] = r
            image[:,:,1] = g
            image[:,:,2] = b
        # 4-channel image (with transparency)
        elif image.shape[2] == 4:
            b,g,r,a = cv2.split(image)
            image[:,:,0] = r
            image[:,:,1] = g
            image[:,:,2] = b
        return image 

    
    print(image)
    image=image.split("'")
    path_list =[]
    image_count = 0 #저장된 이미지 개수
    image_class_count=0 # 이미지 클래스 매칭할때 변수
    is_empty = True
    class_list = []
    class_str = ""
    p = re.compile('[a-zA-Z]')
    for x in image:
        if "media" in x:
            path_list.append(x)
            is_empty=False
            print(is_empty)
        else:
            if p.match(x) is not None:
                class_list.append(x)
                class_str+=x +','
                print(is_empty)
    print(is_empty)
    if is_empty:
        return render(request,'imageprocess/warningtwo.html')

    for i in range(len(path_list)):
        image = plt.imread(path_list[i]) #os.walk로 이제 모든 애들 끌고오면 될듯
        pixels = np.array(image) # numpy 배열로 변환하기
        cut = channel_cut(pixels)
        # img = Image.open('sss.jpg')# 이미지 데이터 열기
        # img = img.convert('RGB')
        # pixel_data = swapped.getdata() #픽셀데이터 가져오기
        pixels = np.array(cut) # numpy 배열로 변환하기
        img_input = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
        height, width = img_input.shape[:2]

        points = process(img_input, debug=False)

        size = len(points)

        if size > 0:
            cv2.namedWindow('input')
            cv2.setMouseCallback("input", mouse_callback, 0);  

            step = 1


            while True:

                img_result = img_input.copy()
                for point in points:
                    cv2.circle(img_result, tuple(point), 10, (255,0,0), 3 )    
                cv2.imshow('input', img_result)

                key = cv2.waitKey(1)
                if key % 256 == 32:
                    break
            cv2.destroyAllWindows()


            img_final = transform(img_input, points )

            im = Image.fromarray(img_final)
            userimage_name="media/images/temp/{}/{}.jpg".format(class_list[i],image_count)
            print(userimage_name + "저장되었습니다.")
            im.save(userimage_name)
            image_count+=1

        else:
            print("여긴가?")
            cv2.imshow('input', img_input)

            cv2.waitKey(0)

            cv2.destroyAllWindows()
    return redirect('avhash',int(image_count),class_str,1)

def avhash(request,image_count,class_list,sort=1):
    kim = image_count
    soo = class_list

    class_list=class_list.split(',')
    
    class_list.pop() # 마지막 새끼 제거
    search_list = []
    address = []
    pricelist = []
    namelist =[]
    k=[]
    for x in class_list:
        if sort==1:
            k = lotteData.objects.filter(category=x).order_by('lottePrice')
        elif sort==2:
            k = lotteData.objects.filter(category=x).order_by('-lottePrice')
        search_list.append(k)
        img_list = k.values_list('lotteImage',flat = True)
    
    #img_list에는 지금 애들 정확히 lotteImage값 들감
    #img_list[0] == images/남성/t-shirts/1.jpg
    print(k)
    print(class_list) #카테고리 프린트
    search_dir = "media/images/{}".format(class_list[0])
    print(search_dir)
    cache_dir = "imageprocess/imagecache/{}".format(class_list[0])
    print(cache_dir)
    

    def average_hash(fname, size=16):
        fname2 = os.path.basename(fname)
        #이미지 캐시하기
        print(fname2)
        cache_file = cache_dir + fname2.replace('\\', "/")+".csv"
        # cache_file = cache_dir +fname2+".csv"
        print(cache_file)
        
        if not os.path.exists(cache_file):
            img = Image.open(fname)
            img = img.convert('L').resize((size,size), Image.ANTIALIAS)
            pixels = np.array(img.getdata()).reshape((size,size))
            avg = pixels.mean()
            px = 1 * (pixels > avg)
            np.savetxt(cache_file, px , fmt ="%.0f", delimiter=",")
        else:
            px = np.loadtxt(cache_file, delimiter=",")
            
        return px

    # 해밍거리 구하기
    def hamming_dist(a,b):
        aa = a.reshape(1,-1)
        ab = b.reshape(1,-1)
        dist = (aa != ab).sum()
        return dist


    def addressfilter(fname):
        return fname



    # hsv 거리 구하기
    def hsv_dist(b):
        color_temp = []

        for a,x in b:
            if (a >0 and a<10) or (a>165 and a<180):
                color_temp.append("빨강")
                    
            elif (a>10 and a< 25):
                color_temp.append("주황")
            elif (a>25 and a< 35):
                color_temp.append("노랑")
            elif (a>35 and a< 80):
                color_temp.append("초록")
            elif (a>80 and a< 95):
                color_temp.append("하늘")
            elif (a>95 and a< 110):
                color_temp.append("파랑")
            elif (a>110 and a<130):
                color_temp.append("진한파랑")
            elif (a>130 and a<145):
                color_temp.append("보라")
            elif (a>145 and a<165):
                color_temp.append("핑크")
        return color_temp
        aa = a.reshape(1,-1)
        ab = b.reshape(1,-1)
        dist = (aa != ab).sum()
        return dist

    def hsv_color_dist(fname):
        fname2 = os.path.basename(fname)
        #이미지 캐시하기
        print(fname2)
        cache_file = cache_dir + fname2.replace('\\', "/")+"hsv"+".csv"
        # cache_file = cache_dir +fname2+".csv"
        print(cache_file)
        if not os.path.exists(cache_file):
            print(fname)
            img = cv2.imread(fname, cv2.IMREAD_COLOR)
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h,s,v = cv2.split(img_hsv)
            hsv_dict = {}
            color = []
            h, cnts = np.unique(h,return_counts=True)
            hsv_dict = dict(zip(h,cnts))
            hsv_dict = sorted(hsv_dict.items(), key=(lambda x:x[1]), reverse=True)
            for x in range(5):
                color.append(hsv_dict[x])
            return color # 여기에 파일 입출력으로 캐시파일 만들기
            # np.savetxt(cache_file, px , fmt ="%.0f", delimiter=",")
        else:
            img = cv2.imread(fname, cv2.IMREAD_COLOR)
            print(fname)
            print("hsv 왜 안먹는데")
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h,s,v = cv2.split(img_hsv)
            hsv_dict = {}
            color = []
            h, cnts = np.unique(h,return_counts=True)
            hsv_dict = dict(zip(h,cnts))
            hsv_dict = sorted(hsv_dict.items(), key=(lambda x:x[1]), reverse=True)
            print(hsv_dict)
            for x in range(5):
                color.append(hsv_dict[x])
            print(color)
            return color
            # px = np.loadtxt(cache_file, delimiter=",") # 캐시파일 불러오기
            
        # return px
        
        return "빈도가 제일 높은 hsv 칼라 특히 h"
    # 모든 폴더에 처리 적용하기
    def enum_all_files(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                fname = os.path.join(root,f)
                if re.search(r'\.(jpg|jpeg|png)$', fname):
                    fname =fname.replace('media/','')
                    fname =fname.replace('\\','/')
                    yield fname
    # 이미지 찾기                
    def find_image(fname, rate,categogo):
        src = average_hash(fname)
        color = hsv_color_dist(fname)
        color_korea=hsv_dist(color)
        print(set(color_korea))
        c = 0
        for fname in enum_all_files(search_dir): # 여기에서 카테고리랑 이름이 같으면 걸러내자
            dst = average_hash(fname)
            try:
                color_files = hsv_color_dist('media/'+fname)
                color_korea2 = hsv_dist(color_files)
                print(set(color_korea2))
            except:
                print("일단 패스")
                continue
            diff_r = hamming_dist(src, dst) / 256
            print("[check] ",fname)
            if diff_r < rate:
                print(set(color_korea) - set(color_korea2))
                for x in img_list:
                    if len(set(color_korea) - set(color_korea2))<=1:
                        if fname == x:
                            address.append(lotteData.objects.get(lotteImage=x))
                c+=1
                yield (diff_r, fname)
        if c==0:
            return render(request, 'imageprocess/warningone.html')
    # 찾기
    sim_list =[]
    srcfile_list =[] 
    distance = []
    namelist = []
    address = []
    sim=[]
    

    for x in range(image_count):
        print(class_list[x])
        srcfile = 'media/images/temp/{}/{}.jpg'.format(class_list[x],x)
        srcfile_list.append(srcfile)
        search_dir = "media/images/{}".format(class_list[x])
        cache_dir = "imageprocess/imagecache/{}".format(class_list[x])
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir) 

        print(srcfile)
        sim = list(find_image(srcfile, 0.5,class_list[x]))
        sim = sorted(sim, key=lambda x:x[0])
        sim_list.append(sim)
        for r, f in sim:
            print(r,">",f)

            f=f.replace("\\",'/')
            f = '/'+f
            print(f)
            # address.append(f)
            # namelist.append(os.path.basename(f))
            # distance.append(r)
        # img_list = address.values_list('lotteImage',flat = True)
    for x in k:
        if x in address:
            pricelist.append(x)
    if len(address)==0:
        return render(request, 'imageprocess/warningone.html')
    
    return render(request, 'imageprocess/result.html', {'sim': sim,  'distance':distance, 'product':pricelist, 'kim':kim, 'soo':soo})