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
MEETING_AUDIENCE_ROLES = ["Core Team", "Tech Team", "Solutions Team", "Social Media Team", "Event Team"]
MEETING_EVERYONE_ROLE = "Core Team"  # already covers everyone, so it can't be mixed with the others
# categories /meeting works in, right click a category > copy id
MEETING_CATEGORY_IDS = [
    881622737444040754,   # core channels (----🔑Team🔑----)
    1081183179400032307,  # bot testing
]
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
