"""Database functions"""
import functools
from operator import itemgetter
from typing import Iterable, Optional, TypeVar

import sqlalchemy.exc

import hworker.depot.objects as objects
from hworker.log import get_logger
from .common import get_Session
from .models import *

ObjectSuccessor = TypeVar("ObjectSuccessor", bound=objects.StoreObject)

_object_to_model_class: dict[type[objects.StoreObject] : type[Base]] = {
    objects.RawData: RawData,
    objects.Homework: Homework,
    objects.Check: Check,
    objects.Solution: Solution,
    objects.CheckResult: CheckResult,
    objects.TaskQualifier: TaskQualifier,
    objects.TaskScore: TaskScore,
    objects.UserQualifier: UserQualifier,
    objects.UserScore: UserScore,
    objects.Formula: Formula,
    objects.FinalScore: FinalScore,
    objects.UpdateTime: UpdateTime,
}

_model_class_to_object: dict[type[Base] : type[objects.StoreObject]] = {
    value: key for key, value in _object_to_model_class.items()
}


def _get_fields_from_object(obj: Any):
    return {name: value for name, value in obj.__dict__.items() if not name.startswith("_") and not callable(value)}


def _translate_object_to_model(obj: objects.StoreObject | type[objects.StoreObject]) -> Base:
    if isinstance(obj, objects.StoreObject) and type(obj) != objects.StoreObject:
        obj = obj
    elif issubclass(obj, objects.StoreObject) and obj != objects.StoreObject:
        obj = obj()
    else:
        raise ValueError("Incorrect object input")

    fields = _get_fields_from_object(obj)
    model_obj = _object_to_model_class[type(obj)]()

    for name, value in fields.items():
        setattr(model_obj, name, value)

    return model_obj


def _create_object(
    to_parse: Base | sqlalchemy.engine.Row,
    return_type: type[objects.StoreObject],
    return_fields: list[str] = None,
) -> objects.StoreObject:
    if isinstance(to_parse, Base):
        fields = [item.name for item in inspect(type(to_parse)).columns]
    else:
        fields = list(to_parse._fields)

    if return_fields is not None:
        if not all(name in fields for name in return_fields):
            raise ValueError("Requested field not found in object")
        fields = return_fields

    vals = {name: getattr(to_parse, name) for name in fields}

    return return_type(**vals)


def _parse_criteria(model: type[Base], criteria: objects.Criteria) -> BinaryExpression:
    model_field = getattr(model, criteria.field_name)

    model_method = getattr(model_field, criteria.get_condition_function())

    return model_method(criteria.field_value)


def store(obj: ObjectSuccessor) -> None:
    """Store object into database
    :param obj: object to store
    """
    get_logger(__name__).debug(f"Stored {type(obj).__name__}: {str(obj)[:100]}")

    if not isinstance(obj, objects.StoreObject) or type(obj) == objects.StoreObject:
        raise ValueError("Incorrect object input")
    if obj.ID is None or obj.timestamp is None:
        raise ValueError("ID and timestamp cannot be None")
    none_field = list(filter(lambda x: x[1] is None, _get_fields_from_object(obj).items()))
    if len(none_field) != 0:
        raise ValueError(
            f"Found None fields in object. Please fill correct value in: {', '.join(map(itemgetter(0), none_field))}"
        )

    try:
        with get_Session().begin() as session:
            model_obj: Base = _translate_object_to_model(obj)

            if obj._is_versioned:
                # should delete by obj.ID and obj.timestamp
                search_result = (
                    session.query(type(model_obj))
                    .where(type(model_obj).ID == obj.ID, type(model_obj).timestamp == obj.timestamp)
                    .first()
                )
            else:
                # should delete by obj.ID
                search_result = session.query(type(model_obj)).where(type(model_obj).ID == obj.ID).first()

            if search_result:
                session.delete(search_result)

            session.add(model_obj)

    except sqlalchemy.exc.IntegrityError:
        get_logger(__name__).debug("Failed to store object, it already exists")
    except Exception as e:
        get_logger(__name__).error(e)


def search(
    obj_type: type[objects.StoreObject],
    *criteria: objects.Criteria,
    return_fields: list[str] = None,
    first: bool = False,
    actual: bool = False,
) -> Iterable[ObjectSuccessor] | Optional[ObjectSuccessor]:
    """Search for object in database
    :param obj_type: type of object to search
    :param criteria: criteria for searching
    :param return_fields: filter for return fields
    :param first: return only first elem
    :param actual: return only latest version of object (grouping them by id)
    :return: iterator for found objects
    """
    get_logger(__name__).debug(f"Searched for {obj_type.__name__}")

    model_type = type(_translate_object_to_model(obj_type))
    with get_Session()() as session:
        search_result = session.query(model_type).order_by(model_type.timestamp.desc())

        if len(criteria) != 0:
            search_result = search_result.filter(*list(map(functools.partial(_parse_criteria, model_type), criteria)))

        if actual and obj_type().is_versioned():
            # wrap base query and subquery and then execute group_by on it for getting most old object
            search_result = session.query(search_result.subquery()).group_by("ID")

        translator = functools.partial(_create_object, return_type=obj_type, return_fields=return_fields)

        if first:
            return None if search_result.first() is None else translator(search_result.first())

        return map(translator, search_result)


def delete(obj_type: type[objects.StoreObject], *criteria: objects.Criteria) -> None:
    """
    Delete object from database
    :param obj_type: type of object to delete or its instance
    :param criteria: criteria for searching objects for delete
    """
    get_logger(__name__).debug(f"Deleted {str(obj_type)[:100]}")

    model_type = type(_translate_object_to_model(obj_type))
    with get_Session().begin() as session:
        search_result = session.query(model_type)
        if len(criteria) != 0:
            search_result = search_result.filter(*list(map(functools.partial(_parse_criteria, model_type), criteria)))

        search_result.delete()
