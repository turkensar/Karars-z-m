from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm
from .models import User


def _safe_next_url(request, next_url):
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return None


def register(request):
    if request.user.is_authenticated:
        return redirect("polls:feed")

    next_url = _safe_next_url(request, request.POST.get("next") or request.GET.get("next"))

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Hesabın oluşturuldu, hoş geldin.")
            return redirect(next_url or "polls:feed")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form, "next": next_url})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("polls:feed")

    next_url = _safe_next_url(request, request.POST.get("next") or request.GET.get("next"))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["identifier"].strip()
            password = form.cleaned_data["password"]

            if "@" in identifier:
                try:
                    username = User.objects.get(email__iexact=identifier).username
                except User.DoesNotExist:
                    username = identifier
            else:
                username = User.normalize_username(identifier)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(next_url or "polls:feed")
            form.add_error(None, "Kullanıcı adı, e-posta veya parola hatalı.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.info(request, "Çıkış yapıldı.")
    return redirect("polls:feed")
