from .models import (
    Match,
    MatchChoice,
    Question,
    QuestionChoice,
    Group,
    GroupChoice,
    Poll,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
import numpy as np


def indexPolls(request):
    polls = Poll.objects.all()
    context = {"polls": polls}
    return render(request, "polls/indexPolls.html", context)


def computeMatchScores(matchs):
    matchNb = len(matchs)
    points = [0]*matchNb
    for matchIdx in range(matchNb):
        prono_1 = matchs[matchIdx].prono_1
        prono_2 = matchs[matchIdx].prono_2
        score_1 = matchs[matchIdx].score_1
        score_2 = matchs[matchIdx].score_2
        if prono_1 is not None and prono_1 != -1 and score_1 != -1\
            and prono_2 is not None and prono_2 != -1 and score_2 != -1:
            if prono_1 == score_1 and prono_2 == score_2:
                points[matchIdx] = 5
            elif prono_1 - prono_2 == score_1 - score_2:
                points[matchIdx] = 3
            elif np.sign(prono_1 - prono_2) == np.sign(score_1 - score_2):
                points[matchIdx] = 2
    return points


def computeQuestionScores(questions):
    questionNb = len(questions)
    points = [0]*questionNb
    for questionIdx in range(questionNb):
        prono  = questions[questionIdx].prono
        answer = questions[questionIdx].answer
        questionPoints = questions[questionIdx].points
        pointScoreType = questions[questionIdx].pointScoreType
        if prono is not None and len(prono) != 0\
            and answer is not None and answer != "None" and len(answer) != 0\
                and questionPoints is not None:
            if pointScoreType is None or len(pointScoreType) == 0 or pointScoreType == "EXACT":
                if answer.lower() in prono.lower():
                    points[questionIdx] = questionPoints
            elif pointScoreType == "DIFF":
                points[questionIdx] = questionPoints - min(questionPoints, abs(int(answer) - int(prono)))
            elif pointScoreType == "DIFF2":
                points[questionIdx] = questionPoints - min(questionPoints, int(np.floor(abs(float(answer) - float(prono))/2))) 
    return points


def isValid(entries):
    isValid = True
    for entry in entries:
        isValid = isValid and entry is not None and entry in range(1, 5)
    return isValid


def computeGroupScores(groups):
    groupNb = len(groups)
    points = [0]*groupNb
    for groupIdx in range(groupNb):
        prono = [groups[groupIdx].prono_1, groups[groupIdx].prono_2, groups[groupIdx].prono_3, groups[groupIdx].prono_4]
        rank  = [groups[groupIdx].rank_1 , groups[groupIdx].rank_2 , groups[groupIdx].rank_3 , groups[groupIdx].rank_4 ]
        if isValid(prono) and isValid(rank):
            points[groupIdx] = 12
            for team1Idx in range(4):
                for team2Idx in range(team1Idx+1, 4):
                    inferiorAndWrong = rank[team1Idx] > rank[team2Idx] and prono[team1Idx] <= prono[team2Idx]
                    superiorAndWrong = rank[team1Idx] < rank[team2Idx] and prono[team1Idx] >= prono[team2Idx]
                    if inferiorAndWrong or superiorAndWrong:
                        points[groupIdx] -= 2
    return points



def detailPoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    subquery = MatchChoice.objects.filter(match=OuterRef("pk"), user=request.user)
    matchs = poll.match_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("score_1"),
        prono_2=subquery.values("score_2"),
    )
    matchScores = computeMatchScores(matchs)

    subquery = QuestionChoice.objects.filter(question=OuterRef("pk"), user=request.user)
    questions = poll.question_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono=subquery.values("choice"),
    )
    questionScores = computeQuestionScores(questions)

    subquery = GroupChoice.objects.filter(group=OuterRef("pk"), user=request.user)
    groups = poll.group_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("rank_1"),
        prono_2=subquery.values("rank_2"),
        prono_3=subquery.values("rank_3"),
        prono_4=subquery.values("rank_4"),
    )
    groupScores = computeGroupScores(groups)

    return render(
        request,
        "polls/detailPoll.html",
        {
            "poll": poll,
            "matchs"    : zip(matchs   , matchScores),
            "questions" : zip(questions, questionScores),
            "groups"    : zip(groups   , groupScores),
            "totalScore": sum(matchScores)+sum(questionScores)+sum(groupScores)
        },
    )


def detailMatch(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, "matchs/detail.html", {"match": match})


def pronosticMatch(request, match_id):
    print("in pronoMatch")
    if request.method == "POST":
        match = get_object_or_404(Match, pk=match_id)
        print(f"in POST, match = {match.__str__()}")
        if match.isPronoOver():
            # Redisplay the match pronosticing form.
            return detailPoll(request, match.poll.pk)
        try:
            matchChoice = match.matchchoice_set.get(user_id=request.user)
        except (KeyError, MatchChoice.DoesNotExist):
            matchChoice = match.matchchoice_set.create(user=request.user)

        try:
            scores = request.POST.getlist("score")
            matchChoice.score_1 = int(scores[0])
            matchChoice.score_2 = int(scores[1])
        except (ValueError):
            # Redisplay the match pronosticing form.
            return detailPoll(request, match.poll.pk)
        else:
            matchChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            #return HttpResponseRedirect(f"/poll/{match.poll.pk}/#match_{match.pk}")
            return HttpResponse('<script>history.back();</script>')


def pronosticQuestion(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=question_id)
        if question.isPronoOver():
            # Redisplay the match pronosticing form.
            return detailPoll(request, question.poll.pk)
        try:
            questionChoice = question.questionchoice_set.get(user_id=request.user)
        except (KeyError, QuestionChoice.DoesNotExist):
            questionChoice = question.questionchoice_set.create(user=request.user)

        try:
            questionChoice.choice = request.POST["answer"]
        except (ValueError):
            # Redisplay the question pronosticing form.
            return detailPoll(request, question.poll.pk)
        else:
            questionChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponse("<script>history.back();</script>")


def pronosticGroup(request, group_id):
    if request.method == "POST":
        group = get_object_or_404(Group, pk=group_id)
        if group.isPronoOver():
            # Redisplay the match pronosticing form.
            return detailPoll(request, group.poll.pk)
        try:
            groupChoice = group.groupchoice_set.get(user_id=request.user)
        except (KeyError, GroupChoice.DoesNotExist):
            groupChoice = group.groupchoice_set.create(user=request.user)

        try:
            ranks = request.POST.getlist("rank")
            groupChoice.rank_1 = int(ranks[0])
            groupChoice.rank_2 = int(ranks[1])
            groupChoice.rank_3 = int(ranks[2])
            groupChoice.rank_4 = int(ranks[3])
        except (ValueError):
            # Redisplay the group pronosticing form.
            return detailPoll(request, group.poll.pk)
        else:
            groupChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponse("<script>history.back();</script>")


# def results(_, match_id):
#     response = "Vous regardez les résultats du match %s."
#     return HttpResponse(response % match_id)
