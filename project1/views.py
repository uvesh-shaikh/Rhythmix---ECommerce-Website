from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request,'Base/index.html')


def about(request):
    return HttpResponse("<h1>about</h1><a href='/'>Home</a>")