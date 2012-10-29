"""
"""
import json
import uuid
import pprint

from sqlalchemy import Table, ForeignKey
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import  relationship

from rhaptos2.user.backend import Base, db_session      #shared session from backend module, for pooling
from rhaptos2.common.err import Rhaptos2Error



################## User test

class User(Base):
    """declarative class for user_details

    
    """
    __tablename__ = "user" 
    
    user_id     = Column(String, primary_key=True)
    firstname   = Column(String)
    middlename  = Column(String)
    lastname    = Column(String)
    
    identifier  = relationship("Identifier")

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
        """Return the """
        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.__dict__[col.name]

        d['identifier'] = [] 
        for i in self.identifier: 
            d['identifier'].append(i.row_as_dict())
        return d

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

class Identifier(Base):
    """The external-to-cnx, globally unique identifer string that 
       is the 'username' a person claims to be, and needs verification
       from a thrid party to us, the relying party.

    """
    __tablename__   = "identifier"

    identifierstring = Column(String, primary_key=True)
    identifiertype   = Column(String)                      # (Enum, "persona", "openid")
    user_id          = Column(String, ForeignKey("user.user_id"))
    
    
    def __init__(self, identifierstring=None, identifiertype=None):
        """ """
        self.identifierstring =identifierstring
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

    pass

def populate_user(incomingd, userobj):
    """not quite clear the benefits of this one apart form testing
       feel need to work with parser mpore"""

    ### put every key in json into User(), manually handling Identifier
    for k in incomingd:
        if k in ('user_id'): continue #.. todo:: test for user_id in a POST 
        if k not in (u'identifier',): ## a poor manual approach...
            setattr(userobj, k, incomingd[k])
        else:
            ### create a list of Identifer objects from the list of identifier strings in JSON
            l = incomingd[k]
            outl =  mkobjfromlistofdict(Identifier, l)
            userobj.identifier = outl

    return userobj
    

def post_user(security_token, json_str):
    """Given a user_id, and a json_str representing the complete set of fields
       then update those fields for that user_id 

    returns user_id string (uuid)"""

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

    parser = verify_schema_version(None)
    incomingd = parser(json_str)

    u = populate_user(incomingd, u)

    return u.user_id

        
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

def delete_user(security_token, user_id):
    """ """
    raise Rhaptos2Error("delete user not supported")


def close_session():
    db_session.remove()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
