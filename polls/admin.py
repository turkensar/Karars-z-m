from django.contrib import admin

from .models import Option, Poll, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "category", "total_votes", "is_closed", "created_at")
    list_filter = ("category", "is_closed")
    search_fields = ("question", "author__username")
    inlines = [OptionInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("poll", "option", "user", "voter_key", "created_at")
    list_filter = ("poll",)
