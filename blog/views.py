from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    """
    Перенаправляет на API документацию
    """
    return redirect('/api/docs')
