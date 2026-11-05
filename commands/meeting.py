import logging
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote, urlencode, urlparse
from zoneinfo import ZoneInfo

import discord
from discord import app_commands, Interaction, Embed, SelectOption
from discord.ui import View, Modal, TextInput, Button
from setup import bot
from database import save_meeting
from config import (
    MEETING_ORGANIZER_ROLES, MEETING_AUDIENCE_ROLES, MEETING_EVERYONE_ROLE, MEETING_CATEGORY_ID,
    MEETING_TIMEZONE, MEETING_FIRST_SLOT, MEETING_LAST_SLOT, MEETING_DEFAULT_DURATION,
)

logger = logging.getLogger("GDSCommander.meeting")

TZ = ZoneInfo(MEETING_TIMEZONE)
# minutes -> what the dropdown shows
DURATIONS = {15: "15 min", 30: "30 min", 45: "45 min", 60: "1 hour", 90: "1.5 hours", 120: "2 hours", 180: "3 hours"}
MAX_QUICK_PICKS = 24  # discord caps dropdowns at 25 options, the last one is "other"
OTHER = "other"  # dropdown value for "let me type it"
EXPIRED = "This panel expired, run /meeting again."


def find_named(items, name):
    # roles are matched by name, caps don't matter
    return next((item for item in items if item.name.lower() == name.lower()), None)


def time_slots():
    # every 30 min from the first slot to the last
    slot = datetime.combine(date.today(), time.fromisoformat(MEETING_FIRST_SLOT))
    last = datetime.combine(date.today(), time.fromisoformat(MEETING_LAST_SLOT))
    slots = []
    while slot <= last and len(slots) < MAX_QUICK_PICKS:
        slots.append(slot.time())
        slot += timedelta(minutes=30)
    return slots


SLOTS = time_slots()  # worked out once when the bot starts


def parse_time(text):
    # takes 18:15, 18.15 and 9:00
    return datetime.strptime(text.replace(".", ":"), "%H:%M").time()


def day_label(day, today):
    # "Today · Thu 5 Nov", "Tomorrow · Fri 6 Nov", then just "Sat 7 Nov"
    label = f"{day:%a} {day.day} {day:%b}"
    return {0: f"Today · {label}", 1: f"Tomorrow · {label}"}.get((day - today).days, label)


def default_title(roles):
    # "Tech Team meeting", "Tech Team and Event Team meeting", "A, B and C meeting"
    names = [role.name for role in roles]
    if not names:
        return "New meeting"
    joined = names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"
    return f"{joined} meeting"


def is_https(link):
    # good enough for discord to accept it as a button link
    parsed = urlparse(link)
    return parsed.scheme == "https" and bool(parsed.netloc) and " " not in link


def calendar_url(base, params, details_key, details):
    # discord rejects button links over 512 chars, so the details get trimmed till it fits
    while len(url := base + urlencode({**params, details_key: details}, quote_via=quote)) > 512 and details:
        details = details[:-25]
    return url if len(url) <= 512 else None


# the private panel, it remembers everything picked so far
class MeetingPanel(View):
    def __init__(self, interaction, audience):
        super().__init__(timeout=600)  # 10 min of nothing and it expires
        self.organizer = interaction.user
        self.channel = interaction.channel
        self.last_interaction = interaction  # what we edit when it times out
        self.audience = audience
        self.everyone = find_named(audience, MEETING_EVERYONE_ROLE)
        self.today = datetime.now(TZ).date()
        # what the organizer fills in, empty till they pick something
        self.roles = []
        self.day = None
        self.start = None
        self.duration = MEETING_DEFAULT_DURATION
        self.title = ""
        self.description = ""
        self.room = ""
        self.link = ""
        self.note = None  # one-off message for the next render
        self.posting = False
        self.refresh()

    def starts_at(self):
        # picked date + time, in budapest time
        return datetime.combine(self.day, self.start, tzinfo=TZ)

    def missing(self):
        # anything in here keeps create! greyed out
        missing = []
        if not self.roles:
            missing.append("who it's for")
        if not self.day:
            missing.append("a date")
        if not self.start:
            missing.append("a time")
        if self.day and self.start and self.starts_at() <= datetime.now(TZ):
            missing.append("a time that isn't in the past")
        if not (self.room or self.link):
            missing.append("a room or link (✏️ Details)")
        if self.link and not is_https(self.link):
            missing.append("a link starting with https://")
        return missing

    def status(self):
        # the text above the preview
        lines = ["**New meeting** · only you can see this"]
        if self.note:
            lines.append(f"ℹ️ {self.note}")
        missing = self.missing()
        lines.append("Still needed: " + ", ".join(missing) if missing else "Looks good! Hit **Create!** to post it.")
        # roles that aren't mentionable only get pinged if the bot has the "mention everyone" perm
        can_ping_all = self.channel.permissions_for(self.channel.guild.me).mention_everyone
        quiet = [role.name for role in self.roles if not (role.mentionable or can_ping_all)]
        if quiet:
            lines.append(f"⚠️ {', '.join(quiet)} won't actually get pinged, turn on \"Allow anyone to @mention this role\" in the role settings.")
        return "\n".join(lines)

    def embed(self):
        # same embed for the preview and the real post, so what you see is what you get :)
        embed = Embed(title=self.title or default_title(self.roles), description=self.description or None, color=discord.Color.blue())
        when = "Not set yet"
        if self.day and self.start:
            start = self.starts_at()
            # discord turns these into each person's own timezone
            when = f"{discord.utils.format_dt(start, 'F')} ({discord.utils.format_dt(start, 'R')})"
        embed.add_field(name="🗓 When", value=when, inline=False)
        embed.add_field(name="⏱ Duration", value=DURATIONS[self.duration])
        embed.add_field(name="📍 Where", value="\n".join(filter(None, [self.room, self.link])) or "Not set yet")
        embed.add_field(name="👥 For", value=" ".join(role.mention for role in self.roles) or "Not set yet", inline=False)
        embed.add_field(name="Organized by", value=self.organizer.mention, inline=False)
        return embed

    def links(self, title, start, end):
        # calendars want utc
        start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
        where = ", ".join(filter(None, [self.room, self.link]))
        google = calendar_url(
            "https://calendar.google.com/calendar/render?",
            {"action": "TEMPLATE", "text": title, "dates": f"{start:%Y%m%dT%H%M%SZ}/{end:%Y%m%dT%H%M%SZ}", "location": where},
            "details", self.description,
        )
        outlook = calendar_url(
            "https://outlook.live.com/calendar/0/action/compose?",
            {"rru": "addevent", "subject": title, "startdt": f"{start:%Y-%m-%dT%H:%M:%SZ}", "enddt": f"{end:%Y-%m-%dT%H:%M:%SZ}", "location": where},
            "body", self.description,
        )
        # plain link buttons, so they keep working even after the bot restarts
        view = View(timeout=None)
        for label, url in [("Join meeting", self.link), ("Add to Google Calendar", google), ("Add to Outlook", outlook)]:
            if url:
                view.add_item(Button(label=label, url=url))
        return view

    def refresh(self):
        # rebuild the dropdowns so they show what's picked
        self.audience_select.options = [SelectOption(label=role.name, value=str(role.id), default=role in self.roles) for role in self.audience]
        self.audience_select.max_values = len(self.audience)

        # a typed date that isn't in the list shows up as the "other" option instead
        days = [self.today + timedelta(days=i) for i in range(MAX_QUICK_PICKS)]
        typed_day = self.day is not None and self.day not in days
        self.date_select.options = [
            *(SelectOption(label=day_label(day, self.today), value=day.isoformat(), default=day == self.day) for day in days),
            SelectOption(label=f"Other · {day_label(self.day, self.today)}" if typed_day else "Other date...", value=OTHER, default=typed_day),
        ]

        typed_time = self.start is not None and self.start not in SLOTS
        self.time_select.options = [
            *(SelectOption(label=f"{slot:%H:%M}", value=slot.isoformat(), default=slot == self.start) for slot in SLOTS),
            SelectOption(label=f"Other · {self.start:%H:%M}" if typed_time else "Other time...", value=OTHER, default=typed_time),
        ]

        self.duration_select.options = [SelectOption(label=label, value=str(minutes), default=minutes == self.duration) for minutes, label in DURATIONS.items()]
        self.create_button.disabled = bool(self.missing())

    async def update(self, interaction):
        # every change ends up here and redraws the panel
        if self.is_finished():
            # the modal outlived the panel ¯\_(ツ)_/¯
            await interaction.response.send_message(EXPIRED, ephemeral=True)
            return
        self.last_interaction = interaction
        self.refresh()
        content = self.status()
        self.note = None  # notes only show once
        await interaction.response.edit_message(content=content, embed=self.embed(), view=self)

    @discord.ui.select(placeholder="Who is this meeting for?", min_values=1, row=0)
    async def audience_select(self, interaction: Interaction, select: discord.ui.Select):
        picked = [role for role in self.audience if str(role.id) in select.values]
        # core team already means everyone, so it wins over the rest
        if self.everyone in picked and len(picked) > 1:
            picked = [self.everyone]
            self.note = f"{self.everyone.name} already covers everyone, so I dropped the others."
        self.roles = picked
        await self.update(interaction)

    @discord.ui.select(placeholder="Date", row=1)
    async def date_select(self, interaction: Interaction, select: discord.ui.Select):
        # "other" opens the typing form, which redraws the panel itself
        if select.values[0] == OTHER:
            await interaction.response.send_modal(TypedModal(self, "day", "Date", "YYYY-MM-DD", date.fromisoformat))
            return
        self.day = date.fromisoformat(select.values[0])
        await self.update(interaction)

    @discord.ui.select(placeholder="Start time", row=2)
    async def time_select(self, interaction: Interaction, select: discord.ui.Select):
        if select.values[0] == OTHER:
            await interaction.response.send_modal(TypedModal(self, "start", "Time", "HH:MM", parse_time))
            return
        self.start = time.fromisoformat(select.values[0])
        await self.update(interaction)

    @discord.ui.select(placeholder="Duration", row=3)
    async def duration_select(self, interaction: Interaction, select: discord.ui.Select):
        self.duration = int(select.values[0])
        await self.update(interaction)

    @discord.ui.button(label="Details", emoji="✏️", style=discord.ButtonStyle.secondary, row=4)
    async def details_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DetailsModal(self))

    @discord.ui.button(label="Create!", style=discord.ButtonStyle.success, row=4)
    async def create_button(self, interaction: Interaction, button: discord.ui.Button):
        # double clicks are real lol
        if self.posting:
            await interaction.response.defer()
            return
        # the panel can sit open long enough for the time to pass
        if self.missing():
            await self.update(interaction)
            return
        self.posting = True

        start = self.starts_at()
        end = start + timedelta(minutes=self.duration)
        embed = self.embed()
        # pings have to go in the text, mentions inside an embed don't notify anyone
        try:
            message = await self.channel.send(
                " ".join(role.mention for role in self.roles),
                embed=embed,
                view=self.links(embed.title, start, end),
                allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=self.roles),
            )
        except discord.HTTPException:
            logger.exception("Couldn't post a meeting")
            self.posting = False
            await interaction.response.send_message("Couldn't post the meeting here, do I have permission to send messages in this channel?", ephemeral=True)
            return

        self.stop()
        await interaction.response.edit_message(content=f"Posted ✅ {message.jump_url}", embed=None, view=None)
        # saved after replying, so a db hiccup can't make a posted meeting look failed
        save_meeting(
            interaction.guild_id, self.channel.id, message.id, self.organizer.id, [role.id for role in self.roles],
            start.astimezone(timezone.utc).isoformat(), self.duration, embed.title, self.description, self.room, self.link,
        )
        logger.info(f"Meeting '{embed.title}' posted by {self.organizer}")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=4)
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button):
        # throw it all away
        self.stop()
        await interaction.response.edit_message(content="Meeting creation cancelled.", embed=None, view=None)

    async def on_timeout(self):
        try:
            await self.last_interaction.edit_original_response(content=EXPIRED, embed=None, view=None)
        except discord.HTTPException:
            pass  # they already dismissed it, nothing to tidy up


# the pop-up for title, description, room and link
class DetailsModal(Modal, title="Meeting details"):
    meeting_title = TextInput(label="Title", placeholder="Leave empty for e.g. \"Tech Team meeting\"", required=False, max_length=100)
    description = TextInput(label="Description", style=discord.TextStyle.paragraph, required=False, max_length=1000)
    room = TextInput(label="Room (if in person)", placeholder="e.g. Q building, QBF13", required=False, max_length=100)
    link = TextInput(label="Link (if online)", placeholder="https://meet.google.com/...", required=False, max_length=200)

    def __init__(self, panel):
        super().__init__()
        self.panel = panel
        # prefill with what's already there, so editing doesn't wipe it
        self.meeting_title.default = panel.title
        self.description.default = panel.description
        self.room.default = panel.room
        self.link.default = panel.link

    async def on_submit(self, interaction: Interaction):
        self.panel.title = self.meeting_title.value.strip()
        self.panel.description = self.description.value.strip()
        self.panel.room = self.room.value.strip()
        self.panel.link = self.link.value.strip()
        await self.panel.update(interaction)


class TypedModal(Modal):
    # for when the dropdown doesn't have the date or time you want
    def __init__(self, panel, attr, label, hint, parse):
        super().__init__(title=f"Type a {label.lower()}")
        self.panel = panel
        self.attr = attr
        self.hint = hint
        self.parse = parse
        self.answer = TextInput(label=label, placeholder=hint, max_length=10)
        self.add_item(self.answer)

    async def on_submit(self, interaction: Interaction):
        try:
            value = self.parse(self.answer.value.strip())
        except ValueError:
            await interaction.response.send_message(f"Couldn't read that, use {self.hint}.", ephemeral=True)
            return
        setattr(self.panel, self.attr, value)  # attr is "day" or "start"
        await self.panel.update(interaction)


@bot.tree.command(name="meeting", description="Set up a meeting and ping the people in it")
@app_commands.guild_only()
async def meeting(interaction: Interaction):
    logger.info(f"Received /meeting from {interaction.user}")
    # heads and admins only
    if not any(find_named(interaction.user.roles, name) for name in MEETING_ORGANIZER_ROLES):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # and only in the core channels (threads count too)
    if interaction.channel.category_id != MEETING_CATEGORY_ID:
        await interaction.response.send_message("You can only use /meeting in the core channels.", ephemeral=True)
        return

    # every audience role has to exist on this server, handy when setting up a test server
    audience = [find_named(interaction.guild.roles, name) for name in MEETING_AUDIENCE_ROLES]
    missing = [name for name, role in zip(MEETING_AUDIENCE_ROLES, audience) if role is None]
    if missing:
        await interaction.response.send_message(f"I can't find these roles on this server: {', '.join(missing)}", ephemeral=True)
        return

    panel = MeetingPanel(interaction, audience)
    await interaction.response.send_message(panel.status(), embed=panel.embed(), view=panel, ephemeral=True)
