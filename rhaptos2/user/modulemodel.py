################################# for module/editor
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
        


