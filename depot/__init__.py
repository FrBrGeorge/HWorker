import datetime


class Task:
    name: str
    deadline: datetime.datetime


class Student:
    id: str
    pretty_name: str


class Test:
    test_fields: list


class Scorer:
    test_fields: list


class Solution:
    files: dict[str, str]  # filename with path: file text
    delivery_time: datetime.datetime
    student_link: Student
    task_link: Task


class TestResults:
    test_link: Test
    solution_link: Solution


class Score:
    test_results_link: TestResults
    scorer_link: Scorer
