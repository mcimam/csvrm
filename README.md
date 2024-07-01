
# CSV RM

##### DO NOT USE ON PRODUCTION

Object relational mapping from csv file. This module will load csv to memory and 
treat it like Object. This module main purpose is to ease up csv usage in small application, mainly in use in sandboxing.
It's highly ineficient and doesn't support multiple instance.

## Features
CSV RM provide basic orm utility such as :
- Load cscv to object
- Create new record
- Update existing record
- Delete records
- Search records

What not supported yet:
- Transaction
- Concurrent usage

## Installation
Just install it directly using pip. No dependecies needed.

``` sh
pip install csvrm
```

Or you can just copy entire source code.

## Usage
1. Define model structure
Defining new model by inheriting Model class. Put csv file location inside  _filename variable. 
Define each fields you want to extract by specifiy it as object.
``` python 
from csvrm import models, fields

class Person(models.Model):
    _filename = '[filepath]'

    id = fields.Integer()
    name = fields.String()

```

2. Create records
``` python
p = Person(load = true)
p.create({
    'id': 1,
    'name': 'person name'
})
p.save()
```

3. Seach records
``` python
p = Person(load = true)
result = p.search(lambda x: x.name == 'person name')
for res in result:
    print(res.name)
```

4. Update records
Updating record can be done using either update methods or directly change properties
``` python

p = Person(load = true)

result = p.search(lambda x: x.name == 'person name')
for res in result:
    res.name = 'new person name'
p.save()

# OR
p.update(
    domain=(lambda x: x.id == 10),
    values= {'name': 'new person name'}
)
p.save()
```

5. Delete records
``` python
p = Person(load = true)
p.unlink(
    domain=(lambda x: x.id == 10)
)
p.save()
```

FOR FULL DETAIL, READ THE CODE

# Contributing

Fell free to port or contribute this project