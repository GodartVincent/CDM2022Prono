from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Poll(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Match(models.Model):
    squad_1 = models.CharField(max_length=20)
    squad_2 = models.CharField(max_length=20)
    score_1 = models.IntegerField(default=-1)
    score_2 = models.IntegerField(default=-1)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    pub_date = models.DateTimeField("date published")

    def isPronoOver(self):
        return self.pub_date - timezone.now() < timedelta(hours=1)

    def __str__(self):
        if self.score_1 != -1 and self.score_2 != -1:
            return (
                self.squad_1
                + " "
                + str(self.score_1)
                + " - "
                + str(self.score_2)
                + " "
                + self.squad_2
            )
        return self.squad_1 + " - " + self.squad_2


class MatchChoice(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    score_1 = models.IntegerField(default=-1)
    score_2 = models.IntegerField(default=-1)
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.score_1 != -1 and self.score_2 != -1:
            return str(self.score_1) + " - " + str(self.score_2)
        return "Pas encore pronostiqué."


class Pronostic(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_1 = models.IntegerField(default=0)
    score_2 = models.IntegerField(default=0)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    answer = models.CharField(max_length=200, default="None")
    pub_date = models.DateTimeField("date published")
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)

    def isPronoOver(self):
        return self.pub_date - timezone.now() < timedelta(hours=1)

    def __str__(self):
        return self.question_text


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=30)
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.choice
