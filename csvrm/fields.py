from datetime import datetime, date
from .exceptions import ModelError


class Field:
    _type = str
    _default = _type()

    def __init__(self, required=False, readonly=False, **kwargs):
        """ Fields model that store each element

        Paramaters:
            required (bool): prevent for empty element
            readonly (bool): prevent element write
        """
        self.required = required
        self.readonly = readonly

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, objtype=None):
        return obj._records[0][self._name]

    def __set__(self, obj, value):
        if self.readonly:
            raise ModelError(f"{self._name} is readonly")

        self._validate(obj, value)
        obj._records[0][self._name] = self._convert_value(value)

    def _convert_value(self, value):
        """ Validate element value
        """
        # Check type or set null
        try:
            if self.required:
                assert value != '', f"{self._name} is required"
            value = self._type(value)
        except ValueError:
            value = self._default
        except AssertionError as e:
            raise ModelError(e)
        except Exception as e:
            raise e

        return value

    def _validate(self, obj, value=False):
        """ Validate value
        """
        # Validate if object is singleton
        obj.ensure_one()


class Boolean(Field):
    _type = bool


class Integer(Field):
    _type = int


class Float(Field):
    _type = float


class String(Field):
    _type = str


class Date(Field):
    _type = date
    _default = date.today()

    def __init__(self, format='%d/%m/%y', **kwargs):
        super().__init__(**kwargs)
        self.format = '%d-%m-%y'

    # def __get__(self, **kwargs):
    #     res = super().__get__(**kwargs)
    #     if res:
    #         res = res.strftime(self.format)

    def _convert_value(self, value):
        """ Validate element value
        """
        # Check type or set null
        try:
            if self.required:
                assert value != '', f"{self._name} is required"
            value = datetime.strptime(value, self.format).date()
        except ValueError:
            value = self._default
        except AssertionError as e:
            raise ModelError(e)
        except Exception as e:
            raise e

        return value


class Datetime(Field):
    _type = date
    _default = datetime.now()

    def __init__(self, format='%d/%m/%y', **kwargs):
        super().__init__(**kwargs)
        self.format = '%d-%m-%y'

    def _convert_value(self, value):
        """ Validate element value
        """
        # Check type or set null
        try:
            if self.required:
                assert value != '', f"{self._name} is required"
            value = datetime.strptime(value, self.format)
        except ValueError:
            value = self._default
        except AssertionError as e:
            raise ModelError(e)
        except Exception as e:
            raise e

        return value
