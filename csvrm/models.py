import csv
from .fields import Field


class ModelError(Exception):
    def __init__(self, message):            
        super().__init__(message)
        self.message = "ModelError {}" % message


# MODEL CLASS
class Model:
    _fields = list()
    _instances = list()
    _owner = list()

    def __init__(self, load=False, owner=None):
        self._filename = self._filename
        self._instances = list()
        # build fields
        self._fields = list(map(lambda x: x[0], filter(
            lambda x: issubclass(type(x[1]), Field),
            list(type(self).__dict__.items())
        )))

        if load:
            self.load()

        # if owner:
        #     self._owner = owner

    def __iter__(self):
        for i in self._instances:
            yield i

    def __repr__(self):
        return f"{self.__class__}"

    def __getitem__(self, key):
        if isinstance(key, str):
            if len(self._instances) > 1:
                raise ModelError("Result has multiple instances")
            return self.key
        elif isinstance(key, slice):
            return self._instances[key]
        else:
            return self._instances[key]

    def load(self):
        with open(self._filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_data = type(self)()
                for col, val in row.items():
                    if not hasattr(new_data, col):
                        raise ModelError("Attribute {} not found" % col)
                    setattr(new_data, col, val)
                self._instances.append(new_data)

    def save(self):
        with open(self._filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fields)
            writer.writeheader()
            # write rows
            for rec in self._instances:
                writer.writerow(rec.get_dict())

    # MISC METHOD
    def _is_one(self):
        return len(self._instances) == 0

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
        return self._instances

    def search(self, domain):
        res = list()
        for rec in self._instances:
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
        self._instances.append(new_data)

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
        for rec in self._instances:
            if domain(rec):
                del rec
