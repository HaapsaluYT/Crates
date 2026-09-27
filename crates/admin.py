from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.forms import widgets
from django.utils.safestring import mark_safe
from query_builder_widget import QueryBuilderWidget

from .fields import POOL_FIELDS
from .models import Crate, CrateInstance, CratesSettings, Pool

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(Crate)
class CrateAdmin(admin.ModelAdmin):
    list_display = ("name", "emoji", "rarity", "amount_min", "amount_max", "openable")
    list_editable = ("rarity", "amount_min", "amount_max", "openable")
    search_fields = ("name",)
    autocomplete_fields = ("reward", "reward_groups", "specials", "pools")

    fieldsets = (
        (None, {"fields": ("name", "emoji_id", "rarity", "openable")}),
        (
            "Rewarding",
            {
                "description": "Fields for crate rewarding logic",
                "fields": ("reward", "reward_groups", "specials", "amount_min", "amount_max"),
            },
        ),
        ("Distribution", {"description": "Crate distribution fields", "fields": ("pools",)}),
        (
            "Behavior",
            {
                "description": "Fields for controlling crate behavior",
                "fields": ("respect_ball_rarity", "respect_special_rarity"),
            },
        ),
    )

    @admin.display(description="Emoji")
    def emoji(self, obj: Crate):
        if not obj.emoji_id:
            return ""

        return mark_safe(
            f'<img src="https://cdn.discordapp.com/emojis/{obj.emoji_id}.png?size=40" title="ID: {obj.emoji_id}" />'
        )


@admin.register(CrateInstance)
class CrateInstanceAdmin(admin.ModelAdmin):
    list_display = ("player", "crate", "earned_at")
    list_filter = ("earned_at",)
    list_select_related = ("player", "crate")
    search_fields = ("player__discord_id", "crate__name")
    date_hierarchy = "earned_at"
    readonly_fields = ("earned_at",)


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ("name", "cooldown", "enabled")
    list_editable = ("cooldown", "enabled")
    search_fields = ("name",)

    fieldsets = (
        (
            "Pool configuration",
            {
                "description": "Basic pool configuration.",
                "fields": ("name", "cooldown", "amount_min", "amount_max", "enabled"),
            },
        ),
        (
            "Command configuration",
            {"description": "Command configuration for the pool.", "fields": ("command_name", "command_description")},
        ),
        (
            "Advanced pool configuration",
            {
                "description": "Advanced pool configuration for controlling pool behavior.",
                "fields": ("conditions",),
                "classes": ("collapse",),
            },
        ),
    )

    formfield_overrides = {models.JSONField: {"widget": QueryBuilderWidget(POOL_FIELDS)}}


@admin.register(CratesSettings)
class CratesSettingsAdmin(admin.ModelAdmin):
    save_on_top = True
    formfield_overrides = {models.TextField: {"widget": widgets.TextInput}}

    fieldsets = (
        (
            "Personalization",
            {
                "description": "Basic package personalization.",
                "fields": ("crate_name", "plural_crate_name", "crates_slash_name"),
            },
        ),
        (
            "Advanced personalization",
            {"description": "Advanced package personalization.", "fields": ("menu_color",), "classes": ("collapse",)},
        ),
    )

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return super().has_add_permission(request) and not CratesSettings.objects.exists()

    def has_delete_permission(self, request: "HttpRequest", obj: CratesSettings | None = None) -> bool:
        return False
