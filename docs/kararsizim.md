# Kararsızım — Proje Spesifikasyonu ve Yol Haritası

Bu dosya projenin tek referans kaynağıdır. Kod yazmadan önce ilgili bölümü oku, bir şey burada yazmıyorsa varsayım yapıp ilerleme, sor.

---

## 1. Proje özeti

**Kararsızım**, insanların kararsız kaldıkları konuları soru haline getirip topluluğa oylattığı bir web uygulamasıdır.

Örnek kullanım: Kullanıcı "Bu akşam sinemaya mı gitsem restorana mı?" sorusunu yazar, 2 ila 5 arası seçenek ekler, paylaşır. Diğer kullanıcılar ana akışta bu soruyu görür, bir seçeneğe oy verir ve sonucu yüzde olarak görür.

**Temel ilkeler:**

- Takip mekanizması **yok**. Arkadaş, takipçi, bildirim akışı yok. Herkes platformdaki bütün anketleri görür.
- Anketleri **görüntülemek ve oy vermek için üyelik gerekmez**.
- **Anket oluşturmak için üyelik zorunludur.**
- Kayıt sırasında e-posta, parola ve kullanıcı adı alınır. Arayüzde **sadece kullanıcı adı** görünür, e-posta hiçbir yerde gösterilmez.
- Hedef çıktı bir **prototip**. Karmaşık altyapı, mikroservis, kuyruk sistemi, gerçek zamanlı websocket vb. yok. Önce çalışan bir ürün, sonra iyileştirme.

**Hedef kitle:** 16–30 yaş arası, mobil ağırlıklı kullanan, hızlı karar vermek isteyen genç kullanıcılar. Arayüz buna göre tasarlanacak.

---

## 2. Claude Code için çalışma kuralları

Bu kurallar her fazda geçerlidir.

1. **Fazları sırayla yap.** Bir fazın "bitti" kriterleri sağlanmadan sonrakine geçme.
2. **Bir seferde bir faz.** Kullanıcı açıkça istemeden birden fazla fazı birleştirme.
3. **Ekstra bağımlılık ekleme.** İzin verilen paket listesi Bölüm 4'te. Yeni bir pakete ihtiyaç duyarsan önce gerekçesiyle birlikte sor.
4. **Frontend framework yok.** React, Vue, Tailwind, Bootstrap, jQuery kullanılmayacak. Django template + saf CSS + saf JavaScript.
5. **Arayüz metinleri Türkçe.** Kod, değişken isimleri, fonksiyon isimleri, commit mesajları, yorumlar **İngilizce**. Model alan adları İngilizce.
6. **Migration'ları sen oluştur** ve dosyaları repoya ekle. `makemigrations` çıktısını kullanıcıya göster.
7. **Gizli anahtarları asla koda yazma.** Hepsi `.env` üzerinden, `.env.example` güncel tutulur, `.env` `.gitignore`'da.
8. Her fazın sonunda **ne yaptığını 5–10 maddede özetle** ve kullanıcının manuel yapması gereken adımları (Supabase'de şu ayarı aç, şu env değişkenini gir gibi) ayrı bir başlıkta listele.
9. **Testleri abartma.** Prototip aşamasında sadece kritik iş kuralları için test yaz (oy tekilliği, seçenek sayısı doğrulaması). Kapsam hedefi yok.
10. Emin olmadığın Vercel/Supabase yapılandırma detayları için **tahmin yürütme**, güncel dokümana bakılması gerektiğini söyle.

---

## 3. Teknoloji kararları

| Katman | Seçim | Not |
|---|---|---|
| Backend | Python 3.12 + Django 5.x | Template render + basit JSON uçları |
| Veritabanı | Supabase (PostgreSQL) | Django ORM ile doğrudan Postgres bağlantısı |
| Kimlik doğrulama | Django'nun kendi auth sistemi | Supabase Auth **kullanılmayacak** |
| Frontend | Django Templates + CSS + Vanilla JS | Aynı repo içinde, `static/` altında |
| Statik dosyalar | WhiteNoise | Vercel'de dosya sistemi salt-okunur |
| Dağıtım | Vercel (Python serverless) | |

**Neden Supabase Auth değil Django auth:** Prototipte tek bir kimlik kaynağı olması işi çok basitleştiriyor. Kullanıcı tablosu Django'nun `AUTH_USER_MODEL`'i olur, `request.user` her yerde çalışır, ekstra token senkronizasyonu gerekmez. Supabase burada sadece "yönetilen Postgres" olarak kullanılır.

**İzin verilen paketler:**

```
Django
psycopg2-binary
python-dotenv
dj-database-url
whitenoise
```

Bunların dışındaki her paket için önce onay al.

---

## 4. Dizin yapısı

```
kararsizim/
├── api/
│   └── index.py              # Vercel serverless giriş noktası
├── config/                   # Django proje ayarları
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # kullanıcı, kayıt, giriş
│   ├── models.py             # custom User
│   ├── forms.py
│   ├── views.py
│   └── urls.py
├── polls/                    # anketler, seçenekler, oylar
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── services.py           # oy verme iş mantığı burada
│   ├── urls.py
│   └── templatetags/
├── templates/
│   ├── base.html
│   ├── partials/
│   │   ├── header.html
│   │   ├── poll_card.html
│   │   └── toast.html
│   ├── accounts/
│   │   ├── register.html
│   │   └── login.html
│   └── polls/
│       ├── feed.html
│       ├── detail.html
│       ├── create.html
│       └── profile.html
├── static/
│   ├── css/
│   │   ├── tokens.css        # renk / tipografi / boşluk değişkenleri
│   │   ├── base.css          # reset, tipografi, layout
│   │   └── components.css    # kart, buton, bar, form
│   ├── js/
│   │   ├── vote.js           # oy verme fetch mantığı
│   │   └── create.js         # seçenek ekle/çıkar mantığı
│   └── img/
├── .env.example
├── .gitignore
├── requirements.txt
├── vercel.json
├── manage.py
└── CLAUDE.md
```

---

## 5. Veri modeli

Tüm modeller `created_at` alanı taşır. Birincil anahtar olarak anketlerde **UUID** kullanılır (URL'den sıralı id tahmin edilmesin, paylaşılabilir link doğal dursun).

### 5.1 User (`accounts.User`, `AbstractUser`'dan türer)

| Alan | Tip | Kural |
|---|---|---|
| `username` | CharField(24), unique | 3–24 karakter, sadece `a-z 0-9 _ .`, küçük harfe normalize edilir, başta/sonda `.` olamaz |
| `email` | EmailField, unique | Zorunlu. **Hiçbir şablonda gösterilmez** |
| `password` | Django hash | Min. 8 karakter, Django'nun varsayılan validator'ları açık |
| `created_at` | DateTimeField | |

Yasaklı kullanıcı adları listesi (`admin`, `kararsizim`, `destek`, `yonetim`, `root`, `api`) kod içinde sabit tutulur.

### 5.2 Poll (`polls.Poll`)

| Alan | Tip | Kural |
|---|---|---|
| `id` | UUIDField, pk | |
| `author` | FK → User, `on_delete=CASCADE`, `related_name="polls"` | Zorunlu |
| `question` | CharField(160) | 10–160 karakter |
| `category` | CharField(20), choices, nullable | Bkz. 5.5 |
| `total_votes` | PositiveIntegerField, default 0 | Denormalize sayaç |
| `is_closed` | BooleanField, default False | Sahibi kapatabilir |
| `created_at` | DateTimeField, `db_index=True` | |

`Meta.ordering = ["-created_at"]`

### 5.3 Option (`polls.Option`)

| Alan | Tip | Kural |
|---|---|---|
| `poll` | FK → Poll, CASCADE, `related_name="options"` | |
| `text` | CharField(60) | 1–60 karakter |
| `position` | PositiveSmallIntegerField | 0'dan başlar, sıralama için |
| `vote_count` | PositiveIntegerField, default 0 | Denormalize sayaç |

`Meta.ordering = ["position"]`, `unique_together = ("poll", "position")`

### 5.4 Vote (`polls.Vote`)

| Alan | Tip | Kural |
|---|---|---|
| `poll` | FK → Poll, CASCADE, `related_name="votes"` | |
| `option` | FK → Option, CASCADE, `related_name="votes"` | |
| `user` | FK → User, `null=True`, `on_delete=SET_NULL` | Üye oyu ise dolu |
| `voter_key` | CharField(64), `db_index=True` | Anonim oy ise dolu, üye oyunda boş string |
| `created_at` | DateTimeField | |

**Kısıtlar (`Meta.constraints`):**

```python
UniqueConstraint(fields=["poll", "user"],
                 condition=Q(user__isnull=False),
                 name="unique_vote_per_user_per_poll")

UniqueConstraint(fields=["poll", "voter_key"],
                 condition=Q(user__isnull=True),
                 name="unique_vote_per_anon_per_poll")
```

### 5.5 Kategoriler

Sabit liste, veritabanı tablosu değil. `polls/constants.py` içinde:

```
yemek      → Yeme içme
gezi       → Gezi
alisveris  → Alışveriş
iliskiler  → İlişkiler
kariyer    → Okul ve kariyer
gunluk     → Günlük hayat
diger      → Diğer
```

Kategori seçimi **isteğe bağlı**, boş bırakılırsa `diger` atanır.

---

## 6. Sayfa ve URL haritası

| URL | Ad | Erişim | İçerik |
|---|---|---|---|
| `/` | `feed` | Herkes | Anket akışı, sayfalama, kategori filtresi, sıralama |
| `/anket/<uuid>/` | `poll_detail` | Herkes | Tek anket, oy verme, sonuçlar, paylaş |
| `/anket/olustur/` | `poll_create` | Sadece üye | Anket oluşturma formu |
| `/anket/<uuid>/kapat/` | `poll_close` | Sadece sahibi | POST, anketi oylamaya kapatır |
| `/anket/<uuid>/sil/` | `poll_delete` | Sadece sahibi | POST, onaylı silme |
| `/u/<username>/` | `profile` | Herkes | Kullanıcının açtığı anketler |
| `/kayit/` | `register` | Misafir | |
| `/giris/` | `login` | Misafir | |
| `/cikis/` | `logout` | Üye | POST |
| `/hakkinda/` | `about` | Herkes | Kısa statik sayfa |
| `/api/anket/<uuid>/oy/` | `vote_api` | Herkes | POST JSON, oy kaydeder |

**Akış sıralama seçenekleri:** `yeni` (varsayılan, `-created_at`), `populer` (`-total_votes`), `sessiz` (`total_votes` artan — az oy almış anketler de görünsün diye).

Sayfalama: sayfa başına 20 anket, klasik `?sayfa=2` parametresi. Sonsuz kaydırma prototipte yok.

---

## 7. İş kuralları

### 7.1 Anket oluşturma

- Giriş yapmamış kullanıcı `/anket/olustur/` adresine giderse `/giris/?next=/anket/olustur/` adresine yönlendirilir.
- Seçenek sayısı **en az 2, en fazla 5**. Sunucu tarafında da doğrulanır, sadece JS'e güvenilmez.
- Aynı anket içinde **birebir aynı metinli iki seçenek** olamaz (karşılaştırma: boşlukları kırpılmış, küçük harfe çevrilmiş hali).
- Boş bırakılan seçenek kutuları yok sayılır, kalan sayı 2'nin altındaysa hata verilir.
- Soru metni 10–160 karakter. Sadece büyük harften oluşan sorular otomatik olarak normal yazıma çevrilmez, ama karakter sınırı uygulanır.
- **Hız sınırı:** Bir kullanıcı 24 saat içinde en fazla 10 anket açabilir. Aşılırsa anlaşılır bir hata mesajı gösterilir.

### 7.2 Oy verme

Oy verme mantığı `polls/services.py` içinde tek bir fonksiyonda toplanır: `cast_vote(request, poll, option) -> VoteResult`.

Adımlar:

1. Anket `is_closed` ise reddet.
2. `option.poll_id != poll.id` ise reddet.
3. Oy verenin kimliğini belirle:
   - `request.user.is_authenticated` → `user=request.user`, `voter_key=""`
   - Aksi halde → `voter_key = get_anon_key(request)`
4. `transaction.atomic()` içinde:
   - `Vote` kaydını oluştur (`IntegrityError` yakalanırsa "zaten oy verdin" sonucu döner).
   - `Option.objects.filter(pk=...).update(vote_count=F("vote_count") + 1)`
   - `Poll.objects.filter(pk=...).update(total_votes=F("total_votes") + 1)`
5. Güncel sonuçları döndür.

**Oy değiştirme prototipte yok.** Oy bir kez verilir. (v2 fikri.)

### 7.3 Anonim kullanıcı kimliği (`get_anon_key`)

```
1. Session boşsa oluştur (request.session.create()).
2. request.session içinde "anon_id" yoksa uuid4().hex üret ve yaz.
3. voter_key = sha256(anon_id + SECRET_SALT) → hex, ilk 64 karakter.
```

- IP adresi **saklanmaz**, hash'e dahil edilmez.
- Bu yöntem çerez silen veya farklı tarayıcı kullanan kişiyi engellemez. **Bu kabul edilmiş bir prototip sınırıdır**, kod içinde yorum olarak belirt. Gerçek kötüye kullanım önleme v2 işi.
- Session cookie ömrü: 1 yıl, `SESSION_COOKIE_SAMESITE = "Lax"`.

### 7.4 Sonuçların görünürlüğü

- Kullanıcı **oy vermeden önce** yüzdeleri görmez. Sadece seçenekleri ve toplam oy sayısını görür. Böylece çoğunluğa kapılma azalır.
- Oy verdikten sonra yüzdeler ve oy sayıları açılır, bar animasyonlu şekilde dolar.
- Anketin sahibi kendi anketinin sonuçlarını oy vermeden de görür.
- Kapatılmış anketlerde sonuçlar herkese açıktır, oy butonları pasiftir.
- Toplam oy 0 ise "İlk oyu sen ver" durumu gösterilir.

### 7.5 Silme ve kapatma

- Sadece anket sahibi silebilir/kapatabilir. Yetki kontrolü view içinde yapılır, sadece şablonda butonu gizlemek yeterli değildir.
- Silme işlemi onay ister ("Bu anket ve tüm oyları kalıcı olarak silinecek").
- Silme sonrası akışa yönlendirilir ve bilgi mesajı gösterilir.

---

## 8. Tasarım yönü

Bu bölüm bağlayıcıdır. Amaç, üretilmiş hissi veren jenerik "koyu zemin + mor-pembe gradyan + her şey aynı yuvarlak kart" görünümünden kaçınmak.

### 8.1 Fikir

Uygulamanın görsel çekirdeği **oy barının kendisi**. Kararsızlık iki seçenek arasında bir ağırlık meselesidir; bu yüzden en dikkat çekici, en kalın, en renkli eleman sonuç barları olacak. Geri kalan her şey sakin kalacak.

Her seçenek kendi rengini alır (1. seçenek hep aynı renk, 2. seçenek hep aynı renk...). Renk burada dekorasyon değil, bilgi taşır: bir seçeneği barda, listede ve rozette aynı renkten tanırsın.

Zemin açık, mürekkep koyu. Tek bir "büyük ve cesur" eleman var: soru metni. Sorular kartın içinde büyük puntoyla, sıkı satır aralığıyla yazılır — kart bir soru posteri gibi durur.

### 8.2 Renk (`static/css/tokens.css`)

```css
:root {
  --zemin:        #F2EFE9;  /* kırık beyaz, hafif sıcak */
  --yuzey:        #FFFFFF;
  --murekkep:     #171420;  /* metin ve çerçeveler */
  --murekkep-soft:#6B6577;  /* ikincil metin */
  --cizgi:        #171420;  /* kartların net konturu */

  /* seçenek renkleri — sırayla atanır */
  --secim-1: #2D4BFF;  /* mavi */
  --secim-2: #FF5436;  /* turuncu-kırmızı */
  --secim-3: #00A676;  /* yeşil */
  --secim-4: #B14BFF;  /* mor */
  --secim-5: #FFB300;  /* sarı */

  --hata:  #C7203C;
  --basari:#00A676;
}
```

Kurallar:

- Gradyan kullanma. Renkler düz ve tam doygunlukta.
- Kartların gölgesi yok; yerine **2px katı kontur** (`border: 2px solid var(--cizgi)`) ve 4px'lik katı ofset (`box-shadow: 4px 4px 0 var(--murekkep)`) kullan. Bu, yumuşak gri gölge klişesinden kaçınır ve mobilde net görünür.
- Köşe yarıçapı hiyerarşiye göre değişir: kart `14px`, buton `10px`, bar `6px`, avatar/rozet `999px`. Her şeye aynı radius verme.
- Koyu tema prototipte **yok**. `prefers-color-scheme` için basit bir invert yapmaya çalışma, v2 işi.

### 8.3 Tipografi

- Başlık ve soru metni: **Bricolage Grotesque** (Google Fonts), ağırlık 700, `letter-spacing: -0.02em`.
- Gövde, form, buton: **Inter Tight**, ağırlık 400/600.
- İki font da Google Fonts'tan `display=swap` ile yüklenir, sadece `latin` ve `latin-ext` alt kümesi (Türkçe karakterler için `latin-ext` şart).

Tip ölçeği:

```
soru (kart)    28px / 1.15
soru (detay)   40px / 1.1
seçenek metni  17px / 1.4
gövde          16px / 1.55
yardımcı       13px / 1.4
```

Kaçınılacaklar:

- Başlıkta tek bir kelimeyi renklendirme/italikleştirme.
- Her başlığın üstüne büyük harfli küçük etiket koyma.
- Buton metninin sonuna `→` ekleme.
- Satır uzunluğunu 70 karakteri geçirme.

### 8.4 Düzen

Mobil öncelikli. Tek sütun, maksimum genişlik `620px`, ortalanmış. Masaüstünde sütun genişlemez; boşluk kalır ve bu bilinçlidir — akış bir telefonda okunuyormuş gibi durur.

```
┌──────────────────────────────┐
│ Kararsızım      [Anket aç]   │  ← sabit üst bar, 56px
├──────────────────────────────┤
│ [Yeni] [Popüler] [Sessiz]    │  ← sıralama sekmeleri
│ [Tümü][Yemek][Gezi][...]     │  ← kategori çipleri, yatay kaydırılır
├──────────────────────────────┤
│ ┌──────────────────────────┐ │
│ │ @ensar · 2 saat önce     │ │
│ │                          │ │
│ │ Bu akşam sinemaya mı     │ │  ← büyük soru metni
│ │ gitsem restorana mı?     │ │
│ │                          │ │
│ │ ▢ Sinema                 │ │  ← oy öncesi: düz butonlar
│ │ ▢ Restoran               │ │
│ │                          │ │
│ │ 34 oy                    │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ ... sonraki anket        │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

Oy verildikten sonra aynı kart yerinde değişir:

```
│ ███████████████░░░░░  62%  │  Sinema      ✓ senin oyun
│ ████████░░░░░░░░░░░░  38%  │  Restoran
│ 35 oy                       │
```

Bar, seçenek metninin **arkasında** dolgu olarak değil, metnin üstünde ayrı bir şerit olarak durur — okunabilirlik için.

### 8.5 Hareket

Tek bir orchestrated an var: **oy verildiğinde barların soldan sağa dolması** (300ms, `cubic-bezier(.2,.8,.2,1)`, seçenekler 40ms arayla sırayla). Bunun dışında:

- Kartlara scroll ile giriş animasyonu **yok**.
- Hover efektlerini yalnızca butonlarda kullan (2px yukarı kayma + gölgenin küçülmesi).
- `@media (prefers-reduced-motion: reduce)` ile tüm geçişleri kapat.

### 8.6 Metin ve ton

- Sen dili, samimi ama abartısız. "Oy ver", "Anket aç", "Sonuçları gör".
- Buton adı sonuçla aynı: "Anket aç" → "Anketin açıldı".
- Hata mesajı özür dilemez, ne olduğunu ve ne yapılacağını söyler: "Bu kullanıcı adı alınmış. Başka bir tane dene."
- Boş durumlar davet eder: "Burada henüz anket yok. İlkini sen aç."
- Emoji arayüzde kullanılmaz (kullanıcının yazdığı soru metninde olabilir).

---

## 9. Fazlar

Her faz ayrı bir oturumda yapılabilir. Fazın sonunda "Bitti kriterleri" sağlanmadan sonrakine geçme.

---

### Faz 0 — Kurulum ve iskelet

**Amaç:** Yerelde çalışan boş bir Django projesi.

**Yapılacaklar:**
- Sanal ortam, `requirements.txt`.
- `django-admin startproject config .` yapısı, Bölüm 4'teki dizin yapısı.
- `accounts` ve `polls` uygulamaları oluşturulur (henüz model yok).
- `python-dotenv` ile `.env` okuma, `.env.example` yazılır.
- Geçici olarak **SQLite** ile çalış. Supabase bağlantısı Faz 5'te.
- `templates/base.html` iskeleti, `static/` klasörleri, boş CSS dosyaları.
- `/` adresinde "Kararsızım" yazan bir sayfa.
- `.gitignore` (`.env`, `__pycache__`, `db.sqlite3`, `staticfiles/`).

**Bitti kriteri:** `python manage.py runserver` çalışıyor, `/` açılıyor, `.env` okunuyor.

**Prompt:**
> CLAUDE.md dosyasındaki Faz 0'ı uygula. Bölüm 4'teki dizin yapısına birebir uy. Veritabanı şimdilik SQLite olsun, Supabase'i sonra bağlayacağız. Bitirince bana çalıştırma adımlarını yaz.

---

### Faz 1 — Veri modeli

**Amaç:** Bölüm 5'teki modellerin kurulması.

**Yapılacaklar:**
- `accounts.User` (custom, `AUTH_USER_MODEL` ayarlanır — **bu ilk migration'dan önce yapılmalı**).
- `polls.Poll`, `polls.Option`, `polls.Vote` + kısıtlar.
- `polls/constants.py` içinde kategoriler.
- Django admin'e üç modelin de kaydı (Option için `TabularInline`).
- Migration'lar oluşturulur ve uygulanır.
- Bir `seed` yönetim komutu: 5 kullanıcı, 20 anket, rastgele oylar üretir (`python manage.py seed`).

**Bitti kriteri:** Admin panelinden anket oluşturulabiliyor, seed komutu çalışıyor, oy tekillik kısıtı veritabanı seviyesinde mevcut.

**Prompt:**
> Faz 1'i uygula: CLAUDE.md Bölüm 5'teki modelleri oluştur. Kısıtları Meta.constraints ile veritabanı seviyesinde tanımla. Admin kayıtlarını ve seed komutunu da ekle.

---

### Faz 2 — Kimlik doğrulama

**Amaç:** Kayıt, giriş, çıkış.

**Yapılacaklar:**
- `RegisterForm`: kullanıcı adı, e-posta, parola, parola tekrar. Bölüm 5.1'deki kuralların hepsi doğrulanır. Yasaklı kullanıcı adı kontrolü.
- `LoginForm`: kullanıcı adı **veya** e-posta ile giriş (`ModelBackend` yerine basit bir custom backend ya da formda e-postayı username'e çevirme).
- `logout` sadece POST ile.
- `register.html` ve `login.html` şablonları, Bölüm 8'deki tasarım diline uygun.
- Başarılı kayıt → otomatik giriş → `next` varsa oraya, yoksa akışa.
- Üst barda giriş durumuna göre "Giriş yap" ya da "@kullanıcıadı" + çıkış.

**Bitti kriteri:** Kayıt olunabiliyor, çıkış/giriş yapılabiliyor, e-posta hiçbir sayfada görünmüyor, hatalar Türkçe ve anlaşılır.

**Prompt:**
> Faz 2'yi uygula: kayıt, giriş, çıkış akışını kur. Kullanıcı adı kurallarını ve yasaklı isim listesini Bölüm 5.1'e göre doğrula. Girişte hem kullanıcı adı hem e-posta kabul edilsin. Şablonlar Bölüm 8'deki tasarım diline uysun ama CSS'i şimdilik minimumda tut, asıl tasarımı Faz 6'da yapacağız.

---

### Faz 3 — Anket oluşturma

**Amaç:** Üyelerin anket açabilmesi.

**Yapılacaklar:**
- `PollForm` + `OptionFormSet` ya da elle yönetilen dinamik alanlar (formset karmaşık gelirse düz POST listesi de kabul).
- `create.js`: "Seçenek ekle" / "Kaldır" butonları, 2–5 sınırı, 5'te ekle butonu pasifleşir, 2'de kaldır butonu pasifleşir.
- Sunucu tarafı doğrulama: seçenek sayısı, boş seçenekler, tekrarlayan seçenekler, soru uzunluğu, 24 saatlik hız sınırı.
- Başarılı oluşturma → yeni anketin detay sayfasına yönlendirme + "Anketin açıldı" mesajı.
- Giriş yapmamış kullanıcı için yönlendirme.

**Bitti kriteri:** JS kapalıyken bile form çalışıyor (2 seçenekle), bütün doğrulamalar sunucuda geçerli.

**Prompt:**
> Faz 3'ü uygula: anket oluşturma formu ve dinamik seçenek alanları. Bölüm 7.1'deki bütün doğrulamaları sunucu tarafında uygula, JS'e güvenme. JavaScript devre dışıyken de form en az 2 seçenekle çalışsın.

---

### Faz 4 — Akış, detay ve oy verme

**Amaç:** Uygulamanın kalbi.

**Yapılacaklar:**
- `feed` view: sayfalama, kategori filtresi, sıralama sekmeleri. `select_related("author").prefetch_related("options")` ile N+1 önlenir.
- `poll_detail` view.
- `partials/poll_card.html`: hem akışta hem detayda kullanılır, oy öncesi ve sonrası iki durumu var.
- `polls/services.py` içinde `cast_vote` (Bölüm 7.2).
- `get_anon_key` (Bölüm 7.3).
- `/api/anket/<uuid>/oy/` JSON ucu: `{"option_id": ...}` alır, `{"ok": true, "results": [{"option_id":…, "count":…, "percent":…}], "total": …, "voted_option_id": …}` döner. CSRF token'ı header ile gönderilir.
- `vote.js`: butona basınca fetch atar, sonucu yerinde günceller, sayfa yenilenmez. **Fetch başarısız olursa** form normal POST'a düşer (progressive enhancement).
- Hangi anketlere oy verildiği bilgisi view'da toplu hesaplanır (tek sorguda), kart bazında sorgu atılmaz.
- Profil sayfası (`/u/<username>/`).
- Anket kapatma ve silme.

**Bitti kriteri:** Giriş yapmadan oy verilebiliyor, aynı tarayıcıdan ikinci oy engelleniyor, üye olarak oy verince de tekillik çalışıyor, oy öncesi yüzdeler görünmüyor.

**Prompt:**
> Faz 4'ü uygula: akış, detay sayfası, oy verme. Oy mantığını polls/services.py içinde tek fonksiyonda topla, view'a iş kuralı koyma. Bölüm 7.2, 7.3 ve 7.4'e birebir uy. Oy verildiğini gösteren bilgiyi akışta toplu sorguyla çöz, her kart için ayrı sorgu atma.

---

### Faz 5 — Supabase'e geçiş

**Amaç:** Veritabanını Supabase Postgres'e taşımak.

**Yapılacaklar:**
- `dj-database-url` ile `DATABASE_URL` okuma.
- Supabase'de iki farklı bağlantı dizesi kullanılır:
  - **Migration ve yerel geliştirme:** session pooler / doğrudan bağlantı.
  - **Vercel (serverless) üretim:** transaction pooler (port `6543`).
- Serverless için zorunlu ayarlar:
  ```python
  CONN_MAX_AGE = 0
  DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
  ```
  (Transaction mode pooler'da server-side cursor çalışmaz.)
- Migration'lar **yerelden** çalıştırılır, Vercel'de migration çalıştırılmaz.
- `.env.example` güncellenir.

**Kullanıcının manuel yapması gerekenler:** Supabase projesi açmak, Database Settings ekranından iki bağlantı dizesini kopyalamak, parolayı üretmek.

**Bitti kriteri:** Yerelde Supabase'e bağlı halde uygulama çalışıyor, seed verisi Supabase'de görünüyor.

**Prompt:**
> Faz 5'i uygula: veritabanını Supabase Postgres'e taşı. Yerel/migration ve serverless üretim için ayrı bağlantı dizesi mantığı kur, Bölüm 9 Faz 5'teki serverless ayarlarını ekle. .env.example'ı güncelle ve benim Supabase panelinde yapmam gereken adımları listele. Emin olmadığın bağlantı detaylarında tahmin yürütme, dokümana bakmam gerektiğini söyle.

---

### Faz 6 — Arayüz tasarımı

**Amaç:** Bölüm 8'deki tasarım dilinin tam olarak uygulanması.

**Yapılacaklar:**
- `tokens.css`, `base.css`, `components.css` yazılır.
- Kart, buton, form alanı, çip, bar, rozet, toast bileşenleri.
- Oy barı animasyonu.
- Mobil (360px) ve masaüstü kontrolü.
- Klavye odağı görünür (`:focus-visible` ile net kontur).
- `prefers-reduced-motion` desteği.
- Boş durumlar, hata durumları, yükleniyor durumu.
- Favicon ve basit bir logo (metin tabanlı olabilir).

**Bitti kriteri:** 360px genişlikte yatay kaydırma yok, kontrast oranları yeterli, Tab ile bütün etkileşimli öğelere ulaşılabiliyor.

**Prompt:**
> Faz 6'yı uygula: CLAUDE.md Bölüm 8'deki tasarım sistemini hayata geçir. Renk, tipografi, kontur ve bar kurallarına birebir uy — gradyan, yumuşak gri gölge ve her şeye tek radius verme. Önce token dosyasını yaz, sonra bileşenleri. Bitirince 360px ve 1280px görünümlerini kontrol et.

---

### Faz 7 — Vercel dağıtımı

**Amaç:** Canlıya almak.

**Yapılacaklar:**
- `api/index.py`:
  ```python
  from config.wsgi import application
  app = application
  ```
- `vercel.json` ile Python runtime ve yönlendirme yapılandırması.
- WhiteNoise: `MIDDLEWARE` içinde `SecurityMiddleware`'den hemen sonra, `STATICFILES_STORAGE` ayarı, build sırasında `collectstatic`.
- Üretim ayarları: `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` (Vercel alan adı), `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`.
- Vercel ortam değişkenleri listesi kullanıcıya verilir.

**Dikkat:** Vercel'de dosya sistemi salt-okunur ve arka plan işi yok. Migration, `createsuperuser` gibi komutlar yerelden Supabase'e karşı çalıştırılır.

**Bitti kriteri:** Canlı URL'de kayıt, anket açma ve oy verme çalışıyor; statik dosyalar yükleniyor.

**Prompt:**
> Faz 7'yi uygula: projeyi Vercel'e hazırla. api/index.py, vercel.json, WhiteNoise ve üretim güvenlik ayarlarını kur. Vercel panelinde girmem gereken ortam değişkenlerini tek tek listele. Vercel Python runtime yapılandırmasında emin olmadığın bir şey varsa güncel Vercel dokümanına bakmam gerektiğini söyle, tahmin etme.

---

### Faz 8 — Cila (isteğe bağlı)

Sırayla, ihtiyaca göre:

- Anket paylaşma: link kopyalama butonu, Open Graph meta etiketleri (paylaşılınca soru metni görünsün).
- Arama: soru metninde basit `icontains` araması.
- 404 ve 500 sayfaları.
- `robots.txt`, sitemap.
- Anket sahibi için "kendi anketlerim" listesi ve toplam oy istatistiği.
- Basit spam koruması: aynı `voter_key`'den dakikada oy sınırı.

---

## 10. Ortam değişkenleri

`.env.example` içeriği:

```
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
ANON_KEY_SALT=
```

- `ANON_KEY_SALT`: anonim oy hash'i için, `SECRET_KEY`'den ayrı tutulur.
- Üretimde `DJANGO_DEBUG=False` zorunlu.
- `.env` asla commit edilmez.

---

## 11. Prototipte kasıtlı olarak yapılmayanlar

Bunlar eksik değil, **kapsam dışı**. Claude Code bunları kendiliğinden eklememeli:

- Takip / arkadaş / bildirim sistemi
- Yorumlar
- Oy değiştirme veya geri alma
- E-posta doğrulama, parola sıfırlama
- Resimli anketler, çoklu seçim, süreli anketler
- Gerçek zamanlı canlı sonuç güncelleme (websocket)
- Koyu tema
- Çoklu dil desteği
- Admin moderasyon paneli, raporlama
- Mobil uygulama

---

## 12. Kabul kriterleri (prototip tamam sayılır)

- [ ] Misafir olarak ana sayfada anketleri görebiliyorum
- [ ] Misafir olarak oy verebiliyorum, aynı ankete ikinci kez veremiyorum
- [ ] Oy vermeden yüzdeleri göremiyorum
- [ ] Kayıt olabiliyorum, kullanıcı adım anketlerde görünüyor, e-postam hiçbir yerde görünmüyor
- [ ] Üye olarak 2–5 seçenekli anket açabiliyorum
- [ ] Sunucu tarafı doğrulamalar geçersiz girdileri reddediyor
- [ ] Kendi anketimi kapatıp silebiliyorum, başkasınınkini silemiyorum
- [ ] Telefonda düzgün görünüyor ve kullanılıyor
- [ ] Vercel'deki canlı adreste hepsi çalışıyor
