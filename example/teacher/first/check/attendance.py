from datetime import datetime
from hworker.config import get_task_info


def version_validator(solutions):
    first_solution = list(solutions)[0]
    date = datetime.fromtimestamp(first_solution.timestamp)
    if date > get_task_info(first_solution.TASK_ID)["open_date"]:
        return 0.0
    return 1.0
