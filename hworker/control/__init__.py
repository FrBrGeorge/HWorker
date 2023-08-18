import random

from .. import check, config, deliver, depot, log, make, publish, score


def download_all():
    deliver.download_all()


def start_publish():
    publish.run_server()


def generate_scores():
    users = config.get_uids()
    tasks = config.get_tasks_list()
    depot.store(depot.objects.Formula(ID=f"", timestamp=123, content=""))
    names_for_qual = ["Attendance", "Score"]
    for name in names_for_qual:
        depot.store(depot.objects.UserQualifier(ID=f"{name}", timestamp=123, name=name, content=""))

        for task_id in tasks:
            depot.store(
                depot.objects.TaskQualifier(
                    ID=f"{task_id}/{name}", TASK_ID=task_id, timestamp=123, name=name, content=""
                )
            )

    for user_id in users:
        score_total = 0
        attend_total = 0
        for task_id in tasks:
            score = random.randint(1, 10)
            attend = random.randint(0, 1)
            for name_index, name in enumerate(names_for_qual):
                depot.store(
                    depot.objects.TaskScore(
                        ID=f"{user_id}/{task_id}/{name}",
                        USER_ID=user_id,
                        TASK_ID=task_id,
                        name=name,
                        timestamp=123,
                        rating=attend if name_index == 0 else score,
                    )
                )
            score_total += score
            attend_total += attend

        for rating, name in zip([attend_total, score_total], names_for_qual):
            depot.store(
                depot.objects.UserScore(
                    ID=f"{user_id}/{name}", USER_ID=user_id, name=name, timestamp=123, rating=rating
                )
            )
        depot.store(
            depot.objects.FinalScore(ID=f"{user_id}", USER_ID=user_id, timestamp=123, rating=f"--{score_total}--")
        )


def generate_homeworks_with_versions():
    for user_id in ["Vania", "Petya", "Vasili"]:
        for task_id in ["01", "02", "03"]:
            for ts in range(10, 31, 10):
                depot.store(
                    depot.objects.Homework(
                        ID=f"t{user_id}{task_id}",
                        USER_ID=user_id,
                        TASK_ID=task_id,
                        timestamp=ts,
                        content={},
                        is_broken=False,
                    )
                )


def do_score():
    score.create_files()
    score.read_and_import()
    score.perform_qualifiers()


def store_check_results():
    deliver.download_all()
    make.parse_store_all_homeworks()
    make.check_all_solutions()
