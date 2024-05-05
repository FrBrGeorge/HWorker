from datetime import datetime
from hworker.config import get_task_info
from hworker.make import fit_deadline


# def validator(solution):
#    date = datetime.fromtimestamp(solution.timestamp)
#    if date > get_task_info(solution.TASK_ID)["hard_deadline"]:
#        return 0.25
#    if date > get_task_info(solution.TASK_ID)["soft_deadline"]:
#        return 0.5
#    return 1.0


def validator(solution):
    if fit_deadline(solution, get_task_info(solution.TASK_ID)["soft_deadline"]):
        return 1.0
    elif fit_deadline(solution, get_task_info(solution.TASK_ID)["hard_deadline"]):
        return 0.5
    return 0.25
