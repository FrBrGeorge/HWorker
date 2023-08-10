from collections import defaultdict

from flask import Flask, request, render_template, redirect

from .lib import create_table
from .. import config, depot
from ..config import get_publish_info

app = Flask(__name__)
app.config.update(get_publish_info())


@app.post("/info/")
def info():
    username, taskname = map(lambda x: request.form.get(x), ["username", "taskname"])
    if username is None or taskname is None:
        return redirect("/")

    objects_to_display = [
        depot.objects.Homework,
        depot.objects.Check,
        depot.objects.Solution,
        depot.objects.CheckResult,
        depot.objects.TaskScore,
    ]

    tables = dict()
    for cur_object in objects_to_display:
        find_objects = [
            *depot.search(
                cur_object,
                depot.objects.Criteria("USER_ID", "==", username),
                depot.objects.Criteria("TASK_ID", "==", taskname),
            )
        ]
        if len(find_objects) == 0:
            find_objects.append(cur_object())

        data = defaultdict(list)
        for item in find_objects:
            for key, value in item:
                data[key].append(value)
        tables[cur_object.__name__] = create_table(data)

    return render_template("info.html", username=username, taskname=taskname, tables=tables)


@app.get("/")
def index():
    users = config.get_uids()
    data_per_user: dict[str, list] = defaultdict(list)

    final_score_names = [*map(lambda x: x.name, depot.search(depot.objects.Formula))]
    user_score_names = [*map(lambda x: x.name, depot.search(depot.objects.UserQualify))]
    task_score_names = [*map(lambda x: x.name, depot.search(depot.objects.TaskQualify))]

    for user_id in users:
        for names, search_object in zip(
            [final_score_names, user_score_names, task_score_names],
            [depot.objects.FinalScore, depot.objects.UserScore, depot.objects.TaskScore],
        ):
            for name in names:
                score = depot.search(
                    search_object,
                    depot.objects.Criteria("USER_ID", "==", user_id),
                    depot.objects.Criteria("name", "==", name),
                    first=True,
                )
                data_per_user[user_id].append(score.rating)

    data = defaultdict(list)
    data["Names"] = users
    for cur_index in range(sum(map(len, [final_score_names, user_score_names, task_score_names]))):
        cur_name = sum([final_score_names, user_score_names, task_score_names], [])[cur_index]
        for user_id in users:
            data[cur_name].append(data_per_user[user_id][cur_index])

    # data = {
    #     "Name": ["Vania", "Petya", "Vasiliy"],
    #     "Final score": ["33", "44", "55"],
    #     "Score1": list(range(5, 8)),
    #     "Score2": list(range(3, 6)),
    #     "Score3": list(range(1, 4)),
    #     "Score4": list(range(7, 10)),
    #     "Score5": list(range(8, 11)),
    # }

    return render_template(
        "index.html", table=create_table(data), skip_prefix=len(final_score_names) + len(user_score_names)
    )
