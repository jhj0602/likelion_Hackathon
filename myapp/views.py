from django.shortcuts import render

# Create your views here.
def homelogin(request):
    return render(request, 'myapp/homelogin.html')

def mypage(request):
    return render(request, 'myapp/mypage.html')

def myportfolio(request):
    return render(request, 'myapp/myportfolio.html')

def like(request):
    return render(request, 'myapp/like.html')

def purchase(request):
    return render(request, 'myapp/purchase.html')

def contact(request):
    return render(request, 'myapp/contact.html')

def create(request):
    return render(request, 'myapp/create.html')