# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from sqlalchemy import (Integer, String, CHAR, Float, Column, ForeignKey, 
                        create_engine, DateTime, text)
from sqlalchemy.orm import  relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
from uuid import uuid1

from piconote.dbtypes import GUID_Char, GUID_Binary
from piconote.connection import get_engine
# create a configured "Session" class

import getpass
username = getpass.getuser()
        
Base = declarative_base()

Now = lambda : datetime.now()

engine = get_engine()
Session = sessionmaker(bind=engine)

prikeytype = GUID_Char
            
class Note(Base):
    
    __tablename__ = 't_note'
    
    #__tableargs__ = {'sqlite_autoincrement' : True}
    
    #NoteID = Column(GUID, primary_key = True, server_default = text("'\x00\x00\x00\x00\x00\x00\x11\xe2\x00\x00 \xcf0>\xcbR'"))
    NoteID = Column(prikeytype, primary_key = True)
    Text = Column(String(10000), nullable = True, server_default = text('NULL'))
    CreateDate = Column(DateTime, nullable = True, server_default = text('NULL'))
    ModifyDate = Column(DateTime, nullable = True, server_default = text('NULL'))

    CreatorID = Column(prikeytype, ForeignKey('t_user.UserID', ondelete='CASCADE'),server_default = text('NULL'))    
    ModifierID = Column(prikeytype, ForeignKey('t_user.UserID', ondelete='SET NULL'),server_default = text('NULL'))    

    Creator = relationship('User', foreign_keys = [CreatorID])
    Modifier = relationship('User', foreign_keys = [ModifierID])
    
    Tags = relationship('Tag', secondary = lambda : TagLink.__table__)
    #def __init__(self, text = None, note_id = None, when = None, user = None):
    def __init__(self, **kwargs):
        
        self.NoteID = kwargs.get('NoteID',uuid1())
        self.CreateDate = kwargs.get('CreateDate',Now())
        self.ModifyDate = kwargs.get('ModifyDate',Now())
        super(Note,self).__init__(**kwargs)
    
    
    def __str__(self):
        
        return "-"*80 + """
ID      : {id}
Author  : {c}
Created : {d}
Tags    : {tags}
--TEXT--
{t}""".format(c=self.Creator,
              d = self.CreateDate,
              tags = ",".join([t.TagName for t in self.Tags]),
              t = self.Text,
              id = self.NoteID)
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
    UserID = Column(prikeytype, primary_key = True, server_default = text('NULL'))
    UserName = Column(String(50), unique = True, server_default = text('NULL'), default = username)
    
    CreatedNotes = relationship('Note', primaryjoin = UserID == Note.CreatorID)

    def __init__(self, **kwargs):
        self.UserID = kwargs.get('UserID',uuid1())
        super(User,self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)

class TagLink(Base):
    __tablename__ = 'link_tags_notes'
    TagID = Column(prikeytype, ForeignKey('t_tag.TagID'), primary_key = True)
    NoteID = Column(prikeytype, ForeignKey('t_note.NoteID'), primary_key = True)    

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)

class Tag(Base):

    __tablename__ = 't_tag'

    TagID = Column(prikeytype,primary_key = True)
    TagName = Column(String(50), unique = True)

    #Must use a Table class for secondary joins.  For a declartive class
    #you can get the Table through the __table__ attribute
    Notes = relationship('Note', secondary = TagLink.__table__)

    def __init__(self, **kwargs):
        self.TagID = kwargs.get('TagID',uuid1())
        super(Tag,self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k),repr(d[k])) for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__,mykwargs)
    

    
def create_note(text,tags, session = None):
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
#    
#    docommit = False    
    if session is None:
        session = Session()
#        docommit = True
#        
    me = session.query(User).filter_by(UserName=username).first()
    if me is None:
        session.add(me)
    session.commit()
    note = session.query(Note).filter_by(Text = text).first() 
    if note is None:
        #note = Note(Text = text,CreatorID=me.UserID,ModifierID=jack.UserID)
        note = Note(Text = text)
        note.Creator = me
        #note.Modifier = jack
        session.add(note)
    else:
        return
    
    current_tags = session.query(Tag).all()
    if current_tags is not None:
        current_tags = [t.TagName for t in current_tags]
    new_tag_items = [Tag(TagName = t) for t in tags 
                     if t not in current_tags]        
    session.add_all(new_tag_items)
    mytags = [session.query(Tag).filter_by(TagName=t).first() for t in tags]
    tgl = [TagLink(NoteID = note.NoteID, TagID = t.TagID) for t in mytags]
    session.add_all(tgl)
    #if docommit:    
    session.commit()

def find_by_tag(tag_name):
    
    session = Session()
        
    #mynotes = session.query(Note).join(TagLink, Note.NoteID == TagLink.NoteID).\
    #    join(Tag, TagLink.TagID == Tag.TagID).filter(Tag.TagName == tag).all()

    tag = session.query(Tag).filter(Tag.TagName == tag_name).first()
    
    return tag.Notes


def get_tags():
    
    session = Session()
    
    tags = session.query(Tag).all()
    
    tagnames = [t.TagName for t in tags]
    
    return tagnames

def find_text_in_note(text):
    
    session = Session()
    mynotes = session.query(Note).filter(Note.Text.contains(text)).all()
    return mynotes
    
#def create_database(deleteFirstIfExists = False):
#    """
#    Creates the database to store the notes in.  Optionally delete an old one
#    if it already exissts
#    """
#    from connection import CreateEngine, CreateDatabase, DropDatabase, dbtype, connection_string
#
#    engine = CreateEngine(connection_string, False)
#    if deleteFirstIfExists: DropDatabase(dbtype, engine)
#    CreateDatabase(dbtype, engine)
#
#    return engine

            



    
if __name__ == '__main__':
    pass