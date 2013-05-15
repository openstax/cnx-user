# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""
Json in and out
---------------

JSON out is a realtively do-able approach - we shall define a method "todict"
on each SA object, and this shall be manually adjusted so that when it is called
it itself calls the same method on "children" objects.  THe presumed existence of children objects is fine for our current use cases.

SA appears not to give decent support to determining types of relationships - but this is so unlikely it is a matter of reading their docs more now.

In is a interesting matter - I intend to do the simple case of one json doc, one mapping (schema specific) and then setattr work.



Discussion on serialising rows
------------------------------

It used to be easy to serialise a database row.  Really.
But here we are really serialsing nested objects - and the dangers that allows
and the edge cases are aquite high.  I cannot find a simple clean and supported method to
arbitraily serialise SQ objects to dict (and on to JSON)

So, the best approach (and variations of this are around the
literature (you know, on the Blue Googles)) is to craft an extra
function in each SA object, that supports a serialisable function (probably __iter__)
and that function returns serialised data that we control

Pretty much exactly what I have been doing.

In short, there are ways to do this arbitrarily deep and recursive -
but the magic is deep in SA and I would worry about defending the edge
cases (

SA mindset - the SA mindset is (IMO) about solving the ORM bete-noir
of inheritence in relations/entites.  THat is if a professor and a
student both inherit from a person class, how is that handeled in the
database, and how to map that in the ORM. My feeling is not to do so.  However a lot of SA becomes easier to understand when you rembmer this and its iomplications.

Some notes:

sqlalchemy.ext.serializer exists to support pickling (with pickle
module) of queries, expressions and other internal SQLAlchemy objects,
it doesn't deal with model objects. In no way it will help you to
serialize model objects to XML.
http://stackoverflow.com/questions/1740817/sqlalchemy-rest-serialization

http://trac.turbogears.org/ticket/1582
http://docs.sqlalchemy.org/en/latest/orm/relationships.html
https://groups.google.com/forum/?fromgroups=#!topic/sqlalchemy/hY13qaWuEGY
https://github.com/mitsuhiko/flask/blob/master/flask/json.py
http://pieceofpy.com/2009/08/17/sqlalchemy-and-json-w-pylons-best-practices/

.. todo:: move this to real docs not code.


Issues: repeating code - either use external calls or inherit
: we do not use jsonpickle - its very python specific - at least datetime transforms are ISOformat


usermodel.py
============

Represents the SQLALchemy classes and assoc functions, that store user
details in web server, and persist to postgres dbase.

We have two main models :py:class:User and :py:class:Identifier.
One User may have many identifiers, but one identifier may only have
one User.  Each identier is either a openid or a persona.

A user_id is a urn of form <domain_of_originating_repo>-<uuid(4)>
"org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383"


API

:/user/:
    Support POST PUT GET [DELETE]
    Is keyed on *user_id* - the uuid form above
    /user/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383
    will return a *user profile* in JSON form

:/users/:
    Support only GET

:/users/:
    GET - will return list of all users - is only for dev. and
          hardcoded to max 25

:/users/?fullname=bob:
    GET - searches the key field in User object and returns
          JSON encoded user profiles


A specialised form of the above search is

/user/?openid=http://xxx
/user/?persona=p@x.com

These explicitly want to look up existing authetnitcatd identifiers in our dbase.
(ie part of signon process)


views
-----

:search_user():

:post_user(<dict>):
     user_id MUST NOT be present
     Will overwrite all fields provided.

:put_user(<dict>):
     user_id MUST be present.
     We will replace all fields provided

:get_user(<user_id>):
     IF search string present, treat it as a search
     else search_user

:search_user(authenticatedID):
     see above

:delete_user():
      TBD


Matching usermodel

Naming convention

distinguohs between a userprofile_dict and userprofile_json
                      identifier_dict and identifier_json


iterating over models

>>> x = [prop for prop in usermodel.User.__mapper__.iterate_properties if isinstance(prop, sqlalchemy.orm.properties.RelationshipProperty)]
>>> u.__getattribute__(x[0].key)
[<rhaptos2.user.usermodel.Identifier object at 0x8073dd890>]

This fails the smell test - a child object (relationship) has a relationship back to the parent - and no obvious way of determining the directionality or visted state (ie loops)
This is fair - parent child is only a common use case, nopt exclusive - but I want to deal with the common use case.



testjson = '{"interests": null, "identifiers": [{"identifierstring": "http://fake1.example.com/", "user_id": "org.cnx.user-f7887118-74d5-4963-a0c2-04d8f863eea3", "identifiertype": "openid"}], "user_id": "org.cnx.user-f7887118-74d5-4963-a0c2-04d8f863eea3", "suffix": null, "firstname": null, "title": null, "middlename": null, "lastname": null, "imageurl": null, "otherlangs": null, "affiliationinstitution_url": null, "email": null, "version": null, "location": null, "recommendations": null, "preferredlang": null, "fullname": "foobar User", "homepage": null, "affiliationinstitution": null, "biography": null}'


>>> u = usermodel.User()
>>> u.fullname="paul"
>>> i = usermodel.Identifier()
>>> i.identifierstring = "http://fake.open.id"
>>> i.identifiertype = "openid"
>>> u.identifiers=[i,]
>>> db_session.add(u)
>>> db_session.commit()
>>>



>>> u = usermodel.User()
>>> d = {'fullname':'bob', 'identifiers':[{'identifierstring':'http://bob@myopenid.com', 'identifiertype':'openid'},]}
>>> u.from_dict(d)
>>> u
bob-org.cnx.user-00bb0cae-970b-4fc6-87be-0b8b3da35187
>>> u.fullname
'bob'
>>> u.identifiers
[<rhaptos2.user.usermodel.Identifier object at 0x8073e3190>]
>>> u.identifiers[0]
<rhaptos2.user.usermodel.Identifier object at 0x8073e3190>
>>> u.identifiers[0].identifierstring
'http://bob@myopenid.com'
>>> db_session.add(u)
>>> db_session.commit()



"""
import json
import uuid
import pprint

from sqlalchemy import (Table, ForeignKey, or_,
                        Column, Integer, String,
                        Text, Enum)
from sqlalchemy.orm import relationship
import sqlalchemy.types
import datetime


from cnxbase import CNXBase

#shared session from backend module, for pooling

from .backend import Base, DBSession as db_session

def dolog(*args, **kwargs):
    pass

class Rhaptos2Error(Exception):
    """ Custom exception """


############## JSON SUpport
## COde that supports converting to json resides in object.
## code that supports converting form json to object seems to sit best externally
##in both cases shared code resuse seems likely ewe shall move this elsewhere.


def parse_json_user_schema(jsonstr):
    """Ul;timately we should have multiple version handling. """
    return json.loads(jsonstr)

def verify_schema_version(versionstr):
    """This is a placeholder only.
    .. todo:: Handle versions sensibly
    """
    return parse_json_user_schema

def mkobjfromlistofdict(o, l):
    """ Glimmering of recursion style needed
        However too fragile...
    """
    ### really I need to know when to stop - test for list / dict in vlaues///
    outl = []
    for dict_of_fields in l:
        x = o()
        for key in dict_of_fields:
            setattr(x, key, dict_of_fields[key])
        outl.append(x)
    return outl


def put_user(jsond, user_id):
    """Given a user_id, and a json_str representing the "Updated" fields
       then update those fields for that user_id """

    try:
        uobj =get_user(user_id)
    except Exception, e:
        dolog("INFO", str(e))
        raise Rhaptos2Error("FAiled to get user")

    #.. todo:: parser = verify_schema_version(None)
    updated_obj = populate_user(jsond, uobj)
    db_session.add(updated_obj); db_session.commit()
    return updated_obj


def populate_user(incomingd, userobj):
    """Given a dict, and a User object, push dict into User object and return it.

    .. todo:: validate and parse dict.

    """

    ### put every key in json into User(), manually handling
    ### Identifier
    for k in incomingd:
        if k in ('user_id'): continue #.. todo:: test for user_id in a POST
        if k not in (u'identifier', u'identifiers'): ## a poor manual approach...
            setattr(userobj, k, incomingd[k])
        else:
            ### create a list of Identifer objects from the list of
            ### identifier strings in JSON
            l = incomingd[k]
            outl =  mkobjfromlistofdict(Identifier, l)
            userobj.identifiers = outl

    return userobj


def post_user(jsond):
    """Given a dict representing the complete set
       of fields then create a new user and those fields

    I am getting a dictionary direct form Flask request object - want
    to handle that myself with parser.

    returns User object, for later saveing to DB"""

    u = User()

    #parser = verify_schema_version(None)
    #incomingd = parser(json_str)
    incomingd = json_dict
    u = populate_user(incomingd, u)
    db_session.add(u); db_session.commit()
    return u


def get_user(user_id):
    """
    returns a User object, when provided with user_id
    """

    ### Now lets recreate it.

    q = db_session.query(User)
    q = q.filter(User.user_id == user_id)
    rs = q.all()
    if len(rs) == 0:
        raise Rhaptos2Error("User ID Not found in this repo")
    ### There is a uniq constraint on the table, but anyway...
    if len(rs) > 1:
        raise Rhaptos2Error("Too many matches")

    newu = rs[0]
    return newu


def get_user_by_identifier(unquoted_id):
    """ """

    ### Now lets recreate it.

    q = db_session.query(Identifier)
    q = q.filter(Identifier.identifierstring == unquoted_id)
    rs = q.all()

    if len(rs) == 0:
        raise Rhaptos2Error("Identifer ID Not found in this repo")
    if len(rs) > 1:
        raise Rhaptos2Error("Too many matches")

    #.. todo:: stop using indexes on rows - transform to fieldnames
    user_id = rs[0].user_id
    newu = get_user(user_id)
    return newu


def get_user_by_name(namefrag):
    """
    Perform a case insensitive search on fullname

    I would like to offer at least two other searches,
    specifying the fields to search, and a frag search across
    many fields.
    """

    q = db_session.query(User)
    q = q.filter(or_(
                     User.fullname.ilike("%%%s%%" % namefrag),
                     User.email.ilike("%%%s%%" % namefrag),
                     ))
    rs = q.all()
    out_l = []
    for row in rs:
        out_l.append(row)
    return out_l

def get_all_users():
    """ FOr search functionality"""

    q = db_session.query(User)
    rs = q.all()
    out_l = []
    c = 0
    for row in rs:
        out_l.append(row)
        c += 1
        if c >= 25: break
    # ..todo:: the worst limiting case ever...
    return out_l



def delete_user(security_token, user_id):
    """ """
    raise Rhaptos2Error("delete user not supported")


def close_session():
    db_session.remove()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
