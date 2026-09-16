import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User

from .constants import CATEGORY_CHOICES
from .forms import PollForm, clean_options
from .models import Option, Poll
from .services import build_poll_context, cast_vote

DAILY_POLL_LIMIT = 10
PAGE_SIZE = 20
SORT_OPTIONS = {
    "yeni": "-created_at",
    "populer": "-total_votes",
    "sessiz": "total_votes",
}


def feed(request):
    sort = request.GET.get("sirala", "yeni")
    if sort not in SORT_OPTIONS:
        sort = "yeni"
    category = request.GET.get("kategori", "")

    polls_qs = Poll.objects.select_related("author").prefetch_related("options")
    if category:
        polls_qs = polls_qs.filter(category=category)
    polls_qs = polls_qs.order_by(SORT_OPTIONS[sort])

    paginator = Paginator(polls_qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get("sayfa"))

    poll_context = build_poll_context(request, page.object_list)

    return render(
        request,
        "polls/feed.html",
        {
            "page": page,
            "sort": sort,
            "category": category,
            "categories": CATEGORY_CHOICES,
            "poll_context": poll_context,
        },
    )


def poll_detail(request, poll_id):
    poll = get_object_or_404(
        Poll.objects.select_related("author").prefetch_related("options"), pk=poll_id
    )
    ctx = build_poll_context(request, [poll])[poll.id]
    return render(
        request,
        "polls/detail.html",
        {
            "poll": poll,
            "show_results": ctx["show_results"],
            "voted_option_id": ctx["voted_option_id"],
            "results_by_option": ctx["results_by_option"],
        },
    )


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


@login_required
@require_POST
def poll_close(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if poll.author_id != request.user.id:
        raise PermissionDenied
    poll.is_closed = True
    poll.save(update_fields=["is_closed"])
    messages.success(request, "Anketin kapatıldı.")
    return redirect("polls:poll_detail", poll_id=poll.id)


@login_required
@require_POST
def poll_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if poll.author_id != request.user.id:
        raise PermissionDenied
    poll.delete()
    messages.info(request, "Anket silindi.")
    return redirect("polls:feed")


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    polls_qs = (
        Poll.objects.filter(author=profile_user)
        .select_related("author")
        .prefetch_related("options")
    )
    paginator = Paginator(polls_qs, PAGE_SIZE)
    page = paginator.get_page(request.GET.get("sayfa"))
    poll_context = build_poll_context(request, page.object_list)

    return render(
        request,
        "polls/profile.html",
        {"profile_user": profile_user, "page": page, "poll_context": poll_context},
    )


@require_POST
def vote_api(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    is_json_request = request.content_type == "application/json"

    if is_json_request:
        try:
            payload = json.loads(request.body)
            option_id = int(payload["option_id"])
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return JsonResponse({"ok": False, "error": "invalid_request"}, status=400)
    else:
        option_id = request.POST.get("option_id")
        if option_id is None:
            return HttpResponseBadRequest("option_id gerekli.")

    option = get_object_or_404(Option, pk=option_id)
    result = cast_vote(request, poll, option)

    if not result.ok:
        if is_json_request:
            status = 409 if result.error == "already_voted" else 400
            return JsonResponse({"ok": False, "error": result.error}, status=status)
        return redirect("polls:poll_detail", poll_id=poll.id)

    if not is_json_request:
        return redirect("polls:poll_detail", poll_id=poll.id)

    poll.refresh_from_db()
    ctx = build_poll_context(request, [poll])[poll.id]
    results = [
        {"option_id": option_id, "count": data["count"], "percent": data["percent"]}
        for option_id, data in ctx["results_by_option"].items()
    ]
    return JsonResponse(
        {
            "ok": True,
            "results": results,
            "total": poll.total_votes,
            "voted_option_id": ctx["voted_option_id"],
        }
    )
