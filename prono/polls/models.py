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
        return self.pub_date - timezone.now() < timedelta(minutes=10)

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
    # Max point number earned if correct answer
    points = models.IntegerField(default=0)
    # Method to compute points :
    # "EXACT"  => points if prono == answer else 0
    # "DIFF"   => points - min(abs(answer-prono), points)
    # "DIFF2"  => points - min(floor(abs(answer-prono)/2), points)
    pointScoreType = models.CharField(max_length=40, default="EXACT")
    pub_date = models.DateTimeField("date published")
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)

    def isPronoOver(self):
        return self.pub_date - timezone.now() < timedelta(minutes=10)

    def __str__(self):
        return self.question_text


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=30)
    points = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.choice


class Qualif(models.Model):
    squad_1 = models.CharField(max_length=20)
    squad_2 = models.CharField(max_length=20)

    answer = models.CharField(max_length=20, default="None")

    pub_date = models.DateTimeField("date published")

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)

    def isPronoOver(self):
        return self.pub_date - timezone.now() < timedelta(minutes=10)

    def __str__(self):
        return self.squad_1 + " ou " + self.squad_2


class QualifChoice(models.Model):
    qualif = models.ForeignKey(Qualif, on_delete=models.CASCADE)

    choice = models.CharField(max_length=20, default="None")

    points = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.choice != "None":
            return str(self.choice)
        return "Pas encore pronostiqué."


class Group(models.Model):
    group_name = models.CharField(max_length=30)
    squad_1 = models.CharField(max_length=20)
    squad_2 = models.CharField(max_length=20)
    squad_3 = models.CharField(max_length=20)
    squad_4 = models.CharField(max_length=20)

    rank_1 = models.IntegerField(default=-1)
    rank_2 = models.IntegerField(default=-1)
    rank_3 = models.IntegerField(default=-1)
    rank_4 = models.IntegerField(default=-1)

    pub_date = models.DateTimeField("date published")

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)

    def isPronoOver(self):
        return self.pub_date - timezone.now() < timedelta(minutes=10)

    def __str__(self):
        return self.group_name


class GroupChoice(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    rank_1 = models.IntegerField(default=-1)
    rank_2 = models.IntegerField(default=-1)
    rank_3 = models.IntegerField(default=-1)
    rank_4 = models.IntegerField(default=-1)

    points = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.rank_1 != -1 and self.rank_2 != -1 and self.rank_3 != -1 and self.rank_4 != -1:
            return str(self.rank_1) + ", " + str(self.rank_2) + ", " + str(self.rank_3) + ", " + str(self.rank_4)
        return "Pas encore pronostiqué."
