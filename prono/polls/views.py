from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import Match, Question, MatchChoice, QuestionChoice
from .serializers import MatchSerializer
from django.shortcuts import get_object_or_404, render
from django.http import Http404


def index(request):
    latest_match_list = Match.objects.order_by('-pub_date')
    latest_question_list = Question.objects.order_by('-pub_date')
    context = {'latest_match_list': latest_match_list, 'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, 'polls/detail.html', {'match': match})

def results(request, match_id):
    response = "Vous regardez les résultats du match %s."
    return HttpResponse(response % match_id)

def vote(request, match_id):
    return HttpResponse("Vous pronostiquez le match %s." % match_id)