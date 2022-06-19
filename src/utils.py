import datetime

from discord.ext import commands


class CoolDownError(commands.CommandError):
    def __init__(self, message):
        self.message = message


def format_time(dt: datetime.timedelta):
    """
    Formats a timedelta object into a string

    :param dt: timedelta object
    :return: string
    """
    ret = ""
    days = dt.seconds // 86400
    hours = (dt.seconds % 86400) // 3600
    minutes = (dt.seconds % 3600) // 60
    seconds = dt.seconds % 60
    if days > 0:
        ret += f"{days} days "
    if hours > 0:
        ret += f"{hours} hours "
    if minutes > 0:
        ret += f"{minutes} minutes "
    if seconds > 0:
        ret += f"{seconds} seconds "
    return ret


def cooldown(seconds=0, minutes=0, hours=0, days=0):
    """
    A decorator that adds a cooldown to a command.

    :param seconds: number of seconds
    :param minutes: number of minutes
    :param hours: number of hours
    :param days: number of days
    :return: a decorator
    """
    timestamp_now = datetime.datetime.now().timestamp()

    async def predicate(ctx):
        cooldowns = await ctx.bot.db.players.find_one(
            {"_id": ctx.author.id, "cooldowns.command_name": ctx.command.name}
        )
        if cooldowns:
            cooldowns = cooldowns["cooldowns"]
            # get the command from cooldowns list
            for cooldown in cooldowns:
                # print(cooldown, ctx.command.name)
                if (
                    cooldown["command_name"]
                    == ctx.command.parent.name + ctx.command.name
                    if ctx.command.parent
                    else ctx.command.name
                ):
                    # get the cooldown time
                    cooldown_timestamp: int = cooldown["cooldown_time"]
                    # get the cooldown end time
                    cooldown_dt: datetime.datetime = datetime.datetime.fromtimestamp(
                        cooldown_timestamp
                    )
                    # get how much time is left until the cooldown is over

                    # if the difference is greater than the cooldown time, return True
                    if datetime.datetime.now() > cooldown_dt:
                        return True
                    else:
                        formatted_time = format_time(
                            cooldown_dt - datetime.datetime.now()
                        )
                        raise CoolDownError(
                            f"You can use this command again in {formatted_time}"
                        )

        else:  # set up a new cooldowns array
            cooldown_timestamp = seconds + minutes * 60 + hours * 3600 + days * 86400
            cooldown_dt = datetime.datetime.fromtimestamp(
                timestamp_now + cooldown_timestamp
            )
            cooldown_data = {
                "command_name": ctx.command.parent.name + ctx.command.name
                if ctx.command.parent
                else ctx.command.name,
                "cooldown_time": cooldown_dt.timestamp(),
            }
            ctx.bot.db.players.update_one(
                {"_id": ctx.author.id},
                {"$push": {"cooldowns": cooldown_data}},
                upsert=True,
            )
            return True

    return commands.check(predicate)


def all_casings(input_string: str):
    """
    Converts a string into all possible casings

    :param input_string: string to convert
    :return: a generator of strings
    """
    if not input_string:
        yield ""
    else:
        first = input_string[:1]
        if first.lower() == first.upper():
            for sub_casing in all_casings(input_string[1:]):
                yield first + sub_casing
        else:
            for sub_casing in all_casings(input_string[1:]):
                yield first.lower() + sub_casing
                yield first.upper() + sub_casing


def get_pet_data(ctx, pet_type):
    for pet_data in ctx.bot.pet_shop_items:
        if pet_type == pet_data["type"]:
            return pet_data
    return None


def get_item(ctx, item_name):
    for isle, isle_items in ctx.bot.shop_items.items():
        for item in isle_items:
            if item_name == item["name"]:
                return item
    return None
