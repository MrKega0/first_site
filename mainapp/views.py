from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import Genre, Game, Comment, Favorite
from django.contrib.auth.decorators import login_required
from userapp.views import logout_view
from ai_bot.ai_bot import get_recommended_games, get_game_description, get_game_genre, get_full_recommendations_for
from asgiref.sync import sync_to_async
from django.http.response import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import viewsets
from .models import Game
from .serializers import GameSerializer

import hashlib
from django.core.cache import cache
from asgiref.sync import sync_to_async

# Обёртки для вызовов get/set кэша из async-кода:
cache_get = sync_to_async(cache.get)
cache_set = sync_to_async(cache.set)


# Асинхронные вспомогательные функции, ну или подобие асинхронности
@sync_to_async
def get_user_favorites(user):
    return list(user.favorites.select_related("game").all())

@sync_to_async
def find_game_by_name(name):
    return Game.objects.filter(name__icontains=name).first()

@sync_to_async
def get_or_create_genre(genre_name):
    genre, _ = Genre.objects.get_or_create(name__iexact=genre_name, defaults={"name": genre_name})
    return genre

@sync_to_async
def create_game(name: str, genre_name: str, description: str) -> Game:
    # Найдём или создадим жанр
    genre, _ = Genre.objects.get_or_create(name__iexact=genre_name, defaults={'name': genre_name})
    return Game.objects.create(name=name, genre=genre, description=description)

@sync_to_async
def serialize_game(game: Game) -> dict:
    return {
        'id':          game.id,
        'name':        game.name,
        'genre':       {'id': game.genre.id, 'name': game.genre.name},
        'description': game.description,
        'img':         game.img.url,
    }

@sync_to_async
def fetch_existing_games(names: list[str]) -> dict:
    # Вернём сразу словарь name → game
    qs = Game.objects.filter(name__in=names).select_related('genre')
    return { g.name: g for g in qs }


#Основные вьюшки
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
    return render(request, "mainapp/recommended_games.html")

# Вспомогательные вьюшки
async def asynh_get_recommended_games(request):
    user_favorites = await get_user_favorites(request.user)
    user_favorites_str = ", ".join([favorite.game.name for favorite in user_favorites])
    key = f"recs:{request.user.id}:{hashlib.md5(user_favorites_str.encode()).hexdigest()}"
    cached = await cache_get(key)
    if cached is not None:
        return JsonResponse({"recommended_games": cached}, status=200)

    ai_rec_names = await get_recommended_games(user_favorites_str)
    
    existing = await fetch_existing_games(ai_rec_names)  # { name: Game }
    new_names = [n for n in ai_rec_names if n not in existing]
    
    new_objs = []
    if new_names:
        # get_full_recommendations_for вернёт list[{'name','genre','description'}] только для new_names
        new_data = await get_full_recommendations_for(new_names)
        for d in new_data:
            # создаём в БД
            g = await create_game(d['name'], d['genre'], d['description'])
            new_objs.append(g)

    result = []
    for name in ai_rec_names:
        if name in existing:
            result.append(await serialize_game(existing[name]))
        else:
            # найдём только что созданный объект
            g = next(x for x in new_objs if x.name == name)
            result.append(await serialize_game(g))
    
    # Делаем кэш
    await cache_set(key, result, timeout=3600)
    print("CACHE SET for key:", key)
        
    return JsonResponse({"recommended_games":result}, status=200)

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

# DRF
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
