from django.contrib import admin
from .models import Question, Choice, Match

admin.site.register(Match)
admin.site.register(Question)
