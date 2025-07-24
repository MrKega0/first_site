from django.contrib import admin
from django.urls import path, include
from mainapp.views import index, about_me, game_info, add_comment, toggle_favorite, recommended_games, asynh_get_recommended_games
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import GameViewSet

router = DefaultRouter()
router.register(r'game', GameViewSet, basename='game')

urlpatterns = router.urls

app_name = "mainapp"

urlpatterns = [
    path('', index),
    path('about-me/', about_me),
    # path('sp/', sp),
    path('game/<int:game_id>', game_info),
    path('add_comments/',add_comment),
    path('toggle_favorite/',toggle_favorite),
    path('recommended_games',recommended_games),
    path('get_recommended_games',asynh_get_recommended_games)
]
