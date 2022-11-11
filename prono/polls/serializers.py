from rest_framework import serializers
from .models import Matchs, Question, Choice

class MatchsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matchs
        fields = ["squad_1", "squad_2", "score_1", "score_2", "pub_date"]