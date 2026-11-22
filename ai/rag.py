'''finds what /ask should know for a question, just a stub until the real rag lands'''
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str  # where it came from, shown under the answer, e.g. "faq.md"
    score: float = 1.0  # how well it matches the question, higher is better


# stand-in knowledge, basically what /about says
CLUB_BASICS = """GDGoC BME (Google Developer Groups on Campus BME, formerly GDSC BME) is a club at BME (Budapest University of Technology and Economics) where techy people meet each other and learn new technologies. It bridges the gap between theory and practice and gives like-minded people a welcoming community.

The club has members and core members. Members hear about the latest events and announcements of the club and of Google, and are part of the community on the Discord server. Core members keep the club alive, create events, decide what goes on in the club and contribute to its internal projects.

The core team is 4 teams and a lead (or co-leads): the event team, the solutions team, the tech team and the social media team. You can learn more about each one with /event-team, /solutions-team, /tech-team and /social-media-team."""


async def retrieve(question: str, k: int = 5) -> list[Chunk]:
    # stub: same chunk whatever you ask :) the real one returns the k best matches
    return [Chunk(CLUB_BASICS, "about")]
