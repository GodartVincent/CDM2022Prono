from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Concat

class Matchs(models.Model):
    squad_1 = models.CharField(max_length=20)
    squad_2 = models.CharField(max_length=20)
    score_1 = models.IntegerField(default=0)
    score_2 = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.squad_1 + " - " + self.squad_2

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
