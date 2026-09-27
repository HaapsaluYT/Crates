from typing import TYPE_CHECKING

from ..models import get_settings
from .cog import Crates
from .core.utils.translator import CrateTranslator

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    settings = await get_settings()

    cog = Crates(bot)
    assert cog.app_command
    cog.app_command.name = settings.crates_slash_name

    replacements = {"crates": settings.plural_crate_name, "crate": settings.crate_name}

    current = bot.tree.translator

    if current is not None and not isinstance(current, CrateTranslator):
        await bot.tree.set_translator(CrateTranslator(current, replacements))

    await bot.add_cog(cog)


async def teardown(bot: "BallsDexBot"):
    current = bot.tree.translator

    if isinstance(current, CrateTranslator):
        await bot.tree.set_translator(current.inner)
