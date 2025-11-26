from django.shortcuts import render

# Create your views here.


def login(request):
    return render(request,"login.html")

def register(request):
    return render(request, "register.html")

def mainpaige(request):
    return render(request, "main.html")