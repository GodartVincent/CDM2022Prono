from django.urls import path
from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.indexPolls, name='indexPoll'),
    path('results/', views.results, name='results'),
    path('poll/<int:poll_id>/', views.detailPoll, name='detailPoll'),
    path('match/<int:match_id>/', views.detailMatch, name='detailMatch'),
    path('<int:match_id>/pronosticMatch/', views.pronosticMatch, name='pronosticMatch'),
    path('<int:question_id>/pronosticQuestion/', views.pronosticQuestion, name='pronosticQuestion'),
    path('<int:group_id>/pronosticGroup/', views.pronosticGroup, name='pronosticGroup'),
    path('<int:qualif_id>/pronosticQualif/', views.pronosticQualif, name='pronosticQualif'),
]