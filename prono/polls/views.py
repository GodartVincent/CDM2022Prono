from .models import Match, MatchChoice, Question, QuestionChoice, Group, GroupChoice, Poll
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Exists, OuterRef


def indexPolls(request):
    polls = Poll.objects.all()
    context = {"polls": polls}
    return render(request, "polls/indexPolls.html", context)


def detailPoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)

    subquery = QuestionChoice.objects.filter(question=OuterRef("pk"), user=request.user)
    questions = poll.question_set.all().annotate(
        isfilled=Exists(subquery),
        prono=subquery.values("choice"),
        points=subquery.values("points"),
    )

    subquery = MatchChoice.objects.filter(match=OuterRef("pk"), user=request.user)
    matchs = poll.match_set.all().annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("score_1"),
        prono_2=subquery.values("score_2"),
        points=subquery.values("points"),
    )

    subquery = GroupChoice.objects.filter(group=OuterRef("pk"), user=request.user)
    groups = poll.group_set.all().annotate(
        isfilled=Exists(subquery),
        prono_1=subquery.values("rank_1"),
        prono_2=subquery.values("rank_2"),
        prono_3=subquery.values("rank_3"),
        prono_4=subquery.values("rank_4"),
        points=subquery.values("points"),
    )
    return render(
        request,
        "polls/detailPoll.html",
        {"poll": poll, "matchs": matchs, "questions": questions, "groups": groups},
    )


def detailMatch(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, "matchs/detail.html", {"match": match})


def pronosticMatch(request, match_id):
    if request.method == "POST":
        match = get_object_or_404(Match, pk=match_id)
        if match.isPronoOver():
            # Redisplay the match pronosticing form.
            return render(
                request,
                "polls/detail.html",
                {
                    "match": match,
                    "error_message": "Il est trop tard pour pronostiquer sur ce match.",
                },
            )
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
            return render(
                request,
                "polls/detail.html",
                {
                    "match": match,
                    "error_message": "Vous n'avez pas rempli les 2 scores.",
                },
            )
        else:
            matchChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(
                reverse("polls:detailPoll", args=(match.poll.id,))
            )


def pronosticQuestion(request, question_id):
    if request.method == "POST":
        question = get_object_or_404(Question, pk=question_id)
        if question.isPronoOver():
            # Redisplay the match pronosticing form.
            return render(
                request,
                "polls/detail.html",
                {
                    "question": question,
                    "error_message": "Il est trop tard pour pronostiquer sur cette question.",
                },
            )
        try:
            questionChoice = question.questionchoice_set.get(user_id=request.user)
        except (KeyError, QuestionChoice.DoesNotExist):
            questionChoice = question.questionchoice_set.create(user=request.user)

        try:
            questionChoice.choice = request.POST["answer"]
        except (ValueError):
            # Redisplay the question pronosticing form.
            return render(
                request,
                "polls/detail.html",
                {
                    "question": question,
                    "error_message": "Vous n'avez pas repondu à la question.",
                },
            )
        else:
            questionChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(
                reverse("polls:detailPoll", args=(question.poll.id,))
            )


def pronosticGroup(request, group_id):
    if request.method == "POST":
        group = get_object_or_404(Group, pk=group_id)
        if group.isPronoOver():
            # Redisplay the match pronosticing form.
            return render(
                request,
                "polls/detail.html",
                {
                    "group": group,
                    "error_message": "Il est trop tard pour pronostiquer sur ce group.",
                },
            )
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
            return render(
                request,
                "polls/detail.html",
                {
                    "group": group,
                    "error_message": "Vous n'avez pas rempli les 4 rangs.",
                },
            )
        else:
            groupChoice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(
                reverse("polls:detailPoll", args=(group.poll.id,))
            )


# def results(_, match_id):
#     response = "Vous regardez les résultats du match %s."
#     return HttpResponse(response % match_id)
