from django.shortcuts import render


def feed(request):
    return render(request, "polls/feed.html")
