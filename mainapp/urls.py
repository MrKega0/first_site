from django.contrib import admin
from django.urls import path, include
from mainapp.views import index, about_me, sp
from django.conf import settings
from django.conf.urls.static import static

app_name = "mainapp"

urlpatterns = [
    path('', index),
    path('about-me/', about_me),
    path('sp/', sp)
]
