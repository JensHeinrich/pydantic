"""
Public methods related to:
* `validator` - a decorator to add validation to a field on a model
* `root_validator` - a decorator to add validation to a model as a whole
* `serializer` - a decorator to add serialization to a field on a model
"""

from __future__ import annotations as _annotations

from types import FunctionType
from typing import Any, Callable, overload

from pydantic_core import core_schema as _core_schema
from typing_extensions import Literal

from ._internal import _decorators
from .errors import PydanticUserError


def validator(
    *fields: str,
    mode: Literal['before', 'after', 'wrap', 'plain'] = 'after',
    check_fields: bool | None = None,
    sub_path: tuple[str | int, ...] | None = None,
    allow_reuse: bool = False,
) -> Callable[[Callable[..., Any]], classmethod[Any]]:
    """
    Decorate methods on the class indicating that they should be used to validate fields
    :param fields: which field(s) the method should be called on
    :param mode: TODO
    :param sub_path: TODO
    :param check_fields: whether to check that the fields actually exist on the model
    :param allow_reuse: whether to track and raise an error if another validator refers to the decorated function
    """
    if not fields:
        raise PydanticUserError('validator with no fields specified')
    elif isinstance(fields[0], FunctionType):
        raise PydanticUserError(
            "validators should be used with fields and keyword arguments, not bare. "
            "E.g. usage should be `@validator('<field_name>', ...)`"
        )
    elif not all(isinstance(field, str) for field in fields):
        raise PydanticUserError(
            "validator fields should be passed as separate string args. "
            "E.g. usage should be `@validator('<field_name_1>', '<field_name_2>', ...)`"
        )

    def dec(f: Callable[..., Any]) -> classmethod[Any]:
        f_cls = _decorators.prepare_decorator(f, allow_reuse)
        setattr(
            f_cls,
            _decorators.FIELD_VALIDATOR_TAG,
            (
                fields,
                _decorators.Validator(mode=mode, sub_path=sub_path, check_fields=check_fields),
            ),
        )
        return f_cls

    return dec


@overload
def root_validator(__func: Callable[..., Any]) -> classmethod[Any]:
    ...


@overload
def root_validator(
    *,
    mode: Literal['before', 'after', 'wrap', 'plain'] = 'after',
    allow_reuse: bool = False,
) -> Callable[[Callable[..., Any]], classmethod[Any]]:
    ...


def root_validator(
    __func: Callable[..., Any] | None = None,
    *,
    mode: Literal['before', 'after', 'wrap', 'plain'] = 'after',
    allow_reuse: bool = False,
) -> classmethod[Any] | Callable[[Callable[..., Any]], classmethod[Any]]:
    """
    Decorate methods on a model indicating that they should be used to validate (and perhaps modify) data either
    before or after standard model parsing/validation is performed.
    """
    if __func:
        f_cls = _decorators.prepare_decorator(__func, allow_reuse)
        setattr(f_cls, _decorators.ROOT_VALIDATOR_TAG, _decorators.Validator(mode=mode))
        return f_cls

    def dec(f: Callable[..., Any]) -> classmethod[Any]:
        f_cls = _decorators.prepare_decorator(f, allow_reuse)
        setattr(f_cls, _decorators.ROOT_VALIDATOR_TAG, _decorators.Validator(mode=mode))
        return f_cls

    return dec


def serializer(
    *fields: str,
    json_return_type: _core_schema.JsonReturnTypes | None = None,
    when_used: Literal['always', 'unless-none', 'json', 'json-unless-none'] = 'always',
    sub_path: tuple[str | int, ...] | None = None,
    check_fields: bool | None = None,
    allow_reuse: bool = False,
) -> Callable[[Callable[..., Any]], classmethod[Any]]:
    """
    Decorate methods on the class indicating that they should be used to serialize fields.

    :param fields: which field(s) the method should be called on
    :param json_return_type: The type that the function returns if the serialization mode is JSON.
    :param when_used: When the function should be called
    :param sub_path: TODO
    :param check_fields: whether to check that the fields actually exist on the model
    :param allow_reuse: whether to track and raise an error if another validator refers to the decorated function
    """
    if not fields:
        raise PydanticUserError('serializer with no fields specified')
    elif isinstance(fields[0], FunctionType):
        raise PydanticUserError(
            "serializers should be used with fields and keyword arguments, not bare. "
            "E.g. usage should be `@serializer('<field_name>', ...)`"
        )
    elif not all(isinstance(field, str) for field in fields):
        raise PydanticUserError(
            "serializer fields should be passed as separate string args. "
            "E.g. usage should be `@serializer('<field_name_1>', '<field_name_2>', ...)`"
        )

    def dec(f: Callable[..., Any]) -> classmethod[Any]:
        f_cls = _decorators.prepare_decorator(f, allow_reuse)
        setattr(
            f_cls,
            _decorators.FIELD_SERIALIZER_TAG,
            (
                fields,
                _decorators.Serializer(
                    json_return_type=json_return_type, when_used=when_used, sub_path=sub_path, check_fields=check_fields
                ),
            ),
        )
        return f_cls

    return dec
