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
    hours = dt.seconds // 3600
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
    cooldown_in_seconds = seconds + minutes * 60 + hours * 3600 + days * 86400

    async def predicate(ctx):
        cooldowns = await ctx.bot.db.players.find_one(
            {"_id": ctx.author.id, "cooldowns.command_name": ctx.command.name}
        )
        if cooldowns:
            cooldowns = cooldowns["cooldowns"]
            # get the current time
            now: datetime.datetime = datetime.datetime.now()
            # get the command from cooldowns list
            for cooldown in cooldowns:
                # print(cooldown, ctx.command.name)
                if cooldown["command_name"] == ctx.command.name:
                    # get the cooldown time
                    cooldown_time: int = cooldown["cooldown_time"]
                    # get how much time is left until the cooldown is over
                    time_left: datetime.timedelta = datetime.timedelta(
                        seconds=cooldown_time
                    ) - (
                        now - datetime.datetime.fromtimestamp(cooldown["cooldown_time"])
                    )
                    # if the difference is greater than the cooldown time, return True
                    if time_left.seconds > cooldown_in_seconds:
                        return True
                    else:
                        formatted_time = format_time(time_left)
                        raise CoolDownError(
                            f"You can use this command again in {formatted_time}"
                        )

        else:  # set up a new cooldowns array
            cooldown_data = {
                "command_name": ctx.command.name,
                "cooldown_time": cooldown_in_seconds,
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
