from datetime import date


class Field:
    _type = str

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, obj, objtype=None):
        return self._type(obj._records[0][self._name])

    def __set__(self, obj, value):
        self._validate(obj, value)
        obj._records[0][self._name] = self._type(value)

    def _validate(self, obj, value):
        """ Validate value
        """
        # Validate if object is singleton
        assert obj.ensure_one()


class Boolean(Field):
    _type = bool


class Integer(Field):
    _type = int


class Float(Field):
    _type = float


class String(Field):
    _type = str


class Date(Field, date):
    _type = date
