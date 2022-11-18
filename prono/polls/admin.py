from django.contrib import admin
from .models import Poll, Match, MatchChoice, Question, QuestionChoice, Group, GroupChoice

admin.site.register(Poll)
admin.site.register(Match)
admin.site.register(MatchChoice)
admin.site.register(Question)
admin.site.register(QuestionChoice)
admin.site.register(Group)
admin.site.register(GroupChoice)
