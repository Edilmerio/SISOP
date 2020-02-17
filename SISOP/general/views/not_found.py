# Create your views here.
from django.shortcuts import render


def not_found(request):
    return render(request, 'general/NotFound.html')

