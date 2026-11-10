import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks
from setup import bot
from config import LOG_REMINDER_CHANNEL_ID, LOG_REMINDER_ROLE, MEETING_TIMEZONE

logger = logging.getLogger("GDSCommander.logReminder")

TZ = ZoneInfo(MEETING_TIMEZONE)  # same budapest time the meetings use

MESSAGE = """📢 Weekly Activity Log Reminder

Hey {mention}! 👋

It's Sunday, which means it's time to update your activity log for this week.

Please make sure to record the tasks you've worked on, your progress, any relevant updates and what you will be working on next week. This helps us keep track of our team's activities and project progress.

🗓️ Deadline: {deadline}

Please don't forget to fill it in before the deadline. Thanks for your cooperation! 🚀"""


@tasks.loop(time=time(12, 0, tzinfo=TZ))
async def send_log_reminder():
    # runs every day at noon, only sundays count
    now = datetime.now(TZ)
    if now.weekday() != 6:
        return
    channel = bot.get_channel(LOG_REMINDER_CHANNEL_ID)
    if channel is None:
        logger.warning("Can't see the log reminder channel, check LOG_REMINDER_CHANNEL_ID")
        return
    role = discord.utils.get(channel.guild.roles, name=LOG_REMINDER_ROLE)
    # tuesday 00:00, the midnight between monday and tuesday
    deadline = datetime.combine(now.date() + timedelta(days=2), time(0, 0), tzinfo=TZ)
    try:
        await channel.send(
            MESSAGE.format(
                mention=role.mention if role else f"@{LOG_REMINDER_ROLE}",
                # shows in everyone's own timezone, plus "in 2 days"
                deadline=f"{discord.utils.format_dt(deadline, 'F')} ({discord.utils.format_dt(deadline, 'R')})",
            ),
            allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=[role] if role else False),
        )
    except discord.HTTPException:
        logger.exception("Couldn't send the weekly log reminder")


@bot.listen("on_ready")
async def start_log_reminder():
    # on_ready fires again after reconnects, so only start once
    if not send_log_reminder.is_running():
        send_log_reminder.start()
