from django.shortcuts import render, HttpResponse
from .models import Genre, Game, Comment
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def index(request):
    # request.session['a'] = 'a'
    genre_filter = request.GET.get('genre')
    game_filter = request.GET.get('game')
    # print(f"Genre = {genre}")
    games = Game.objects.all()

    if genre_filter:
        games = Game.objects.filter(genre_id=genre_filter)
    if game_filter:
        games = Game.objects.filter(name__contains=game_filter)

    context = {'genres':Genre.objects.all(), 'games': games}
    return render(request, "mainapp/index.html", context)

def about_me(request):
    return render(request, "mainapp/about_me.html")

def sp(request):
    #print(request.session['a'])
    name = request.GET.get('name')
    last_name = request.GET.get('last_name')
    print(name)
    if not name:
        name = 'Безымянный лох'
    context = {'name':name, 'last_name':last_name }
    return render(request, "mainapp/sp.html", context)

@login_required
def game_info(request, game_id):
    game = Game.objects.get(id=game_id)

    if request.method == "POST":
        content = request.POST.get("comment_content","").strip()
        if content:
            Comment.objects.create(
                user = request.user,
                game = game,
                content = content
            )
    
    comments = game.comments.all()
    context = {
        'game':Game.objects.get(id=game_id),
        'comments': comments
    }
    return render(request, "mainapp/game_info.html", context)
    # game = Game.objects.create()
    # game.save()