# schemas/response.py
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseModel(GenericModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None
