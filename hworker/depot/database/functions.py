"""Database functions"""
import functools
from operator import itemgetter
from typing import Iterable, Union, Type, Optional

import sqlalchemy.exc

from .common import Session
from .models import *

import hworker.depot.objects as objects
from hworker.log import get_logger

_object_to_model_class: dict[Type[objects.StoreObject] : Type[Base]] = {
    objects.Homework: Homework,
    objects.Check: Check,
    objects.Solution: Solution,
    objects.CheckResult: CheckResult,
    objects.TaskQualify: TaskQualify,
    objects.TaskScore: TaskScore,
    objects.UserQualify: UserQualify,
    objects.UserScore: UserScore,
    objects.Formula: Formula,
    objects.FinalScore: FinalScore,
}
_model_class_to_object: dict[Type[Base] : Type[objects.StoreObject]] = {
    value: key for key, value in _object_to_model_class.items()
}


def _get_fields_from_object(obj: Any):
    return {name: value for name, value in obj.__dict__.items() if not name.startswith("_") and not callable(value)}


def _translate_object_to_model(obj: Union[objects.StoreObject, Type[objects.StoreObject]]) -> Base:
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


def _translate_model_to_object(model: Base, field_filter: list[str] = None) -> objects.StoreObject:
    fields = _get_fields_from_object(model)
    obj = _model_class_to_object[type(model)]()

    if field_filter is not None:
        if field_filter not in fields:
            raise ValueError("Requested field not found in object")
        [fields.pop(name) for name in field_filter]

    for name, value in fields.items():
        setattr(obj, name, value)

    return obj


def _parse_criteria(model: Type[Base], criteria: objects.Criteria) -> BinaryExpression:
    model_field = getattr(model, criteria.field_name)

    model_method = getattr(model_field, criteria.get_condition_function())

    return model_method(criteria.field_value)


def store(obj: objects.StoreObject) -> None:
    """Store object into database
    :param obj: object to store
    """
    get_logger(__name__).debug(f"Tried to store {str(obj)[:100]}")

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
        with Session.begin() as session:
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
    obj_type: Union[objects.StoreObject, Type[objects.StoreObject]],
    *criteria: objects.Criteria,
    return_fields: list[str] = None,
    first: bool = False,
) -> Union[Iterable[objects.StoreObject], Optional[objects.StoreObject]]:
    """Search for object in database
    :param obj_type: type of object to search or its instance
    :param criteria: criteria for searching
    :param return_fields: filter for return fields
    :param first: return only first elem
    :return: iterator for found objects
    """
    get_logger(__name__).debug(f"Tried to search {str(obj_type)[:100]}")

    model_type = type(_translate_object_to_model(obj_type))
    with Session.begin() as session:
        search_result = session.query(model_type)

        if len(criteria) != 0:
            search_result = search_result.filter(*list(map(functools.partial(_parse_criteria, model_type), criteria)))

        func = functools.partial(_translate_model_to_object, field_filter=return_fields)

        if first:
            return None if search_result.first() is None else func(search_result.first())

        return map(func, search_result)


def delete(obj_type: objects.StoreObject, *criteria: Iterable[objects.Criteria]) -> None:
    """
    Delete object from database
    :param obj_type: type of object to delete or its instance
    :param criteria: criteria for searching objects for delete
    """
    get_logger(__name__).debug(f"Tried to delete {str(obj_type)[:100]}")

    model_type = type(_translate_object_to_model(obj_type))
    with Session.begin() as session:
        search_result = session.query(model_type)
        if len(criteria) != 0:
            search_result = search_result.filter(*list(map(functools.partial(_parse_criteria, model_type), criteria)))

        search_result.delete()
