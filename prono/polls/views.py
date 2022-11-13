from .models import Match, Poll
from django.shortcuts import get_object_or_404, render

def indexPolls(request):
    polls = Poll.objects.all()
    context = {'polls': polls}
    return render(request, 'polls/index.html', context)


def detailPoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def detailMatch(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, 'matchs/detail.html', {'match': match})

# def results(_, match_id):
#     response = "Vous regardez les résultats du match %s."
#     return HttpResponse(response % match_id)

# def vote(_, match_id):
#     return HttpResponse("Vous pronostiquez le match %s." % match_id)
