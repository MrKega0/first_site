from django.shortcuts import render, HttpResponse
from .models import Genre
# Create your views here.
def index(request):
    request.session['a'] = 'a'
    Genre.objects.all()[0]
    print(Genre.objects.all()[0].name)
    context = {'genres':Genre.objects.all()}
    return render(request, "mainapp/index.html", context)

def about_me(request):
    return render(request, "mainapp/about_me.html")

def sp(request):
    print(request.session['a'])
    name = request.GET.get('name')
    last_name = request.GET.get('last_name')
    print(name)
    if not name:
        name = 'Безымянный лох'
    context = {'name':name, 'last_name':last_name }
    return render(request, "mainapp/sp.html", context)