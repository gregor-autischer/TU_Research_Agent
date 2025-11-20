from django.shortcuts import render
import os
from django.conf import settings

def index(request):
    return render(request, 'web_app/index.html')
