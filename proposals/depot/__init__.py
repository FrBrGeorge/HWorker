# See/modify https://github.com/FrBrGeorge/HWorker/wiki/depot
# See/modify https://github.com/FrBrGeorge/HWorker/wiki/API
class StoreObject:
    ID: str                 # Uniquie ID
    uid: str                # User name
    tid: str                # Task name
    timestamp: int          # Timestamp / version ?? or (datetime.datetime?)


class Homework(StoreObject):
    obj: dict[str, str]     # filename with path: file text


class Test(StoreObject):
    obj: bytes              # TODO Needs to be TestOject
    category: str


class Solution:
    obj: dict[str, str]     # filename with path: file text
    tests: list[str]        # ?? or list[Test]?


class TestResult:
    obj: float
    category: str


class Plagiary:
    obj: list[str]          # ID's ?? or list[Homework] or list[Solution]


class ScoreFunction:
    obj: str


class PartialScore:
    obj: float


class Formula:
    obj: str


class Score:
    obj: str
