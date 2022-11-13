from django.contrib import admin
from .models import Question, QuestionChoice, Match, MatchChoice

admin.site.register(Match)
admin.site.register(Question)
admin.site.register(MatchChoice)
admin.site.register(QuestionChoice)
