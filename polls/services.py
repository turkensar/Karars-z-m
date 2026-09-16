import hashlib
import uuid
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F

from .models import Option, Poll, Vote


@dataclass
class VoteResult:
    ok: bool
    error: Optional[str] = None


def get_anon_key(request):
    if not request.session.session_key:
        request.session.create()
    anon_id = request.session.get("anon_id")
    if not anon_id:
        anon_id = uuid.uuid4().hex
        request.session["anon_id"] = anon_id
    raw = f"{anon_id}{settings.ANON_KEY_SALT}".encode()
    return hashlib.sha256(raw).hexdigest()[:64]


def cast_vote(request, poll, option):
    """Bolum 7.2'deki oy verme akisini uygular."""
    if poll.is_closed:
        return VoteResult(ok=False, error="closed")
    if option.poll_id != poll.id:
        return VoteResult(ok=False, error="invalid_option")

    if request.user.is_authenticated:
        user = request.user
        voter_key = ""
    else:
        user = None
        voter_key = get_anon_key(request)

    try:
        with transaction.atomic():
            Vote.objects.create(poll=poll, option=option, user=user, voter_key=voter_key)
            Option.objects.filter(pk=option.pk).update(vote_count=F("vote_count") + 1)
            Poll.objects.filter(pk=poll.pk).update(total_votes=F("total_votes") + 1)
    except IntegrityError:
        return VoteResult(ok=False, error="already_voted")

    return VoteResult(ok=True)


def get_voted_option_map(request, poll_ids):
    """Verilen anket id listesi icin gecerli ziyaretcinin oy verdigi secenekleri tek sorguda dondurur."""
    if not poll_ids:
        return {}
    if request.user.is_authenticated:
        votes = Vote.objects.filter(poll_id__in=poll_ids, user=request.user)
    else:
        anon_key = get_anon_key(request)
        votes = Vote.objects.filter(poll_id__in=poll_ids, voter_key=anon_key, user__isnull=True)
    return {vote.poll_id: vote.option_id for vote in votes}


def serialize_results(poll):
    total = poll.total_votes
    results = {}
    for option in poll.options.all():
        percent = round((option.vote_count / total) * 100) if total else 0
        results[option.id] = {"count": option.vote_count, "percent": percent}
    return results, total


def build_poll_context(request, polls):
    """Bir veya daha fazla anket icin gosterim bilgisini (sonuc gorunurlugu, oy verilen secenek,
    yuzdeler) tek sorguda hesaplar. Kart basina ayri sorgu atmamak icin feed/detail/profile
    view'larinca ortak kullanilir."""
    polls = list(polls)
    poll_ids = [poll.id for poll in polls]
    voted_option_by_poll = get_voted_option_map(request, poll_ids)

    context = {}
    for poll in polls:
        voted_option_id = voted_option_by_poll.get(poll.id)
        is_owner = request.user.is_authenticated and poll.author_id == request.user.id
        show_results = bool(voted_option_id) or poll.is_closed or is_owner
        results_by_option = {}
        if show_results:
            results_by_option, _ = serialize_results(poll)
        context[poll.id] = {
            "show_results": show_results,
            "voted_option_id": voted_option_id,
            "results_by_option": results_by_option,
        }
    return context
