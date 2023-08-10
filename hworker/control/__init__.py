import random

import hworker.deliver as deliver
import hworker.publish as publish
import hworker.config as config
import hworker.depot as depot
import hworker.depot.objects as objects


def download_all():
    deliver.download_all()


def start_publish():
    publish.run_server()


def generate_scores():
    users = config.get_uids()
    tasks = config.get_tasks_list()
    depot.store(objects.Formula(ID=f"", timestamp=123, content=""))
    depot.store(objects.UserQualify(ID=f"", timestamp=123, name="User total", content=""))

    for task_id in tasks:
        depot.store(objects.TaskQualify(ID=f"{task_id}", TASK_ID=task_id, timestamp=123, name=task_id, content=""))

    for user_id in users:
        user_total = 0
        for task_id in tasks:
            cur_task = random.randint(1, 10)
            depot.store(
                objects.TaskScore(
                    ID=f"{user_id}{task_id}", USER_ID=user_id, TASK_ID=task_id, name=task_id, timestamp=123, rating=cur_task
                )
            )
            user_total += cur_task
        depot.store(objects.UserScore(ID=f"{user_id}", USER_ID=user_id, name="User total", timestamp=123, rating=user_total))
        depot.store(objects.FinalScore(ID=f"{user_id}", USER_ID=user_id, timestamp=123, rating=f"--{user_total}--"))
