from django.contrib import admin
from .models import Poll, Match, MatchChoice, Question, QuestionChoice, Group, GroupChoice


class MatchAdmin(admin.ModelAdmin):
    list_display = ('squad_1', 'squad_2', 'score_1', 'score_2', 'pub_date')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'answer', 'pub_date')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'rank_1', 'pub_date')


admin.site.register(Poll)
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchChoice)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionChoice)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupChoice)
