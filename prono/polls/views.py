from .models import (
    Match,
    MatchChoice,
    Question,
    QuestionChoice,
    Qualif,
    QualifChoice,
    Group,
    GroupChoice,
    Poll,
    User,
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

def results(request):
    polls = Poll.objects.all()
    pollNames = polls.values("name")
    pollNb = len(polls)
    users = User.objects.all()
    userNames = []
    userNb = len(users)
    scoreArray = []
    totalScoreArray = []
    for userIdx in range(userNb):
        user = users[userIdx]
        userNames.append(user.username)
        scoreArray.append([])
        totalScoreArray.append(0)
        for pollIdx in range(pollNb):
            poll = polls[pollIdx]
            scoreArray[userIdx].append([0, 0, 0])
            subquery = MatchChoice.objects.filter(match=OuterRef("pk"), user=user)
            matchs = poll.match_set.all().order_by("pub_date").annotate(
                isfilled=Exists(subquery),
                prono_1=subquery.values("score_1"),
                prono_2=subquery.values("score_2"),
            )
            scoreArray[userIdx][pollIdx][0] = sum(computeMatchScores(matchs))

            subquery = QuestionChoice.objects.filter(question=OuterRef("pk"), user=user)
            questions = poll.question_set.all().order_by("pub_date").annotate(
                isfilled=Exists(subquery),
                prono=subquery.values("choice"),
            )
            scoreArray[userIdx][pollIdx][1] = sum(computeQuestionScores(questions))

            subquery = GroupChoice.objects.filter(group=OuterRef("pk"), user=user)
            groups = poll.group_set.all().order_by("pub_date").annotate(
                isfilled=Exists(subquery),
                prono_1=subquery.values("rank_1"),
                prono_2=subquery.values("rank_2"),
                prono_3=subquery.values("rank_3"),
                prono_4=subquery.values("rank_4"),
            )
            scoreArray[userIdx][pollIdx][2] = sum(computeGroupScores(groups))
            totalScoreArray[userIdx] += sum(scoreArray[userIdx][pollIdx])
    
    zippedResults = list(zip(userNames, totalScoreArray, scoreArray))
    print(str(zippedResults))
    zippedResults = sorted(zippedResults, key = lambda x: x[1], reverse=True)
    print(str(zippedResults))
    return render(request,
                    "polls/results.html",
                    {
                        "pollnames" : pollNames,
                        "users"     : users,
                        "results"   : zippedResults,
                    })


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
                if answer.lower() in prono.lower() or prono.lower() in answer.lower():
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
            points[groupIdx] = 6
            for team1Idx in range(4):
                for team2Idx in range(team1Idx+1, 4):
                    inferiorAndWrong = rank[team1Idx] > rank[team2Idx] and prono[team1Idx] <= prono[team2Idx]
                    superiorAndWrong = rank[team1Idx] < rank[team2Idx] and prono[team1Idx] >= prono[team2Idx]
                    if inferiorAndWrong or superiorAndWrong:
                        points[groupIdx] -= 1
    return points


def computeQualifScores(qualifs):
    qualifNb = len(qualifs)
    points = [0]*qualifNb
    for questionIdx in range(qualifNb):
        prono  = qualifs[questionIdx].prono
        answer = qualifs[questionIdx].answer
        questionPoints = 2
        if prono is not None and len(prono) != 0\
            and answer is not None and answer != "None" and len(answer) != 0\
                and questionPoints is not None:
            if answer.lower() in prono.lower() or prono.lower() in answer.lower():
                points[questionIdx] = questionPoints
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

    subquery = QualifChoice.objects.filter(qualif=OuterRef("pk"), user=request.user)
    qualifs = poll.qualif_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono=subquery.values("choice"),
    )
    qualifScores = computeQualifScores(qualifs)

    return render(
        request,
        "polls/detailPoll.html",
        {
            "poll": poll,
            "matchs"    : zip(matchs   , matchScores),
            "questions" : zip(questions, questionScores),
            "groups"    : zip(groups   , groupScores),
            "qualifs"    : zip(qualifs  , qualifScores),
            "totalScore": sum(matchScores)+sum(questionScores)+sum(groupScores)+sum(qualifScores),
            "isGroup"   : len(groups) > 0,
            "isQualif"  : len(qualifs) > 0,
        },
    )


def detailMatch(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, "matchs/detail.html", {"match": match})


def pronosticMatch(request, match_id):
    if request.method == "POST":
        match = get_object_or_404(Match, pk=match_id)
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


def pronosticQualif(request, qualif_id):
    if request.method == "POST":
        qualif = get_object_or_404(Qualif, pk=qualif_id)
        if qualif.isPronoOver():
            # Redisplay the match pronosticing form.
            return detailPoll(request, qualif.poll.pk)
        try:
            qualifChoice = qualif.qualifchoice_set.get(user_id=request.user)
        except (KeyError, QualifChoice.DoesNotExist):
            qualifChoice = qualif.qualifchoice_set.create(user=request.user)

        try:
            qualifChoice.choice = request.POST.getlist("prono")[0]
        except (ValueError):
            # Redisplay the qualif pronosticing form.
            return detailPoll(request, qualif.poll.pk)
        else:
            qualifChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponse("<script>history.back();</script>")


# def results(_, match_id):
#     response = "Vous regardez les résultats du match %s."
#     return HttpResponse(response % match_id)
