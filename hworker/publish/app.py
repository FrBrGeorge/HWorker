import datetime
from itertools import batched

from flask import Flask, request, render_template, redirect

from .lib import create_table
from .. import config, depot
from ..config import get_publish_info

app = Flask(__name__)
app.config.update(get_publish_info())


def _get_data_for_user(user_id: str):
    user_data: list = []

    final_score_names = list(map(lambda x: x.name, depot.search(depot.objects.Formula)))
    user_score_names = list(map(lambda x: x.name, depot.search(depot.objects.UserQualifier)))
    task_qualifiers = list(map(lambda x: x.name, depot.search(depot.objects.TaskQualifier)))
    task_score_names = {task_id: task_qualifiers for task_id in config.get_tasks_list()}

    for big_names, search_object in zip(
        [final_score_names, user_score_names, task_score_names],
        [depot.objects.FinalScore, depot.objects.UserScore, depot.objects.TaskScore],
    ):
        if type(big_names) == list:
            for name in big_names:
                score = depot.search(
                    search_object,
                    depot.objects.Criteria("USER_ID", "==", user_id),
                    depot.objects.Criteria("name", "==", name),
                    first=True,
                )
                user_data.append(None if score is None else score.rating)
        else:
            for task_id, names in big_names.items():
                for name in names:
                    score = depot.search(
                        search_object,
                        depot.objects.Criteria("TASK_ID", "==", task_id),
                        depot.objects.Criteria("USER_ID", "==", user_id),
                        depot.objects.Criteria("name", "==", name),
                        first=True,
                    )
                    user_data.append(None if score is None else score.rating)

    return user_data


@app.get("/")
def index():
    users = config.get_uids()
    data_per_user: dict[str, list] = dict()

    final_score_names = list(map(lambda x: x.name, depot.search(depot.objects.Formula)))
    user_score_names = list(map(lambda x: x.name, depot.search(depot.objects.UserQualifier)))
    task_score_names = {
        task_id: list(map(lambda x: x.name, depot.search(depot.objects.TaskQualifier)))
        for task_id in config.get_tasks_list()
    }

    for user_id in users:
        data_per_user[user_id] = _get_data_for_user(user_id)

    header: list = ["Users"]
    if len(final_score_names) != 0:
        header.append(final_score_names[0])
    type_pretty_names = ["User Qualifiers", "Task Qualifiers"]
    for type_index, big_names in enumerate([user_score_names, task_score_names]):
        header.append({type_pretty_names[type_index]: big_names})

    rows = [[key] + value for key, value in data_per_user.items()]

    return render_template(
        "index.html",
        table=create_table(header, rows),
        skip_prefix=len(final_score_names) + len(user_score_names) + 1,
        homework_names=",".join(config.get_tasks_list()),
    )


@app.post("/info")
def info():
    username, taskname = map(lambda x: request.form.get(x), ["username", "taskname"])
    if username is None or taskname is None:
        return redirect("/")

    objects_to_display = [
        depot.objects.Homework,
        depot.objects.Check,
        depot.objects.Solution,
        depot.objects.CheckResult,
    ]

    tables = dict()
    for cur_object in objects_to_display:
        find_objects = list(
            depot.search(
                cur_object,
                depot.objects.Criteria("USER_ID", "==", username.replace("\xa0", " ")),
                depot.objects.Criteria("TASK_ID", "==", taskname),
            )
        )

        data = [[value for key, value in item] for item in find_objects]

        tables[cur_object.__name__] = create_table([key for key, value in cur_object()], data)

    return render_template("student.html", username=username, taskname=taskname, tables=tables)


@app.route("/student/<user_id>", methods=["POST", "GET"])
def student(user_id):
    if user_id not in config.get_uids():
        return redirect("/")

    user_data: list = _get_data_for_user(user_id)

    user_score_names = list(map(lambda x: x.name, depot.search(depot.objects.UserQualifier)))
    task_qualifiers = list(map(lambda x: x.name, depot.search(depot.objects.TaskQualifier)))

    user_qual_table = create_table(
        ["Task name", *user_score_names], [["All tasks", *user_data[1 : 1 + len(user_score_names)]]]
    )

    task_qual_table = create_table(
        ["Task name", *task_qualifiers],
        [
            [task_name, *scores]
            for task_name, scores in zip(
                config.get_tasks_list(), batched(user_data[1 + len(user_score_names) :], len(task_qualifiers))
            )
        ],
    )
    return render_template(
        "student.html",
        tables={"User Qualifiers": user_qual_table, "Task Qualifiers": task_qual_table},
        username=user_id,
        final_mark=user_data[0] if len(user_data) > 0 else None,
    )


@app.get("/status")
def status():
    data: list[depot.objects.UpdateTime] = list(depot.search(depot.objects.UpdateTime))

    rows = list(
        map(lambda x: [x.name, datetime.datetime.fromtimestamp(x.timestamp).strftime("%H:%M:%S %d.%m.%Y")], data)
    )

    table = create_table(["Event type", "Date and time"], rows)

    return render_template("status.html", table=table)
