import random

from ballsdex.packages.countryballs.countryball import BallSpawnView
from ballsdex.settings import settings
from bd_models.models import Ball, BallInstance, Player, Special, balls

from ...models import CrateInstance


def _select_reward(reward: list[Ball], respect_rarity: bool) -> Ball:
    weights = [ball.rarity for ball in reward] if respect_rarity else None

    return random.choices(population=reward, weights=weights, k=1)[0]


def _select_special(specials: list[Special], respect_rarity: bool) -> Special | None:
    if not specials:
        return BallSpawnView.get_random_special()

    weights = [special.rarity for special in specials] if respect_rarity else None

    return random.choices(population=specials, weights=weights, k=1)[0]


async def open_crate(crate_instance: CrateInstance, player: Player) -> list[BallInstance]:
    instances: list[BallInstance] = []
    crate = crate_instance.crate

    specials = [special async for special in crate.specials.all()]

    reward_balls: dict[int, Ball] = {}
    async for ball in crate.reward.all():
        reward_balls[ball.pk] = ball
    async for group in crate.reward_groups.all():
        async for ball in group.balls.all():
            reward_balls[ball.pk] = ball
    reward = list(reward_balls.values())

    respect_ball_rarity = crate.respect_ball_rarity and bool(reward)
    respect_special_rarity = crate.respect_special_rarity and bool(specials)

    if not reward:
        reward = [ball for ball in balls.values() if ball.enabled]

    for _ in range(random.randint(crate.amount_min, crate.amount_max)):
        ball_instance = await BallInstance.objects.acreate(
            ball=_select_reward(reward, respect_ball_rarity),
            player=player,
            special=_select_special(specials, respect_special_rarity),
            attack_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
            health_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
        )

        instances.append(ball_instance)

    return instances
