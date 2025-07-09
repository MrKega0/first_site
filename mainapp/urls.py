from django.contrib import admin
from django.urls import path, include
from mainapp.views import index, about_me, game_info, add_comment, toggle_favorite, recommended_games
from django.conf import settings
from django.conf.urls.static import static

app_name = "mainapp"

urlpatterns = [
    path('', index),
    path('about-me/', about_me),
    # path('sp/', sp),
    path('game/<int:game_id>', game_info),
    path('add_comments/',add_comment),
    path('toggle_favorite/',toggle_favorite),
    path('recommended_games',recommended_games)
]
