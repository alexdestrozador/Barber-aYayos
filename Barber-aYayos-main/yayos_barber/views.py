from django.shortcuts import render

def home(request):
    return render(request, 'Home/home.html')

def main(request):
    return render(request, 'Landing/index.html')

