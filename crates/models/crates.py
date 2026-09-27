from typing import TYPE_CHECKING

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from bd_models.models import Ball, BallGroup, Player, Special

from .pool import Pool
from .regex import EMOJI_ID_RE

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class Crate(models.Model):
    name = models.CharField(max_length=64, unique=True)

    emoji_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Optional emoji ID for this crate",
        validators=(RegexValidator(EMOJI_ID_RE, message="Invalid emoji ID."),),
    )

    rarity = models.FloatField(
        default=1.0, help_text="Weight used when randomly picking a crate to give.", validators=(MinValueValidator(0),)
    )

    reward = models.ManyToManyField(
        Ball,
        blank=True,
        help_text=(
            "The countryballs that can be given. Combined with any balls found in reward_groups. "
            "If both are blank, countryballs will be chosen at random."
        ),
    )

    reward_groups = models.ManyToManyField(
        BallGroup,
        blank=True,
        help_text=(
            "Groups of countryballs that can be given. Every ball in a group becomes an eligible "
            "reward option with any other individual balls selected above. Duplicates are removed."
        ),
    )

    specials = models.ManyToManyField(
        Special,
        blank=True,
        help_text=(
            "The specials that can be given. "
            "If blank, specials will be chosen at random with the same algorithm used when catching a ball."
        ),
    )

    respect_ball_rarity = models.BooleanField(
        default=False,
        help_text=(
            "If enabled, balls in the 'rewards' field are weighted by rarity when one is randomly selected, "
            "instead of each having an equal chance."
        ),
    )

    respect_special_rarity = models.BooleanField(
        default=False,
        help_text=(
            "If enabled, specials in the 'specials' field are weighted by rarity when one is randomly selected, "
            "instead of each having an equal chance."
        ),
    )

    amount_min = models.PositiveIntegerField(
        help_text="The minimum amount of countryballs that will be given.", validators=(MinValueValidator(1),)
    )

    amount_max = models.PositiveIntegerField(help_text="The maximum amount of countryballs that will be given.")
    openable = models.BooleanField(default=True, help_text="Whether this crate can be opened.")
    pools = models.ManyToManyField(Pool, blank=True, related_name="crates")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_max__gte=models.F("amount_min")), name="amount_max_gte_amount_min"
            ),
            models.CheckConstraint(condition=models.Q(amount_min__gte=1), name="amount_min_gte_1"),
        ]

    async def describe(self, bot: "BallsDexBot") -> str:
        if not self.emoji_id:
            return self.name

        emoji = bot.get_emoji(self.emoji_id)

        return f"{emoji} {self.name}"

    def __str__(self):
        return self.name


class CrateInstance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="crate_instances")
    crate = models.ForeignKey(Crate, on_delete=models.CASCADE, related_name="instances")
    earned_at = models.DateTimeField(auto_now_add=True)
