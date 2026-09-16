from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PollForm, clean_options
from .models import Option, Poll

DAILY_POLL_LIMIT = 10


def feed(request):
    return render(request, "polls/feed.html")


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, "polls/detail.html", {"poll": poll})


@login_required
def poll_create(request):
    option_errors = []

    if request.method == "POST":
        form = PollForm(request.POST)
        raw_options = request.POST.getlist("options")

        try:
            options = clean_options(raw_options)
        except ValidationError as exc:
            option_errors = exc.messages
            options = None

        if form.is_valid() and options is not None:
            since = timezone.now() - timedelta(hours=24)
            recent_count = Poll.objects.filter(
                author=request.user, created_at__gte=since
            ).count()

            if recent_count >= DAILY_POLL_LIMIT:
                option_errors = [
                    "24 saat içinde en fazla 10 anket açabilirsin. Biraz sonra tekrar dene."
                ]
            else:
                poll = Poll.objects.create(
                    author=request.user,
                    question=form.cleaned_data["question"],
                    category=form.cleaned_data["category"] or "diger",
                )
                for position, text in enumerate(options):
                    Option.objects.create(poll=poll, text=text, position=position)
                messages.success(request, "Anketin açıldı.")
                return redirect("polls:poll_detail", poll_id=poll.id)
    else:
        form = PollForm()
        raw_options = ["", ""]

    return render(
        request,
        "polls/create.html",
        {"form": form, "option_errors": option_errors, "raw_options": raw_options},
    )
