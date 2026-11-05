from inspect import isclass

from adapters.model_adapter import ModelAdapter


class UserModelAdapter(ModelAdapter):
    @property
    def displayed_field_name_or_value(self):
        if isclass(self._item_or_cls):
            return "last_name"
        else:
            return self.last_name.replace("\n", "")
