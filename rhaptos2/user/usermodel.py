#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###


"""
usermodel.py

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


"""
import json
import uuid
import pprint

from sqlalchemy import (Table, ForeignKey, or_,
                        Column, Integer, String,
                        Text, Enum)
from sqlalchemy.orm import relationship

#shared session from backend module, for pooling
from rhaptos2.user.backend import Base, db_session      
from rhaptos2.common.err import Rhaptos2Error



################## User test

class User(Base):
    """declarative class for user_details

    
    """
    __tablename__ = "cnxuser" 
    
    user_id                      = Column(String, primary_key=True)
    title                        = Column(String)
    firstname                    = Column(String)
    middlename                   = Column(String)
    lastname                     = Column(String)
    suffix                       = Column(String)
    fullname                     = Column(String)
    interests                    = Column(String)
    affiliationinstitution_url   = Column(String)
    affiliationinstitution       = Column(String)
    preferredlang                = Column(String)
    otherlangs                   = Column(String)
    imageurl                     = Column(String)
    location                     = Column(String)
    biography                    = Column(String)
    recommendations              = Column(String)
    homepage                     = Column(String)
    email                        = Column(String)
    version                      = Column(String)
         
    identifiers  = relationship("Identifier")

    def __init__(self, user_id=None, **kwds):
        """ """

        if user_id is None: 
            self.set_new_id()
        else: 
            self.user_id = user_id 

        for k in kwds:
            self.__dict__[k] = kwds[k]  #.. todo:: dangerous !!

        ##.. todo:: check for failure to provide user_id

    def row_as_dict(self):
        """Return self as a dict, suitable for jsonifying """
        d = {}
        for col in self.__table__.columns:
            ##We can have a field name and nothing set in self...
            if col.name not in self.__dict__.keys():
                d[col.name] = None
            else:
                d[col.name] = self.__dict__[col.name]

        d['identifiers'] = [] 
        for i in self.identifiers: 
            d['identifiers'].append(i.row_as_dict())
        return d

    def jsonify(self):
        """Helper function that returns simple json repr """
        selfd = self.row_as_dict()
        jsonstr = json.dumps(selfd)
        return jsonstr

    def set_new_id(self):
        """If we are new user, be able to create uuid 
       
        ### .. todo: A new User() autosets uuid. Is this correct
        ### behaviour?

        >>> u = User()
        >>> x = u.set_new_id() # +doctest.ELLIPSIS
        >>> assert x == u.user_id
          

        """
        if self.user_id is not None: return self.user_id

        uid = uuid.uuid4()
        self.user_id =  "org.cnx.user-" + str(uid)
        return self.user_id

    def __repr__(self):
        return "%s-%s" % (self.fullname, self.user_id)

class Identifier(Base):
    """The external-to-cnx, globally unique identifer string that 
       is the 'username' a person claims to be, and needs verification
       from a thrid party to us, the relying party.

    """
    __tablename__   = "cnxidentifier"

    identifierstring = Column(String, primary_key=True)
    identifiertype   = Column(String)  # (Enum, "persona", "openid")
    user_id          = Column(String, ForeignKey("cnxuser.user_id"))
    
    
    def __init__(self, identifierstring=None, identifiertype=None):
        """ """
        self.identifierstring = identifierstring
        self.identifiertype = identifiertype
        
        
    def row_as_dict(self):
        """Return the """
        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.__dict__[col.name]
        return d


###########


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


def put_user(security_token, json_str, user_id):
    """Given a user_id, and a json_str representing the "Updated" fields
       then update those fields for that user_id """

    #get User()
    #parse JSON
    #update
    #session add commit
    #return result
    #handle errors

    raise NotImplementedError

def populate_user(incomingd, userobj):

    """not quite clear the benefits of this one apart form testing
       feel need to work with parser mpore"""

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
    

def post_user(security_token, json_dict):
    """Given a user_id, and a json_str representing the complete set
       of fields then update those fields for that user_id

    I am getting a dictionary direct form Flask request object - want
    to handle that myself with parser.

    returns User object, for later saveing to DB"""

    #get User()
    #parse JSON
    #create new user
    #session add commit
    #return result
    #handle errors

    u = User()

    print u.user_id
    u.set_new_id()
    print u.user_id

    #parser = verify_schema_version(None)
    #incomingd = parser(json_str)

    incomingd = json_dict
    u = populate_user(incomingd, u)

    return u

        
def get_user(security_token, user_id):
    """ """

    ### Now lets recreate it.

    q = db_session.query(User)
    q = q.filter(User.user_id == user_id)
    rs = q.all()
    if len(rs) == 0:
        raise Rhaptos2Error("User ID Not found in this repo")
    if len(rs) > 1:
        raise Rhaptos2Error("Too many matches")
    
    newu = rs[0]
    newu_asdict = newu.row_as_dict()
    return json.dumps(newu_asdict)

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

    print rs    

    #.. todo:: stop using indexes on rows - transform to fieldnames
    user_id = rs[0].user_id
    newu = get_user(None, user_id)#now look her up again
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
