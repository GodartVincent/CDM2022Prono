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
from django.http import HttpResponse, JsonResponse
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
            scoreArray[userIdx][pollIdx][0] = sum(computeMatchScores(matchs,
                                                                    poll.exact_score,
                                                                    poll.diff_score,
                                                                    poll.win_score,
                                                                    poll.minority_score))

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
            scoreArray[userIdx][pollIdx][2] = sum(computeGroupScores(groups, poll.rank_score, poll.rank_factor_score))

            subquery = QualifChoice.objects.filter(qualif=OuterRef("pk"), user=user)
            qualifs = poll.qualif_set.all().order_by("pub_date").annotate(
                isfilled=Exists(subquery),
                prono=subquery.values("choice"),
            )
            scoreArray[userIdx][pollIdx][2] += sum(computeQualifScores(qualifs, poll.qualif_score))
            totalScoreArray[userIdx] += sum(scoreArray[userIdx][pollIdx])
            
    zippedResults = list(zip(userNames, totalScoreArray, scoreArray))
    zippedResults = sorted(zippedResults, key = lambda x: x[1], reverse=True)
    return render(request,
                    "polls/results.html",
                    {
                        "pollnames" : pollNames,
                        "users"     : users,
                        "results"   : zippedResults,
                    })


def isIn(answer, prono):
    allAnswers = answer.split("/")
    for singleAnswer in allAnswers:
        if singleAnswer in prono or prono in singleAnswer:
            return True 
    return False


def computeMatchScores(matchs, exact_score, diff_score, win_score, minority_score):
    matchNb = len(matchs)
    points = [0.0] * matchNb  # On utilise des Float pour les cotes

    for matchIdx in range(matchNb):
        prono_1 = matchs[matchIdx].prono_1
        prono_2 = matchs[matchIdx].prono_2
        score_1 = matchs[matchIdx].score_1
        score_2 = matchs[matchIdx].score_2

        # Si le match est termine et que l'utilisateur a fait un prono
        if prono_1 is not None and prono_1 != -1 and score_1 != -1 \
            and prono_2 is not None and prono_2 != -1 and score_2 != -1:

            prono_delta = prono_1 - prono_2
            score_delta = score_1 - score_2

            # 1. Quelle est l'issue réelle du match et quelle cote s'applique ?
            if score_delta > 0:
                cote_gagnee = matchs[matchIdx].cote_1
            elif score_delta == 0:
                cote_gagnee = matchs[matchIdx].cote_N
            else:
                cote_gagnee = matchs[matchIdx].cote_2

            # 2. Le joueur a-t-il trouve la bonne issue (bon vainqueur ou bon nul) ?
            if np.sign(prono_delta) == np.sign(score_delta):
                
                # S'il a le score exact
                if prono_1 == score_1 and prono_2 == score_2:
                    points[matchIdx] = cote_gagnee * 2.0
                
                # S'il a la bonne difference de buts
                elif prono_delta == score_delta:
                    points[matchIdx] = cote_gagnee * 1.5
                
                # S'il a juste la bonne issue
                else:
                    points[matchIdx] = cote_gagnee

    return points


# def computeMatchScores(matchs, exact_score, diff_score, win_score, minority_score):
#     matchNb = len(matchs)
#     points = [0]*matchNb
#     for matchIdx in range(matchNb):
#         win_nb = 0
#         equal_nb = 0
#         loss_nb = 0
#         all_prono = MatchChoice.objects.filter(match=matchs[matchIdx])
#         for prono in all_prono:
#             diff = prono.score_1 - prono.score_2
#             win_nb += diff > 0
#             equal_nb += diff == 0
#             loss_nb += diff < 0
#         is_win_major = win_nb >= equal_nb and win_nb >= loss_nb
#         is_equal_major = equal_nb >= win_nb and equal_nb >= loss_nb
#         is_loss_major = loss_nb >= equal_nb and loss_nb >= win_nb

#         prono_1 = matchs[matchIdx].prono_1
#         prono_2 = matchs[matchIdx].prono_2
#         score_1 = matchs[matchIdx].score_1
#         score_2 = matchs[matchIdx].score_2
#         is_prono_correct = False
#         if prono_1 is not None and prono_1 != -1 and score_1 != -1\
#             and prono_2 is not None and prono_2 != -1 and score_2 != -1:
#             prono_delta = prono_1 - prono_2
#             if prono_1 == score_1 and prono_2 == score_2:
#                 is_prono_correct = True
#                 points[matchIdx] = exact_score
#             elif prono_delta == score_1 - score_2:
#                 is_prono_correct = True
#                 points[matchIdx] = diff_score
#             elif np.sign(prono_delta) == np.sign(score_1 - score_2):
#                 is_prono_correct = True
#                 points[matchIdx] = win_score
#             if is_prono_correct:
#                 if prono_delta > 0 and not is_win_major:
#                     points[matchIdx] += minority_score
#                 elif prono_delta == 0 and not is_equal_major:
#                     points[matchIdx] += minority_score
#                 elif prono_delta < 0 and not is_loss_major:
#                     points[matchIdx] += minority_score
#     return points


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
                if isIn(answer.lower(), prono.lower()):
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


def computeGroupScores(groups, rank_score, rank_factor_score):
    groupNb = len(groups)
    points = [0]*groupNb
    for groupIdx in range(groupNb):
        prono = [groups[groupIdx].prono_1, groups[groupIdx].prono_2, groups[groupIdx].prono_3, groups[groupIdx].prono_4]
        rank  = [groups[groupIdx].rank_1 , groups[groupIdx].rank_2 , groups[groupIdx].rank_3 , groups[groupIdx].rank_4 ]
        if isValid(prono) and isValid(rank):
            points[groupIdx] = rank_score*rank_factor_score
            for team1Idx in range(4):
                for team2Idx in range(team1Idx+1, 4):
                    inferiorAndWrong = rank[team1Idx] > rank[team2Idx] and prono[team1Idx] <= prono[team2Idx]
                    superiorAndWrong = rank[team1Idx] < rank[team2Idx] and prono[team1Idx] >= prono[team2Idx]
                    if inferiorAndWrong or superiorAndWrong:
                        points[groupIdx] -= rank_factor_score
    return points


def computeQualifScores(qualifs, qualif_score):
    qualifNb = len(qualifs)
    points = [0]*qualifNb
    for qualifIdx in range(qualifNb):
        prono  = qualifs[qualifIdx].prono
        answer = qualifs[qualifIdx].answer
        if prono is not None and len(prono) != 0\
            and answer is not None and answer != "None" and len(answer) != 0\
                and qualif_score is not None:
            if answer.lower() in prono.lower() or prono.lower() in answer.lower():
                points[qualifIdx] = qualif_score
    return points



def detailPoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    subquery = MatchChoice.objects.filter(match=OuterRef("pk"), user=request.user)
    matchs = poll.match_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("score_1"),
        prono_2=subquery.values("score_2"),
    )
    matchScores = computeMatchScores(matchs,
                                    poll.exact_score,
                                    poll.diff_score,
                                    poll.win_score,
                                    poll.minority_score)

    subquery = QuestionChoice.objects.filter(question=OuterRef("pk"), user=request.user)
    questions = poll.question_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono=subquery.values("choice"),
    )
    questionScores = computeQuestionScores(questions)

    subquery = GroupChoice.objects.filter(group=OuterRef("pk"), user=request.user)
    groups = poll.group_set.all().order_by("group_name").annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("rank_1"),
        prono_2=subquery.values("rank_2"),
        prono_3=subquery.values("rank_3"),
        prono_4=subquery.values("rank_4"),
    )
    groupScores = computeGroupScores(groups, poll.rank_score, poll.rank_factor_score)

    subquery = QualifChoice.objects.filter(qualif=OuterRef("pk"), user=request.user)
    qualifs = poll.qualif_set.all().order_by("pub_date").annotate(
        isfilled=Exists(subquery),
        prono=subquery.values("choice"),
    )
    qualifScores = computeQualifScores(qualifs, poll.qualif_score)

    return render(
        request,
        "polls/detailPoll.html",
        {
            "poll"      : poll,
            "matchs"    : zip(matchs   , matchScores),
            "questions" : zip(questions, questionScores),
            "groups"    : zip(groups   , groupScores),
            "qualifs"   : zip(qualifs  , qualifScores),
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
        
        # Si le match a déjà commencé (bloqué)
        if match.isPronoOver():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Trop tard, le match a commencé !'}, status=400)
            return detailPoll(request, match.poll.pk)
            
        try:
            matchChoice = match.matchchoice_set.get(user_id=request.user)
        except (KeyError, MatchChoice.DoesNotExist):
            matchChoice = match.matchchoice_set.create(user=request.user)

        try:
            scores = request.POST.getlist("score")
            matchChoice.score_1 = int(scores[0])
            matchChoice.score_2 = int(scores[1])
        except (ValueError, IndexError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Valeur invalide.'}, status=400)
            return detailPoll(request, match.poll.pk)
        else:
            matchChoice.save()
            # Si c'est une sauvegarde automatique en arrière-plan
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Score enregistré !'})
            return HttpResponse('<script>history.back();</script>')


def pronosticQuestion(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=question_id)
        
        if question.isPronoOver():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Trop tard !'}, status=400)
            return detailPoll(request, question.poll.pk)
            
        try:
            questionChoice = question.questionchoice_set.get(user_id=request.user)
        except (KeyError, QuestionChoice.DoesNotExist):
            questionChoice = question.questionchoice_set.create(user=request.user)

        try:
            questionChoice.choice = request.POST["answer"]
        except (ValueError, KeyError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Erreur de saisie.'}, status=400)
            return detailPoll(request, question.poll.pk)
        else:
            questionChoice.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Réponse enregistrée !'})
            return HttpResponse("<script>history.back();</script>")


def pronosticGroup(request, group_id):
    if request.method == "POST":
        group = get_object_or_404(Group, pk=group_id)
        
        if group.isPronoOver():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Les pronos sont fermés pour ce groupe !'}, status=400)
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
        except (ValueError, IndexError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Classement invalide.'}, status=400)
            return detailPoll(request, group.poll.pk)
        else:
            groupChoice.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Groupe mis à jour !'})
            return HttpResponse("<script>history.back();</script>")


def pronosticQualif(request, qualif_id):
    if request.method == "POST":
        qualif = get_object_or_404(Qualif, pk=qualif_id)
        
        if qualif.isPronoOver():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Trop tard !'}, status=400)
            return detailPoll(request, qualif.poll.pk)
            
        try:
            qualifChoice = qualif.qualifchoice_set.get(user_id=request.user)
        except (KeyError, QualifChoice.DoesNotExist):
            qualifChoice = qualif.qualifchoice_set.create(user=request.user)

        try:
            qualifChoice.choice = request.POST.getlist("prono")[0]
        except (ValueError, IndexError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Erreur.'}, status=400)
            return detailPoll(request, qualif.poll.pk)
        else:
            qualifChoice.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Qualification enregistrée !'})
            return HttpResponse("<script>history.back();</script>")
        

# def results(_, match_id):
#     response = "Vous regardez les résultats du match %s."
#     return HttpResponse(response % match_id)
