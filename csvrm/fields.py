from datetime import date


# FIELD CLASS
class Field:
    _type = str
    _default = False

    def __init__(self, **kwargs):
        self._type = str
        self._default = False
        self._value = self._default

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        self._value = value

    def __repr__(self):
        val = self._type(self._value)
        return f"{val}"


class Integer(Field, int):
    _type = int
    _default = 0


class Float(Field, float):
    _type = float
    _default = 0.0


class String(Field, str):
    _type = str
    _default = False


class Date(Field, date):
    _type = date
    _default = date.today()

    def __new__(cls, year=None, month=None, day=None,):
        if not year:
            self = cls._default
        else:
            self = super().__new__(year, month=None, day=None)
        return self
