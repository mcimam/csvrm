import csv
import logging

from os.path import abspath
from pathlib import Path


from .exceptions import ModelError
from .fields import Field

logger = logging.getLogger(__name__)


class Model:
    """
    This is base model for csv relational mapping.

    Attributes:
        fields (Fields): Model fields

    """
    # Class variable
    _name = ''
    _filename = False  # csv file location
    _dialect = 'excel'  # csv dialect
    _check = True  # csv check

    _fields = list()  # list of fields
    _field_maps = dict()  # map fields and class
    _master_records = list()  # master records
    _lock = False  # transaction lock

    _id = 'id'  # PK Fields

    def __init__(self, records: list[dict] = False, **kwargs):
        """
        Init file should set if current model is master or not
        """
        # This method is better to run in metaclass
        # Or when class is register even if instace is not created yet

        if records is False:
            # Initialize
            # Set filename to abs path
            type(self)._filename = abspath(self._filename)

            # Handle fields register
            type(self)._fields = [x[0] for x in type(
                self).__dict__.items() if issubclass(type(x[1]), Field)]

            # Register fields in it's class
            type(self)._field_maps = {x[0]: x[1] for x in type(
                self).__dict__.items() if issubclass(type(x[1]), Field)}

            ########################################################
            # Load record as master
            # In this case _records is shallow copy of _master_records
            self.load()
            self._records = self._master_records
        else:
            # Load record as non master
            self._records = records

    # DUNDER Methods

    def __iter__(self):
        for rec in self._records:
            yield type(self)([rec])

    def __getitem__(self, key):
        if isinstance(key, str):
            if len(self._records) > 1:
                raise ModelError("Result has multiple instances")
            return getattr(self, key, None)
        elif isinstance(key, slice):
            return type(self)(self._records[key])
        elif isinstance(key, int):
            return type(self)([self._records[key]])
        else:
            raise ModelError("Invalid get item method")

    def __len__(self):
        return len(self._records)

    # FILE Methods
    def _check_file(self):
        """ Check file if it not exist yet or invalid
        """

        if not Path(self._filename).is_file():
            logger.warning("Warning: File not exist, try to create one")
            with open(self._filename, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self._fields)
                writer.writeheader()

    def load(self):
        """ Load csv to memory

        Paramaters:
            disable_create(bool) : disable file creation if not found
        """
        if self._check:
            self._check_file()

        with open(self._filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, dialect=self._dialect)

            # Check if file is empty
            try:
                frow = next(reader)
            except StopIteration:
                self._master_records = []
                return

            # Validate fields with the first row
            invalid_fields = [fi for fi in self._fields if fi not in frow]
            invalid_fields = ', '.join(invalid_fields)

            if invalid_fields:
                raise ModelError(
                    "Attribute(s) %s not found in %s" %
                    (invalid_fields,
                     self._filename),
                )

            # Process the first row and the rest
            arec = []
            for row in [frow] + list(reader):
                rec = {}
                for col, val in row.items():
                    if col in self._fields:
                        rec[col] = self._field_maps[col]._convert_value(val)
                arec.append(rec)

            type(self)._master_records = arec

    def save(self):
        with open(self._filename, 'w') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=self._fields, dialect=self._dialect)
            writer.writeheader()
            for rec in self._records:
                writer.writerow(rec)

    # MISC Methods
    def ensure_one(self):
        if len(self._records) > 1:
            raise ModelError("Model not singleton")

    # CRUD Methods
    def search(self, domain):
        if callable(domain):
            res = [rec._records[0] for rec in self if domain(rec)]
            return type(self)(res)
        else:
            raise NotImplementedError

    def read(self, id):
        return self[id]

    def create(self, value: dict):
        rec = {col: None for col in self._fields}
        for c, v in value.items():
            if c not in self._fields:
                raise ModelError("Attribute {} not found" % c)
            rec[c] = v

        type(self)._master_records.append(rec)
        return self

    def update(self, domain, value: dict):
        if not domain and not self:
            raise ModelError("Domain is required")

        records = self.search(domain)
        for rec in records:
            for c, v in value.items():
                if c not in self._fields:
                    raise ModelError("Attribute {} not found" % c)
                rec[c] = v

        return records

    def delete(self, domain=None):
        if not domain and not self._records:
            raise ModelError("Domain is required")
        rec = self.search(domain) if self._records == [] else self
        if not rec:
            raise ModelError("No record found")
        for d in rec:
            del d

    # OPERATOR Methods
    def __eq__(self, other):
        empty = self._records == []
        return empty == other
