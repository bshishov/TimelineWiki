from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo, ObjectId
from flask_api import FlaskAPI, status, exceptions
from flask_cors import CORS
from backend.validations import *

app = FlaskAPI(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/timelinewiki"

#CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources=r'/*')
mongo = PyMongo(app)

STR_VALIDATION = [Type(str), StrNotEmpty()]
URI_VALIDATION = [Type(str), StrNotEmpty(), StrMatchRe('^[a-z0-9_]+$')]
EVENT_TYPE_VALIDATION = [Type(str), In(['text', 'header'])]


class Model(object):
    collection = None

    def __init__(self, _id=None):
        if isinstance(_id, str):
            _id = ObjectId(_id)
        if _id is None:
            _id = ObjectId()
        self._id = _id

    def save(self, upsert=True):
        result = Event.collection.update_one(
            {'_id': self._id},
            {"$set": self.to_mongo()},
            upsert=upsert)
        if upsert:
            return result.upserted_id is not None
        return result.modified_count == 1

    def get_representation(self):
        raise NotImplementedError

    def delete(self):
        self.collection.delete_one({'_id': self._id})

    def to_mongo(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_mongo(cls, obj: dict):
        raise NotImplementedError

    @classmethod
    def find_one_or_404(cls, **kwargs):
        obj = cls.collection.find_one_or_404(kwargs)
        return cls.from_mongo(obj)

    @classmethod
    def find_many(cls, **kwargs):
        objects = cls.collection.find(kwargs)
        return list(map(cls.from_mongo, objects))


class Realm(Model):
    collection = mongo.db.realms

    POST_SCHEMA = {
        SCHEMA_ONLY_THESE_FIELDS: True,
        SCHEMA_FIELDS: {
            'uri': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: URI_VALIDATION},
            'name': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: STR_VALIDATION}
        }
    }

    PUT_SCHEMA = {
        SCHEMA_ONLY_THESE_FIELDS: True,
        SCHEMA_FIELDS: {
            'uri': {FIELD_IS_REQUIRED: False, FIELD_VALIDATORS: URI_VALIDATION},
            'name': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: STR_VALIDATION}
        }
    }

    def __init__(self, name: str, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.uri = uri

    def get_representation(self):
        return {
            'url': request.host_url.rstrip('/') + url_for('realm_detail', uri=self.uri),
            'url_events': request.host_url.rstrip('/') + url_for('realm_events', realm_uri=self.uri),
            'url_headers': request.host_url.rstrip('/') + url_for('realm_headers', realm_uri=self.uri),
            'name': self.name,
            'uri': self.uri
        }

    def to_mongo(self):
        return {'name': self.name, 'uri': self.uri}

    @classmethod
    def from_mongo(cls, mongo_obj):
        return Realm(**mongo_obj)


class Event(Model):
    collection = mongo.db.events

    POST_SCHEMA = {
        SCHEMA_ONLY_THESE_FIELDS: True,
        SCHEMA_FIELDS: {
            'type': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: EVENT_TYPE_VALIDATION},
            'value': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: STR_VALIDATION},
            'order': {FIELD_IS_REQUIRED: False, FIELD_VALIDATORS: [Type(float, int)]}
        }
    }

    PUT_SCHEMA = {
        SCHEMA_ONLY_THESE_FIELDS: True,
        SCHEMA_FIELDS: {
            'type': {FIELD_IS_REQUIRED: False, FIELD_VALIDATORS: EVENT_TYPE_VALIDATION},
            'value': {FIELD_IS_REQUIRED: False, FIELD_VALIDATORS: STR_VALIDATION},
            'order': {FIELD_IS_REQUIRED: False, FIELD_VALIDATORS: [Type(float, int)]}
        }
    }

    def __init__(self, type: str, value: str, realm: str, order: float=0.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.realm = realm
        self.type = type
        self.value = value
        self.order = order

    def get_representation(self):
        return {
            'url': request.host_url.rstrip('/') + url_for('event_detail', event_id=str(self._id)),
            'id': str(self._id),
            'realm': self.realm,
            'type': self.type,
            'value': self.value,
            'order': self.order
        }

    def to_mongo(self):
        return {'type': self.type, 'value': self.value, 'realm': self.realm, 'order': self.order}

    @classmethod
    def find_many(cls, **kwargs):
        objects = cls.collection.find(kwargs).sort('order', 1)
        return list(map(cls.from_mongo, objects))

    @classmethod
    def from_mongo(cls, mongo_obj):
        return Event(**mongo_obj)


class User(Model):
    collection = mongo.db.users

    USER_LOGIN_SCHEMA = {
        SCHEMA_ONLY_THESE_FIELDS: True,
        SCHEMA_FIELDS: {
            'email': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: STR_VALIDATION},
            'value': {FIELD_IS_REQUIRED: True, FIELD_VALIDATORS: STR_VALIDATION}
        }
    }

    def __init__(self, email, role, created, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.email = email
        self.created = created

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_representation(self):
        return {
            'email': self.email,
            'created': self.created,
            'role': self.role
        }

    def to_mongo(self):
        return {'role': self.role, 'created': self.created, 'email': self.email}

    @classmethod
    def from_mongo(cls, mongo_obj):
        return User(**mongo_obj)


def get_representation(model: Model):
    return model.get_representation()


def _filter_args(fields=None):
    def _query_arg_to_filter(_v):
        if isinstance(_v, list):
            return {"$in": _v}
        return _v
    if fields is not None:
        return {k: _query_arg_to_filter(v) for k, v in request.args.items() if k in fields}
    return {k: _query_arg_to_filter(v) for k, v in request.args.items()}


@app.route("/", methods=['GET', 'POST'])
def realm_list():
    if request.method == 'POST':
        validate_schema(Realm.POST_SCHEMA, request.data)
        realm = Realm(name=request.data.get('name'), uri=request.data.get('uri'))
        if realm.save(upsert=True):
            return realm.get_representation(), status.HTTP_201_CREATED
        return '', status.HTTP_400_BAD_REQUEST

    # request.method == 'GET'
    return list(map(get_representation, Realm.find_many()))


@app.route("/<string:uri>/", methods=['GET', 'PUT', 'DELETE'])
def realm_detail(uri):
    realm = Realm.find_one_or_404(uri=uri)

    if request.method == 'PUT':
        validate_schema(Realm.PUT_SCHEMA, request.data)
        realm.name = request.data.get('name', realm.uri)
        realm.uri = request.data.get('uri', realm.uri)
        if realm.save(upsert=False):
            return realm.get_representation()
        return '', status.HTTP_400_BAD_REQUEST

    elif request.method == 'DELETE':
        realm.delete()
        return '', status.HTTP_204_NO_CONTENT

    return realm.get_representation()


@app.route("/<string:realm_uri>/events/", methods=['GET', 'POST'])
def realm_events(realm_uri):
    # To make sure that realm exists
    realm = Realm.find_one_or_404(uri=realm_uri)

    if request.method == 'POST':
        validate_schema(Event.POST_SCHEMA, request.data)
        event = Event(realm=realm_uri,
                      type=request.data.get('type'),
                      order=request.data.get('order'),
                      value=request.data.get('value'))
        if event.save(upsert=True):
            return event.get_representation()
        return '', status.HTTP_400_BAD_REQUEST

    query = {'realm': realm_uri}
    query.update(_filter_args(['type']))
    return list(map(get_representation, Event.find_many(**query)))


@app.route("/<string:realm_uri>/headers/", methods=['GET'])
def realm_headers(realm_uri):
    realm = Realm.find_one_or_404(uri=realm_uri)
    query = {'realm': realm_uri, 'type': 'header'}
    return list(map(get_representation, Event.find_many(**query)))


@app.route("/events/<string:event_id>/", methods=['GET', 'PUT', 'DELETE'])
def event_detail(event_id: str):
    event = Event.find_one_or_404(_id=ObjectId(event_id))

    if request.method == 'PUT':
        validate_schema(Event.PUT_SCHEMA, request.data)
        event.type = request.data.get('type', event.type)
        event.value = request.data.get('value', event.value)
        event.order = request.data.get('order', event.order)
        if event.save(upsert=False):
            return event.get_representation()
        return '', status.HTTP_400_BAD_REQUEST

    elif request.method == 'DELETE':
        event.delete()
        return '', status.HTTP_204_NO_CONTENT

    return event.get_representation()


@app.route("/auth/", methods=['POST', 'DELETE'])
def auth():
    pass


if __name__ == "__main__":
    app.run(debug=True)
