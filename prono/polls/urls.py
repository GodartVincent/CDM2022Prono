from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexPolls, name='indexPoll'),
    path('poll/<int:poll_id>/', views.detailPoll, name='detailPoll'),
    path('match/<int:match_id>/', views.detailMatch, name='detailMatch'),
    # path('match/<int:match_id>/prono/', views.vote, name='vote'),
]