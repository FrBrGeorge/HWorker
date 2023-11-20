import random
from pathlib import Path

from .. import config, deliver, depot, make, publish, score


def download_all():
    """Download all solutions from several backends

    :return: -
    """
    deliver.download_all()


def start_publish():
    """Runs publish server

    :return: -
    """
    publish.run_server()


def generate_scores():
    """Example store generation

    :return: -
    """
    users = config.get_uids()
    tasks = config.get_tasks_list()
    depot.store(depot.objects.Formula(ID=f"", timestamp=123, content=""))
    names_for_qual = ["Attendance", "Score"]
    for name in names_for_qual:
        depot.store(depot.objects.UserQualifier(ID=f"{name}", timestamp=123, name=name, content=""))

        depot.store(depot.objects.TaskQualifier(ID=f"{name}", timestamp=123, name=name, content=""))

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
    """Example homeworks generation

    :return: -
    """
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
    """Perform qualifiers and get score results

    :return: -
    """
    score.create_files()
    score.read_and_import()
    score.perform_qualifiers()


def download_store_check_results():
    """Get check results from homeworks

    :return: -
    """
    deliver.download_all()
    make.parse_all_stored_homeworks()
    make.check_new_solutions()


def update_all():
    """Starts a full working system circle

    :return: -
    """
    download_store_check_results()
    do_score()


def big_red_button():
    """Perform full circle and start publishing

    :return: -
    """
    update_all()
    start_publish()


def generate_static_html():
    target_path = Path(config.get_publish_info()["static_folder"])
    target_path.mkdir(parents=True, exist_ok=True)
    publish.generate_static_html(target_path)
