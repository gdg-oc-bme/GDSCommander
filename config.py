# Superthread Configuration & ID Mapping
TEAM_ID = "t3SJYXJN"
PROJECT_ID = "2"
BASE_URL = "https://api.superthread.com/v1"

# Boards Mapping
BOARDS = {
    "Tech Team": "4",
    "Social Media Team": "5",
    "Solutions Team": "6",
    "Event Team": "7"
}

# Column Names (Standard for your workspace)
COLUMN_NAMES = ["Ideas", "To-do", "Doing", "Done", "Canceled"]

# Column ID Mapping for each Board
BOARD_COLUMNS = {
    "4": ["16", "17", "18", "19", "20"], # Tech
    "5": ["21", "22", "23", "24", "25"], # Social Media
    "6": ["26", "27", "28", "29", "30"], # Solutions
    "7": ["31", "32", "33", "34", "35"]  # Event
}

# /meeting (names are matched ignoring caps)
MEETING_ORGANIZER_ROLES = ["Admin", "Club Lead", "Tech Team Head", "Solutions Team Head", "Social Media Team Head", "Event Team Head"]
MEETING_TESTERS = [335783692175802368]  # user ids that skip the role check, temporary, remove before merging
MEETING_TEST_CHANNELS = [1153008384925253682]  # channels that skip the category check (bot testing), also temporary
MEETING_AUDIENCE_ROLES = ["Core Member", "Tech Team", "Solutions Team", "Social Media Team", "Event Team"]
MEETING_EVERYONE_ROLE = "Core Member"  # already covers everyone, so it can't be mixed with the others
# core channels category, right click the category > copy id
MEETING_CATEGORY_ID = 881622737444040754 # category ID for category containing core channels (----🔑Team🔑----)
MEETING_TIMEZONE = "Europe/Budapest"
MEETING_FIRST_SLOT = "09:00"
MEETING_LAST_SLOT = "20:30"
MEETING_DEFAULT_DURATION = 60  # minutes, has to be one of the DURATIONS in commands/meeting.py

def get_column_id(board_id, column_name):
    """Helper to find the specific API ID for a column name on a board."""
    if board_id not in BOARD_COLUMNS:
        return None
    try:
        idx = COLUMN_NAMES.index(column_name)
        return BOARD_COLUMNS[board_id][idx]
    except (ValueError, IndexError):
        return None
