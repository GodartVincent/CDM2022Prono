from rest_framework import serializers
from .models import Question, QuestionChoice, Match, MatchChoice

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["squad_1", "squad_2", "score_1", "score_2", "pub_date"]