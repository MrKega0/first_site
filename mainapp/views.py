from django.shortcuts import render, HttpResponse
from .models import Genre, Game
# Create your views here.
def index(request):
    # request.session['a'] = 'a'
    genre = request.GET.get('genre')
    genre = request.GET.get('genre')
    # print(f"Genre = {genre}")
    games = Game.objects.all()
    if genre:
        games = Game.objects.filter(genre_id=genre)

    context = {'genres':Genre.objects.all(), 'games': games}
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
