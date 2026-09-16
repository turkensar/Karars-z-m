from django import forms

from .constants import CATEGORY_CHOICES

MIN_OPTIONS = 2
MAX_OPTIONS = 5
MAX_OPTION_LENGTH = 60


class PollForm(forms.Form):
    question = forms.CharField(label="Soru", min_length=10, max_length=160)
    category = forms.ChoiceField(
        label="Kategori",
        choices=[("", "Kategori seç (isteğe bağlı)")] + CATEGORY_CHOICES,
        required=False,
    )


def clean_options(raw_options):
    """Validate a raw list of submitted option texts and return the cleaned list.

    Raises forms.ValidationError on any rule violation from spec Bolum 7.1.
    """
    texts = [text.strip() for text in raw_options if text.strip()]

    if len(texts) < MIN_OPTIONS:
        raise forms.ValidationError(f"En az {MIN_OPTIONS} seçenek girmelisin.")
    if len(texts) > MAX_OPTIONS:
        raise forms.ValidationError(f"En fazla {MAX_OPTIONS} seçenek ekleyebilirsin.")

    seen = set()
    for text in texts:
        if len(text) > MAX_OPTION_LENGTH:
            raise forms.ValidationError("Seçenek metni en fazla 60 karakter olabilir.")
        key = text.lower()
        if key in seen:
            raise forms.ValidationError("Aynı metinli iki seçenek olamaz.")
        seen.add(key)

    return texts
