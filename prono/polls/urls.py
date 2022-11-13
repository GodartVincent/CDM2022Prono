from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.indexPolls, name='indexPoll'),
    path('poll/<int:poll_id>/', views.detailPoll, name='detailPoll'),
    path('match/<int:match_id>/', views.detailMatch, name='detailMatch'),
]