from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Match, Question, Choice
from .serializers import MatchSerializer
from django.shortcuts import get_object_or_404, render
from django.http import Http404


def index(request):
    latest_matchs_list = Match.objects.order_by('-pub_date')[:1]
    context = {'latest_matchs_list': latest_matchs_list}
    return render(request, 'polls/index.html', context)

def detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, 'polls/detail.html', {'matchs': match})

def results(request, match_id):
    response = "Vous regardez les résultats du match %s."
    return HttpResponse(response % match_id)

def vote(request, match_id):
    return HttpResponse("Vous pronostiquez le match %s." % match_id)