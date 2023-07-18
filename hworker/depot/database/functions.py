"""Database functions"""
from typing import Iterable, Union, Type

import sqlalchemy.exc

from .common import Session
from .models import *

import hworker.depot.objects as objects

from hworker.log import get_logger

my_logger = get_logger(__name__)


def _translate_object_to_model(obj: Union[objects.StoreObject, Type[objects.StoreObject]]) -> Base:
    if isinstance(obj, objects.StoreObject) and type(obj) != objects.StoreObject:
        cur_object = obj
    elif issubclass(obj, objects.StoreObject) and obj != objects.StoreObject:
        cur_object = obj()
    else:
        raise ValueError("Incorrect object input")

    if isinstance(cur_object, objects.Homework):
        return Homework(ID="10", USER_ID="11", TASK_ID="12", timestamp=12345, data=b"dasdada")


def _translate_model_to_object(model: Base) -> objects.StoreObject:
    if type(model) == Base:
        raise ValueError("Base class cannot be translated")
    if isinstance(model, Homework):
        return objects.Homework(ID="10", USER_ID="11", TASK_ID="12", timestamp=12345, data={"lalala": b"dasdada"})


def store(obj: objects.StoreObject) -> None:
    get_logger(__name__).debug(f"Tried to store {obj}")
    return

    """Store object into database"""
    if not isinstance(obj, objects.StoreObject) or type(obj) == objects.StoreObject:
        raise ValueError("Incorrect object input")
    if obj.ID is None or obj.timestamp is None:
        raise ValueError("ID and timestamp cannot be None")

    try:
        with Session.begin() as session:
            model_obj: Base = _translate_object_to_model(obj)

            # if object is not versioned previous version should be deleted first
            if not obj._is_versioned:
                # TODO add search criteria
                search_result = session.query(type(model_obj)).where(type(model_obj).ID == obj.ID).first()
                print(search_result)
                if search_result is not Null:
                    session.delete(search_result)
            session.add(model_obj)

    except sqlalchemy.exc.IntegrityError:
        get_logger(__name__).debug("Failed to store object, it already exists")
    except Exception as e:
        get_logger(__name__).error(e)


def search(obj_type: Union[objects.StoreObject, Type[objects.StoreObject]], criteria=None) -> Iterable[objects.StoreObject]:
    get_logger(__name__).debug(f"Tried to search {obj_type}")
    return
    """Search for object in database"""
    model_type = type(_translate_object_to_model(obj_type))
    with Session.begin() as session:
        if criteria is None:
            # TODO add search criteria
            return map(_translate_model_to_object, session.query(model_type))

    return iter([])


def delete(obj_type: objects.StoreObject, criteria=None) -> None:
    get_logger(__name__).debug(f"Tried to delete {obj_type}")
    model_type = type(_translate_object_to_model(obj_type))
    """Delete object from database"""
    with Session.begin() as session:
        if criteria is None:
            return session.query(model_type).delete()


# def add_report(email, report_path):
#     """Adds report to student"""
#     with Session() as session:
#         """Get or create student"""
#         student = session.query(Student).filter(Student.unique_id == email).first()
#         if not student:
#             username = "Undefined"
#             student = Student(username, email)
#             session.add(student)
#             session.commit()
#
#         """Get or create task"""
#         report_name = os.path.basename(report_path)
#         task_name = "TODO"
#         task = session.query(Task).filter(Task.name == task_name).filter(Task.student_id == student.id).first()
#         if not task:
#             task = Task(student, task_name)
#             session.add(task)
#             session.commit()
#
#         """Add report if it isn't already added"""
#         report = session.query(Solution).join(Task).filter(Task.student == student).filter(Solution.name == report_name).first()
#         if not report:
#             """Add completely new report"""
#             report = Solution(task, report_path)
#             session.add(report)
#             session.commit()
#         else:
#             """Check new report date"""
#             new_report = Solution(task, report_path)
#             if new_report.creation_date > report.creation_date:
#                 """Replacing older report by new one"""
#                 session.delete(report)
#                 session.add(new_report)
#                 session.commit()
#             else:
#                 """New report is older"""
#                 pass
#
#         task.creation_date = min([report.creation_date for report in task.reports])
#         if sum([1 for report in task.reports if report.is_broken]):
#             task.is_broken = True
#         else:
#             task.is_broken = False
#         session.commit()
