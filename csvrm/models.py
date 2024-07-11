import csv
import logging
from pathlib import Path

from .fields import Field
from .exceptions import ModelError

logger = logging.getLogger(__name__)


# MODEL CLASS
class Model:
    """
    This is base model for csv relational mapping.

    Attributes:
        fields (Fields): Model fields

    """
    # Instances variable
    _fields = list()
    _records = list()

    def __init__(self, load=False, disable_create=False, **kwargs):
        """
        Paramaters:
            load (bool) : load data when init class
            disable_create(bool) : disable file creation if not found
        """

        # Config Variable
        self._filename = self._filename

        # Runtime Variable
        self.__master = False
        self._records = list()

        # Build fields
        self._fields = list(map(lambda x: x[0], filter(
            lambda x: issubclass(type(x[1]), Field),
            list(type(self).__dict__.items())
        )))

        # Treate object as idividual record or whole data
        if load:
            self.load(disable_create)
        elif kwargs:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self._records.append(self)

    def __iter__(self):
        for i in self._records:
            yield i

    def __compile_output(self):
        cname = self.__class__.__name__
        if self.__master:
            return f"{cname}(M)"
        else:
            rdata = ""
            for field in self._fields:
                rdata += f"{field}={getattr(self, field, None).__repr__()},"

            if len(rdata) > 80:
                rdata = rdata[:80]

            return f"{cname}({rdata})"

    def __repr__(self):
        return self.__compile_output()

    def __str__(self):
        return self.__compile_output()

    def __getitem__(self, key):
        if isinstance(key, str):
            if len(self._records) > 1:
                raise ModelError("Result has multiple instances")
            return self.key
        elif isinstance(key, slice):
            return self._records[key]
        else:
            return self._records[key]

    def _is_master(self):
        return self.__master

    # READ WRITE METHOD
    def _ccreate_file(self):
        """ Create file if it not exist yet
        """
        if Path(self._filename).is_file():
            return

        logger.warning("Warning: File not exist, try to create one")
        with open(self._filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fields)
            writer.writeheader()

    def load(self, disable_create=False):
        """ Load csv to memory

        Paramaters:
            disable_create(bool) : disable file creation if not found
        """
        self.__master = True

        if not disable_create:
            self._ccreate_file()

        with open(self._filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_data = type(self)()
                for col, val in row.items():
                    if not hasattr(new_data, col):
                        raise ModelError("Attribute {} not found" % col)
                    setattr(new_data, col, val)
                self._records.append(new_data)

    def save(self):
        mode = 'w' if self.__master else 'a'

        with open(self._filename, mode) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fields)
            if self.__master:
                writer.writeheader()
            for rec in self._records:
                writer.writerow(rec.get_dict())

    # MISC METHOD
    def _is_one(self):
        return len(self._records) == 0

    def ensure_one(self):
        if not self._is_one():
            raise ModelError("Model not singleton")

    def get_dict(self):
        res = {}
        for f in self._fields:
            res[f] = getattr(self, f)
        return res

    # CRUD METHOD
    def get(self):
        return self._records

    def search(self, domain):
        res = list()
        for rec in self._records:
            if domain(rec):
                res.append(rec)
        return res

    def read(self, id):
        res = self.search(str(id))
        return res[0]

    def create(self, values):
        new_data = type(self)()
        for c, v in values.items():
            if not hasattr(new_data, c):
                raise ModelError("Attribute {} not found" % c)
            setattr(new_data, c, v)
        self._records.append(new_data)

    def update(self, domain=None, values={}):
        if not domain:
            raise ModelError("Domain is required")
        for rec in self.search(domain):
            for c, v in values.items():
                if not hasattr(rec, c):
                    raise ModelError("Attribute {} not found" % c)
                setattr(rec, c, v)

    def unlink(self, domain=None):
        if not domain:
            raise ModelError("Domain is required")
        for rec in self._records:
            if domain(rec):
                del rec
