import random
import uuid

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from accounts.models import User
from polls.models import Option, Poll, Vote

USERNAMES = ["ensar", "defne", "kerem", "sude", "baran"]

SAMPLE_POLLS = [
    ("Bu akşam sinemaya mı gitsem restorana mı?", ["Sinema", "Restoran"], "gunluk"),
    ("Tatilde deniz mi dağ mı?", ["Deniz", "Dağ"], "gezi"),
    ("Yeni telefon mu alsam yoksa tasarruf mu etsem?", ["Telefon al", "Tasarruf et"], "alisveris"),
    ("Staj teklifi: büyük şirket mi küçük startup mı?", ["Büyük şirket", "Küçük startup"], "kariyer"),
    ("Bu hafta sonu aileme mi gitsem arkadaşlarımla mı takılsam?", ["Aile", "Arkadaşlar"], "iliskiler"),
    ("Öğle yemeği: pizza mı döner mi lahmacun mu?", ["Pizza", "Döner", "Lahmacun"], "yemek"),
    ("Yeni bir diziye mi başlasam eski bir filmi mi tekrar izlesem?", ["Yeni dizi", "Eski film"], "gunluk"),
    ("Kahve mi çay mı?", ["Kahve", "Çay"], "yemek"),
    ("Spor salonuna mı yazılsam evde mi spor yapsam?", ["Spor salonu", "Evde spor"], "gunluk"),
    ("Yaz stajını yurt dışında mı yapsam yurt içinde mi?", ["Yurt dışı", "Yurt içi"], "kariyer"),
    ("Kitap mı sesli kitap mı?", ["Kitap", "Sesli kitap"], "gunluk"),
    ("Doğum günü hediyesi: kıyafet mi teknoloji mi deneyim mi?", ["Kıyafet", "Teknoloji", "Deneyim"], "alisveris"),
    ("Hafta sonu kampta mı otelde mi kalınmalı?", ["Kamp", "Otel"], "gezi"),
    ("İlişkide anlaşmazlıkta önce mi konuşmalı yoksa önce mi soğumalı?", ["Önce konuş", "Önce soğu"], "iliskiler"),
    ("Sabah mı gece mi ders çalışmak daha verimli?", ["Sabah", "Gece"], "kariyer"),
    ("Tatlıda baklava mı sütlaç mı?", ["Baklava", "Sütlaç"], "yemek"),
    ("Yeni evde üst kat mı zemin kat mı daha iyi?", ["Üst kat", "Zemin kat"], "gunluk"),
    ("Arkadaş grubu tatili yurt dışında mı yurt içinde mi olmalı?", ["Yurt dışı", "Yurt içi"], "gezi"),
    ("İş görüşmesine takım elbise mi rahat kıyafet mi giyilmeli?", ["Takım elbise", "Rahat kıyafet"], "kariyer"),
    ("Sevgiliye sürpriz: çiçek mi yemek mi hediye mi?", ["Çiçek", "Yemek", "Hediye"], "iliskiler"),
]


class Command(BaseCommand):
    help = "Örnek kullanıcı, anket ve oy verisi üretir."

    def handle(self, *args, **options):
        with transaction.atomic():
            users = self._create_users()
            polls = self._create_polls(users)
            self._create_votes(users, polls)
        self.stdout.write(
            self.style.SUCCESS(f"{len(users)} kullanıcı, {len(polls)} anket oluşturuldu.")
        )

    def _create_users(self):
        users = []
        for username in USERNAMES:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            if created:
                user.set_password("kararsizim123")
                user.save()
            users.append(user)
        return users

    def _create_polls(self, users):
        polls = []
        for question, option_texts, category in SAMPLE_POLLS:
            author = random.choice(users)
            poll = Poll.objects.create(author=author, question=question, category=category)
            for position, text in enumerate(option_texts):
                Option.objects.create(poll=poll, text=text, position=position)
            polls.append(poll)
        return polls

    def _create_votes(self, users, polls):
        for poll in polls:
            options = list(poll.options.all())
            voters = [user for user in users if user != poll.author]
            for user in random.sample(voters, random.randint(1, len(voters))):
                option = random.choice(options)
                self._record_vote(poll, option, user=user)
            for _ in range(random.randint(0, 5)):
                option = random.choice(options)
                self._record_vote(poll, option, voter_key=uuid.uuid4().hex)

    def _record_vote(self, poll, option, user=None, voter_key=""):
        Vote.objects.create(poll=poll, option=option, user=user, voter_key=voter_key)
        Option.objects.filter(pk=option.pk).update(vote_count=F("vote_count") + 1)
        Poll.objects.filter(pk=poll.pk).update(total_votes=F("total_votes") + 1)
