from bs4 import BeautifulSoup


def encode_to_str(to_encode: any) -> str:
    return str(to_encode).replace(" ", "\xa0")


def create_table(data: dict[str, list]) -> str:
    """
    :param data: All data, where keys in ordered correctly and value in list of data
    :rtype: object Return html string
    """
    lens = [len(value) for key, value in data.items()]
    if not lens or any([cur_len != lens[0] for cur_len in lens]):
        raise ValueError("Invalid data got on input")

    soup = BeautifulSoup()

    soup.append(
        table := soup.new_tag("table", attrs={"class": "table table-hover table-striped table-bordered align-middle"})
    )

    table.append(thead := soup.new_tag("thead"))
    table.append(tbody := soup.new_tag("tbody"))

    thead.append(head_tr := soup.new_tag("tr"))
    # thead content

    for head_name in data.keys():
        th = soup.new_tag("th", attrs={"scope": "col"})
        th.string = encode_to_str(head_name)
        head_tr.append(th)

    for index in range(lens[0]):
        tbody.append(body_tr := soup.new_tag("tr"))

        for elem in data.values():
            th = soup.new_tag("th")
            th.string = "Nope" if elem[index] is None else encode_to_str(elem[index])
            body_tr.append(th)
        # for homework_name in homeworks_names_and_files.keys():
        #     cur_task = submitted_tasks.get(homework_name, None)
        #     if cur_task is not None:
        #         if cur_task.grade == int(configs["Rating grades"]["on_time"]):
        #             color = "bg-success"
        #         elif cur_task.grade == int(configs["Rating grades"]["week"]):
        #             color = "bg-warning"
        #         elif cur_task.grade == int(configs["Rating grades"]["fortnight"]):
        #             color = "bg-danger"
        #         elif cur_task.is_plagiary and not cur_task.is_broken:
        #             # not original and not broken
        #             color = "bg-primary"
        #         else:
        #             # broken
        #             color = "bg-info"
        #         elem = soup.new_tag("th", attrs={"class": color})
        #         elem.string = cur_task.creation_date.strftime("%d\xa0%b\xa0%H:%M")
        #     else:
        #         elem = soup.new_tag("th")
        #         elem.string = "Nope"
        #     body_tr.append(elem)
        # elem = soup.new_tag("th")
        # elem.string = str(sum([task.grade for task in submitted_tasks.values()]))
        # body_tr.append(elem)

    return str(soup)
