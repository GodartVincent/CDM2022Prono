from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Matchs, Question, Choice
from .serializers import MatchsSerializer
from django.shortcuts import get_object_or_404, render
from django.http import Http404


def index(request):
    latest_matchs_list = Matchs.objects.order_by('-pub_date')[:1]
    context = {'latest_matchs_list': latest_matchs_list}
    return render(request, 'polls/index.html', context)

def detail(request, matchs_id):
    matchs = get_object_or_404(Matchs, pk=matchs_id)
    return render(request, 'polls/detail.html', {'matchs': matchs})

def results(request, matchs_id):
    response = "Vous regardez les résultats du match %s."
    return HttpResponse(response % matchs_id)

def vote(request, matchs_id):
    return HttpResponse("Vous pronostiquez le match %s." % matchs_id)