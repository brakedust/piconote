# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from sqlalchemy import (Integer, String, CHAR, Float, Column, ForeignKey, 
                        create_engine, DateTime)
from sqlalchemy.orm import  relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

from mininote.dbtypes import GUID

# create a configured "Session" class

Base = declarative_base()

Now = lambda : datetime.now()

            
class Note(Base):
    
    __tablename__ = 't_note'
    
    #__tableargs__ = {'sqlite_autoincrement' : True}
    
    NoteID = Column(GUID, primary_key = True)
    Text = Column(String(10000), nullable = False)
    CreateDate = Column(DateTime, nullable = False)
    ModifyDate = Column(DateTime, nullable = False)

    CreatorID = Column(GUID, ForeignKey('t_user.UserID', ondelete='Restrict'))    
    ModifierID = Column(GUID, ForeignKey('t_user.UserID', ondelete='Restrict'))    

    Creator = relationship('User', foreign_keys = [CreatorID])
    Modifier = relationship('User', foreign_keys = [ModifierID])
    #def __init__(self, text = None, note_id = None, when = None, user = None):
    def __init__(self, **kwargs):
        
        self.NoteID = kwargs.get('NoteID',GUID.new_uuid())
        self.CreateDate = kwargs.get('CreateDate',Now())
        self.ModifyDate = kwargs.get('ModifyDate',Now())
        super(Note,self).__init__(**kwargs)
    
    #def __repr__(self):
    #    return "Note(Text={0},NoteID={1},When={2},User={3})".format(repr(self.Text), 
    #                                                                  repr(self.NoteID), 
    #                                                                  repr(self.When),
    #                                                                  repr(self.User))
    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)

class User(Base):
    __tablename__ = 't_user'
    #__tableargs__ = {'sqlite_autoincrement' : True}
    UserID = Column(GUID, primary_key = True)
    UserName = Column(String(50), unique = True)
    
    CreatedNotes = relationship('Note', primaryjoin = UserID == Note.CreatorID)

    def __init__(self, **kwargs):
        self.UserID = kwargs.get('UserID',GUID.new_uuid())
        super(User,self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)

class TagLink(Base):
    __tablename__ = 'link_tags_notes'
    TagID = Column(GUID, ForeignKey('t_tag.TagID'), primary_key = True)
    NoteID = Column(GUID, ForeignKey('t_note.NoteID'), primary_key = True)    

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)

class Tag(Base):

    __tablename__ = 't_tag'

    TagID = Column(GUID,primary_key = True)
    TagName = Column(String(50), unique = True)

    #Must use a Table class for secondary joins.  For a declartive class
    #you can get the Table through the __table__ attribute
    Notes = relationship('Note', secondary = TagLink.__table__)

    def __init__(self, **kwargs):
        self.TagID = kwargs.get('TagID',GUID.new_uuid())
        super(Tag,self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)
    

    
def CreateNote(text,tags, session = None):
    """
    Creates a Note associated with the given tags
    
    Input
        text - str
            the note content
        tags - list
            the tags associated with the note
            
    Returns
        None
        
    Example:
        >>> CreateNote('What is the air speed of a fully laden swallow?',['birds','monty python'])
    """
    global Session
#    
#    docommit = False    
    if session is None:
        session = Session()
#        docommit = True
#        
    me = session.query(User).filter_by(UserName='Superman').first()
    jack = session.query(User).filter_by(UserName='Batman').first()
    note = session.query(Note).filter_by(Text = text).first() 
    if note is None:
        #note = Note(Text = text,CreatorID=me.UserID,ModifierID=jack.UserID)
        note = Note(Text = text)
        note.Creator = me
        note.Modifier = jack
        session.add(note)
    else:
        return
        
    current_tags = [t.TagName for t in session.query(Tag).all()]
    new_tag_items = [Tag(TagName = t) for t in tags 
        if t not in current_tags]        
    session.add_all(new_tag_items)
    mytags = [session.query(Tag).filter_by(TagName=t).first() for t in tags]
    tgl = [TagLink(NoteID = note.NoteID, TagID = t.TagID) for t in mytags]
    session.add_all(tgl)
    #if docommit:    
    session.commit()

def FindNotesByTag(tag):

    session = Session()
        
    mynotes = session.query(Note).join(TagLink, Note.NoteID == TagLink.NoteID).\
        join(Tag, TagLink.TagID == Tag.TagID).filter(Tag.TagName == tag).all()
    
    return mynotes


def CreateDatabase(deleteFirstIfExists = False):
    """
    Creates the database to store the notes in.  Optionally delete an old one
    if it already exissts
    """
    from connection import CreateEngine, CreateDatabase, DropDatabase, dbtype, connection_string

    engine = CreateEngine(connection_string, False)
    if deleteFirstIfExists: DropDatabase(dbtype, engine)
    CreateDatabase(dbtype, engine)

    return engine

            



    
if __name__ == '__main__':
    from pprint import pprint
    from mininote.connection import CreateDatabase, DropDatabase, connection_string
    
    DropDatabase(connection_string,False)
    engine = CreateDatabase(connection_string, False)
    #Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    print('Creating tables')
    Base.metadata.create_all(engine)
    print('done')

    s = Session()    
    
    #if s.query(User).filter_by(UserName = 'Bradley').first() is None:
    u1 = User(UserName = 'Superman')
    u2 = User(UserName = 'Batman')
    s.add(u1)
    s.add(u2)
    s.commit()
        
    CreateNote('Penguins are slow!!!!',['people','villain','animal'])
    CreateNote('Jokers are not funny',['people','villain','comedian'])    
    CreateNote("Is Robin OK?\nI haven't seen him in a while.",['people','sidekick'])
    CreateNote("Lex Luther....",["people","villain"])
    #note = Note(Text = 'Something cool happened')
    #note.User = me
    
    s = Session()
    notes = s.query(Note).all()
    for n in notes:
        print(repr(n))
#    
    print('\nAnimal Notes\n------------')
    pprint(FindNotesByTag('animal'))

    print('\nTags\n------------')
    mytags = s.query(Tag).all()
    pprint(mytags)

    print('\nUsers\n------------')
    pprint(s.query(User).all())
    u=s.query(User).first()
