from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:match_id>/', views.detail, name='detail'),
    path('<int:match_id>/results/', views.results, name='results'),
    path('<int:match_id>/prono/', views.vote, name='vote'),
]