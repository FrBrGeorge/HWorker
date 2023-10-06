from bs4 import BeautifulSoup


def encode_to_str(to_encode: any) -> str:
    if type(to_encode) == float:
        to_encode = f"{to_encode:0.3f}"
    return str(to_encode).replace(" ", "\xa0")


def _create_header(header: list, soup: BeautifulSoup):
    def get_depth(x):
        if issubclass(type(x), list):
            return max([get_depth(item) for item in x], default=0)
        elif issubclass(type(x), dict):
            return 1 + max([get_depth(item) for item in x.values()], default=0)
        else:
            return 0

    def create_ths(cur_data, index):
        if type(cur_data) == list:
            for item in cur_data:
                create_ths(item, index)

            return len(cur_data)
        elif type(cur_data) == dict:
            th_created = 0
            for key in cur_data:
                cur_th_count = create_ths(cur_data[key], index + 1)
                th_created += cur_th_count

                th_cur = soup.new_tag("th", attrs={"rowspan": "1", "colspan": cur_th_count})
                th_cur.string = encode_to_str(key)
                trs[index].append(th_cur)

            return th_created
        else:
            # leaf element
            th_cur = soup.new_tag("th", attrs={"rowspan": max_depth - index, "colspan": "1"})
            th_cur.string = encode_to_str(cur_data)
            trs[index].append(th_cur)
            return 1

    max_depth = get_depth(header) + 1

    thead = soup.new_tag("thead")

    trs = [soup.new_tag("tr") for _ in range(max_depth)]
    for item in trs:
        thead.append(item)

    create_ths(header, 0)

    return thead


def create_table(header: list, rows: list) -> str:
    """
    :param rows: Just rows with data
    :param header: Complex object, that can contain dicts, list and basic elements with str()
    :rtype: object Return html string
    """

    lens = [len(value) for value in rows]
    if not lens and any([cur_len != lens[0] for cur_len in lens]):
        raise ValueError("Invalid data got on input")

    soup = BeautifulSoup()

    soup.append(
        table := soup.new_tag("table", attrs={"class": "table table-hover table-striped table-bordered align-middle"})
    )

    table.append(_create_header(header, soup))
    table.append(tbody := soup.new_tag("tbody"))

    for row in rows:
        tbody.append(body_tr := soup.new_tag("tr"))

        for elem in row:
            th = soup.new_tag("td")
            th.string = "Nope" if elem is None else encode_to_str(elem)
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
