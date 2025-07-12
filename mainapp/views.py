from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import Genre, Game, Comment, Favorite
from django.contrib.auth.decorators import login_required
from userapp.views import logout_view
from ai_bot.ai_bot import get_recommended_games, get_game_description, get_game_genre
from asgiref.sync import sync_to_async
from django.http.response import JsonResponse
from django.forms.models import model_to_dict

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
def create_game(name, genre, description):
    return Game.objects.create(name=name, genre=genre, description=description)

@sync_to_async
def serialize_game_obj(game):
    data = model_to_dict(game, fields=['id','name','description'])
    data['genre'] = model_to_dict(game.genre, fields=['id','name'])
    data['img'] = game.img.url if game.img else None
    return data


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

# В recommended_games.html сделать запрос к асинхронной вспомогательной вьюшке
# которая должна делать запрос ai, получать список рекомендуемых игр,
# подгружать имеющиеся игры из бд. А отсутствующим играм нужно делать запрос на получение
# описания и добавлять в бд, а затем подгружать эти игры из бд
def recommended_games(request):
    return render(request, "mainapp/recommended_games.html")

# Вспомогательные вьюшки
async def asynh_get_recommended_games(request):
    user_favorites = await get_user_favorites(request.user)
    user_favorites_str = ", ".join([favorite.game.name for favorite in user_favorites])
    ai_rec_games = await get_recommended_games(user_favorites_str)
    
    print(ai_rec_games)
    recommended_games = []
    
    for game_name in ai_rec_games:
        game = await find_game_by_name(game_name)
        if not game:
            description = await get_game_description(game_name)
            genre_name = await get_game_genre(game_name)
            genre = await get_or_create_genre(genre_name)
            game = await create_game(game_name, genre, description)

        data = await serialize_game_obj(game)
        recommended_games.append(data)
        
    return JsonResponse({"recommended_games":recommended_games}, status=200)

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
