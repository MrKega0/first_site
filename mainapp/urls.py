from django.contrib import admin
from django.urls import path, include
from mainapp.views import IndexView, about_me,GameInfoView, add_comment, toggle_favorite, recommended_games, asynh_get_recommended_games
from django.conf import settings
from django.conf.urls.static import static

app_name = "mainapp"

urlpatterns = [
    path('', IndexView.as_view()),
    path('about-me/', about_me),
    # path('sp/', sp),
    path('game/<int:game_id>', GameInfoView.as_view()),
    path('add_comments/',add_comment),
    path('toggle_favorite/',toggle_favorite),
    path('recommended_games',recommended_games),
    path('get_recommended_games',asynh_get_recommended_games)
]
