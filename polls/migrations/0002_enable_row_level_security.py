from django.db import migrations

# Supabase, public semadaki her tabloyu varsayilan olarak kendi otomatik REST
# API'siyle (anon/authenticated rolleri) disariya aciyor. Bu proje Supabase'e
# sadece yonetilen Postgres olarak baglaniyor (Supabase Auth/REST API
# kullanilmiyor), o API yolunu tamamen kapatmak icin RLS aciliyor.
#
# Django, tablo sahibi rolle (DATABASE_URL'deki rol) baglandigi icin RLS'den
# etkilenmez -- FORCE ROW LEVEL SECURITY ayarlanmadigi surece tablo sahibi
# RLS'yi bypass eder. Bu yuzden bu degisiklik uygulamanin calismasini
# etkilemez, sadece Supabase'in disariya actigi API'den erisimi kapatir.

TABLES = [
    "accounts_user",
    "accounts_user_groups",
    "accounts_user_user_permissions",
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
    "polls_poll",
    "polls_option",
    "polls_vote",
]


def enable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;')


def disable_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("polls", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("sessions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]
