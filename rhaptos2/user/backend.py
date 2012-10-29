


"""

This focuses on postgres


Ship.__table__.columns will provide you with columns information
Ship.__table__.foreign_keys will list foreign keys
Ship.__table__.constraints, Ship.__table__.indexes are other properties you might find useful

# Basics - I want to 
#1. Set up a simple working version that 
#2. setup tests
#3. get a jsonifiable solution to support 1:m and M;N relations
#4. work this as standa lone with tests so it can bio-directionally deal with User JSON and later modul#e JSON
#   and do so standalo=ne in tests
#http://docs.sqlalchemy.org/en/rel_0_7/orm/relationships.html


"""


from sqlalchemy import create_engine, MetaData, Table, ForeignKey
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship



### Module globals.  Following Pylons lead, having global
### scoped_session will ensure threads (and thread locals in Flask)
### all have theit own sessions

Session = scoped_session(sessionmaker(autoflush=True,
                                      autocommit=False,))

Base = declarative_base()
### As long as we subclass everything from Base, we are following
### ndeclarative pattern recommended

engine = None
### leave it for ad hoc queries...

def connect_now(confd):
    connstr = "postgresql+psycopg2://%(rhaptos2user_pgusername)s:%(rhaptos2user_pgpassword)s@%(rhaptos2user_pghost)s/%(rhaptos2user_pgusername)s" % confd
    engine = create_engine(connstr)
    return engine


def bind(engine):

    global Session
    Session.configure(bind=engine)


def initdb(confd):
    global engine
  
    engine = connect_now(confd)
    bind(engine)
    Base.metadata.create_all(engine)    
    


#def is_alive(confd):
#    
#    m = Module(user_id='12345',title='swag',content='XXX')
#    Session.add(m)
#    Session.commit()
#    print m



keywd_link = Table(
    'keywd_link', Base.metadata,
    Column('user_id', String, ForeignKey('module.user_id')),
    Column('keyword_id', Integer, ForeignKey('keyword.keyword_id'))
    )

class Keyword(Base):
    """ """
    __tablename__ = 'keyword'
    keyword_id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True)
    

class Module(Base):
    """

    This is also the class returned from a query ... v useful.

    """
    __tablename__ = 'module'
    user_id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    keywords = relationship("Keyword", secondary=keywd_link)
    

    #not really needed ... will use above definitoon
    def __init__(self, user_id=None, title=None, content=None):
        self.user_id = user_id
        self.title = title
        self.content = content

    def row_as_dict(self):
        """Return the """
        d = {}
        for col in self.__table__.columns:
            d[col.name] = self.__dict__[col.name]
        return d
  
   

    def __repr__(self):
        return "Module:(%s)-%s" % (self.user_id, self.title)
        


