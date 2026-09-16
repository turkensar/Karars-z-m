from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.Form):
    username = forms.CharField(label="Kullanıcı adı", max_length=24)
    email = forms.EmailField(label="E-posta")
    password1 = forms.CharField(label="Parola", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Parola (tekrar)", widget=forms.PasswordInput)

    def clean_username(self):
        username = User.normalize_username(self.cleaned_data.get("username", ""))
        temp_user = User(username=username)
        try:
            temp_user.full_clean(exclude=["email", "password", "first_name", "last_name"])
        except ValidationError as exc:
            raise forms.ValidationError(list(exc.message_dict.get("username", exc.messages)))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta zaten kayıtlı.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        temp_user = User(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
        )
        try:
            password_validation.validate_password(password1, user=temp_user)
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)
        return password1

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Parolalar birbiriyle eşleşmiyor.")
        return cleaned

    def save(self):
        user = User(username=self.cleaned_data["username"], email=self.cleaned_data["email"])
        user.set_password(self.cleaned_data["password1"])
        user.save()
        return user


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Kullanıcı adı veya e-posta")
    password = forms.CharField(label="Parola", widget=forms.PasswordInput)
