from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:matchs_id>/', views.detail, name='detail'),
    path('<int:matchs_id>/results/', views.results, name='results'),
    path('<int:matchs_id>/prono/', views.vote, name='vote'),
]