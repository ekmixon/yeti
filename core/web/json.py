from __future__ import unicode_literals

import datetime

import simplejson
from bson.dbref import DBRef
from bson.json_util import default, object_hook as bson_hook
from bson.objectid import ObjectId
from mongoengine import QuerySet, Document, EmbeddedDocument

from core.database import Node, Link, YetiDocument
from core.user import User


def recursive_encoder(objects, template=None, ctx=None):
    if isinstance(objects, dict):
        return {key: recursive_encoder(value) for key, value in objects.items()}

    elif isinstance(objects, (list, QuerySet, set)):
        return [recursive_encoder(o) for o in objects]

    elif isinstance(objects, tuple):
        return tuple(recursive_encoder(o) for o in objects)

    elif isinstance(objects, (ObjectId, DBRef, datetime.datetime)):
        return to_json(objects)

    elif isinstance(objects, (Node, Link, YetiDocument, Document, EmbeddedDocument)):
        data = objects.info() if hasattr(objects, "info") else objects.to_mongo()
        return recursive_encoder(data)

    else:
        return objects


def to_json(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, DBRef):
        return {"collection": obj.collection, "id": str(obj.id)}
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, User):
        return obj.username
    else:
        return default(obj)


class JSONDecoder(simplejson.JSONDecoder):
    def decode(self, s):
        def object_hook(obj):
            return bson_hook(obj)

        return simplejson.loads(s, object_hook=self.object_hook)
