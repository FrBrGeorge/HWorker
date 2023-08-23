from datetime import datetime
from hworker.config import get_task_info


def validator(solution):
    date = datetime.fromtimestamp(solution.timestamp)
    if date > get_task_info(solution.TASK_ID)["hard_deadline"]:
        return 0.25
    if date > get_task_info(solution.TASK_ID)["soft_deadline"]:
        return 0.5
    return 1.0
