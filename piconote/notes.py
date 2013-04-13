# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sqlalchemy import String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

from piconote.dbtypes import GUID
from piconote.connection import get_engine
# create a configured "Session" class

Base = declarative_base()

Now = lambda: datetime.now()

engine = get_engine()
Session = sessionmaker(bind=engine)


class Note(Base):

    __tablename__ = 't_note'

    #__tableargs__ = {'sqlite_autoincrement' : True}

    NoteID = Column(GUID, primary_key=True)
    Text = Column(String(10000), nullable=False)
    CreateDate = Column(DateTime, nullable=False)
    ModifyDate = Column(DateTime, nullable=False)

    CreatorID = Column(GUID, ForeignKey('t_user.UserID', ondelete='Restrict'))
    ModifierID = Column(GUID, ForeignKey('t_user.UserID', ondelete='Restrict'))

    Creator = relationship('User', foreign_keys=[CreatorID])
    Modifier = relationship('User', foreign_keys=[ModifierID])

    Tags = relationship('Tag', secondary=lambda: TagLink.__table__)
    #def __init__(self, text = None, note_id = None, when = None, user = None):

    def __init__(self, **kwargs):
        self.NoteID = kwargs.get('NoteID', GUID.new_uuid())
        self.CreateDate = kwargs.get('CreateDate', Now())
        self.ModifyDate = kwargs.get('ModifyDate', Now())
        super(Note, self).__init__(**kwargs)

    def __str__(self):
        return "-" * 80 + """
ID      : {id}
Author  : {c}
Created : {d}
Tags    : {tags}
--TEXT--
{t}""".format(c=self.Creator,
              d=self.CreateDate,
              tags=",".join([t.TagName for t in self.Tags]),
              t=self.Text,
              id=self.NoteID)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k), repr(d[k]))
                             for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__, mykwargs)


class User(Base):
    __tablename__ = 't_user'
    #__tableargs__ = {'sqlite_autoincrement' : True}
    UserID = Column(GUID, primary_key=True)
    UserName = Column(String(50), unique=True)

    CreatedNotes = relationship('Note', primaryjoin=(UserID == Note.CreatorID))

    def __init__(self, **kwargs):
        self.UserID = kwargs.get('UserID', GUID.new_uuid())
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k), repr(d[k]))
                             for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__, mykwargs)


class TagLink(Base):
    __tablename__ = 'link_tags_notes'
    TagID = Column(GUID, ForeignKey('t_tag.TagID'), primary_key=True)
    NoteID = Column(GUID, ForeignKey('t_note.NoteID'), primary_key=True)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k), repr(d[k]))
                             for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__, mykwargs)


class Tag(Base):

    __tablename__ = 't_tag'

    TagID = Column(GUID, primary_key=True)
    TagName = Column(String(50), unique=True)

    #Must use a Table class for secondary joins.  For a declartive class
    #you can get the Table through the __table__ attribute
    Notes = relationship('Note', secondary=TagLink.__table__)

    def __init__(self, **kwargs):
        self.TagID = kwargs.get('TagID', GUID.new_uuid())
        super(Tag, self).__init__(**kwargs)

    def __repr__(self):
        d = self.__dict__
        mykwargs = ", ".join(['{0}={1}'.format(str(k), repr(d[k]))
                             for k in d if k != '_sa_instance_state'])
        return "{0}({1})".format(type(self).__name__, mykwargs)


def create_note(text, tags, session=None):
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
        >>> CreateNote('What is the air speed of a fully laden swallow?',
        ... ['birds','monty python'])
    """
#
#    docommit = False
    if session is None:
        session = Session()
#        docommit = True
#
    me = session.query(User).filter_by(UserName='Superman').first()
    jack = session.query(User).filter_by(UserName='Batman').first()
    note = session.query(Note).filter_by(Text=text).first()
    if note is None:
        #note = Note(Text = text,CreatorID=me.UserID,ModifierID=jack.UserID)
        note = Note(Text=text)
        note.Creator = me
        note.Modifier = jack
        session.add(note)
    else:
        return

    current_tags = [t.TagName for t in session.query(Tag).all()]
    new_tag_items = [Tag(TagName=t) for t in tags
        if t not in current_tags]
    session.add_all(new_tag_items)
    mytags = [session.query(Tag).filter_by(TagName=t).first() for t in tags]
    tgl = [TagLink(NoteID=note.NoteID, TagID=t.TagID) for t in mytags]
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
