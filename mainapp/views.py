from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import Genre, Game, Comment, Favorite
from django.contrib.auth.decorators import login_required
from userapp.views import logout_view
from ai_bot.ai_bot import get_recommended_games

from django.http.response import JsonResponse

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

# def sp(request):
#     #print(request.session['a'])
#     name = request.GET.get('name')
#     last_name = request.GET.get('last_name')
#     print(name)
#     if not name:
#         name = 'Безымянный лох'
#     context = {'name':name, 'last_name':last_name }
#     return render(request, "mainapp/sp.html", context)

@login_required
def game_info(request, game_id):
    game = Game.objects.get(id=game_id)
    # print(game.id in request.user.favorites.all().values_list("game",flat=True))
    # print(request.user.favorites.all().filter(game = game).exists())
    if request.method == "POST":
        content = request.POST.get("comment_content","").strip()
        if content:
            Comment.objects.create(
                user = request.user,
                game = game,
                content = content
            )
        return HttpResponseRedirect(request.path)
    
    comments = game.comments.all()
    context = {
        'game':game,
        'comments': comments,
        'is_fav': request.user.favorites.all().filter(game = game).exists()
    }
    return render(request, "mainapp/game_info.html", context)
    # game = Game.objects.create()
    # game.save()

def recommended_games(request):
    user_favorites = request.user.favorites.all()
    user_favorites_str = ", ".join([favorite.game.name for favorite in user_favorites])
    ai_rec_games = get_recommended_games(user_favorites_str)
    
    context = {"recommended_games":ai_rec_games}
    print(ai_rec_games)
    
    return render(request, "mainapp/recommended_games.html", context)

def add_comment(request):
    print(dict(request.POST.items()))
    try:
        content = request.POST.get("comment_content","").strip()
        print(content)
        game_id = int(request.POST.get("game_id"))
        Comment.objects.create(
            user = request.user,
            game_id = game_id,
            content = content
        )
        return JsonResponse({"message":'ok'}, status=201)
    except Exception as e:
        print(e)

    return JsonResponse({"message":'что то пошло не так'}, status=400)

def toggle_favorite(request):
    # print(dict(request.POST.items()))
    try:
        game_id = int(request.POST.get("game_id"))
        game = Game.objects.get(id=game_id)

        fav_qs = Favorite.objects.filter(user=request.user, game=game)

        if not fav_qs.exists():
            Favorite.objects.create(user=request.user, game=game)
            return JsonResponse({"message": "Добавлено в избранное", "status": "added"}, status=200)
        else:
            fav_qs.delete()
            return JsonResponse({"message": "Удалено из избранного", "status": "removed"}, status=200)

    except Exception as e:
        print(e)

    return JsonResponse({"message":'что то пошло не так'}, status=400)