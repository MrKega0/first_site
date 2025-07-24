from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import Genre, Game, Comment, Favorite
from django.contrib.auth.decorators import login_required
from userapp.views import logout_view
from ai_bot.ai_bot import get_recommended_games, get_game_description, get_game_genre, get_full_recommendations_for
from asgiref.sync import sync_to_async
from django.http.response import JsonResponse
from django.forms.models import model_to_dict
<<<<<<< HEAD
from rest_framework import viewsets
from .models import Game
from .serializers import GameSerializer
=======
from django.views.generic import ListView, DetailView
>>>>>>> e0ffbcbcc46ddb55e139434bcacaa741f5d53361

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
class IndexView(ListView):
    model = Game
    template_name = "mainapp/index.html"
    context_object_name = 'games'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        genre_filter = self.request.GET.get('genre')
        game_filter = self.request.GET.get('game')
        if genre_filter:
            queryset = queryset.filter(genre_id=genre_filter)
        if game_filter:
            queryset = queryset.filter(name__contains=game_filter)
        return queryset

def about_me(request):
    return render(request, "mainapp/about_me.html")

class GameInfoView(DetailView):
    model = Game
    template_name = "mainapp/game_info.html"
    context_object_name = 'game'
    pk_url_kwarg = 'game_id'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        content = request.POST.get("comment_content","").strip()
        if content:
            Comment.objects.create(
                user = request.user,
                game = self.object,
                content = content
            )
        return HttpResponseRedirect(self.request.path)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.all()
        context['is_fav'] = self.request.user.favorites.all().filter(game = self.object).exists()
        context['comments'] = comments
        return context
        

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
