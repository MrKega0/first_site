from django.contrib import admin
from django.urls import path, include
from userapp.views import login
from django.conf import settings
from django.conf.urls.static import static

app_name = "userapp"

urlpatterns = [
    path('login/', view=login),
]
