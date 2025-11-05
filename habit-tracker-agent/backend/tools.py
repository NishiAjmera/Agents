import json
from datetime import datetime

HABIT_LOG_FILE = "habit_log.json"


def log_habit(type: str, details: str):
    """
    Logs a user's habit to a JSON file.

    Args:
        type (str): The type of habit (e.g., 'workout', 'meal').
        details (str): A description of the habit (e.g., 'ran 5 km').
    """
    try:
        with open(HABIT_LOG_FILE, "r") as f:
            habits = json.load(f)
    except FileNotFoundError:
        habits = []

    habits.append(
        {"timestamp": datetime.now().isoformat(), "type": type, "details": details}
    )

    with open(HABIT_LOG_FILE, "w") as f:
        json.dump(habits, f, indent=2)

    return f"Successfully logged habit: {type} - {details}"


def get_summary(period: str):
    """
    Returns a summary of logged habits for a given period.

    Args:
        period (str): The period to summarize (e.g., 'daily', 'weekly').
    """
    try:
        with open(HABIT_LOG_FILE, "r") as f:
            habits = json.load(f)
    except FileNotFoundError:
        return "No habits logged yet."

    # This is a simple summary. A more advanced implementation would
    # filter by the requested period.
    if not habits:
        return "No habits logged yet."

    summary = "Here's a summary of your recent habits:\n"
    for habit in habits[-5:]:
        summary += f"- {habit['timestamp']}: {habit['type']} - {habit['details']}\n"

    return summary
