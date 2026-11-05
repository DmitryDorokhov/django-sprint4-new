from abc import abstractmethod, ABC
from inspect import isclass
from typing import Union, Type, Any

from django.db.models import Model


class ModelAdapter(ABC):
    def __init__(self, item_or_class: Union[Model, Type[Model]]):
        self._item_or_cls = item_or_class

    def __getattr__(self, name: str) -> Any:
        return getattr(self._item_or_cls, name)

    def get_student_field_name(self, field_name: str) -> str:
        return getattr(self.item_cls_adapter, field_name).field.name

    @property
    @abstractmethod
    def displayed_field_name_or_value(self):
        ...

    @property
    def item_cls(self):
        if isclass(self._item_or_cls):
            return self._item_or_cls
        else:
            return self._item_or_cls.__class__

    @property
    def item_cls_adapter(self):
        if isclass(self._item_or_cls):
            return self
        else:
            return self.__class__(self._item_or_cls.__class__)
