# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser

from piconote.connection import create_database, drop_database, connection_string
from piconote.notes import (Base, create_note, find_text_in_note,
    find_by_tag, get_tags)

def run(inargs):
    
    parser = ArgumentParser(prog = 'piconote', prefix_chars = '-/', 
                            description = "A simple note taking app")
    parser.add_argument('-n', '--new', help = 'Create a new note', 
                        action = 'store_const', const=True,default=False)
    parser.add_argument('-s', '--search', help = 'Finds notes',
                        action = 'store_const', const=True, default=False)
    parser.add_argument('-tags',help = 'List of tags',
                        type = str, nargs='*')
    parser.add_argument('-text',help = 'Note text to create or search for.',
                        type = str)
                        
    parser.add_argument('--create_database',help='Creates the initial database',
                        action='store_const',const=True,default=False)
    parser.add_argument('--delete_database',help='Deletes the piconote database',
                        action='store_const',const=True,default=False)
    
    parser.add_argument('--listtags',action='store_const',const=True,default=False)
        
    
    args = parser.parse_args(inargs[1:])
    #print(args)
    if args.create_database:
        print('Creating database')        
        engine = create_database(connection_string)
        Base.metadata.create_all(engine)
    
    if args.delete_database:        
        answer = input("Do you want to delete the database (y/n)? ")
        if answer.lower() in ('y','yes','1'):
            answer = input("Do you REALLY want to delete the database (y/n)? ")
            if answer.lower() in ('y','yes','1'):
                print('Deleting database')            
                drop_database(connection_string)
    if args.new:
        if args.text is None:
            print('You must use the -text option when creating a new note')
        if len(args.tags) < 1:
            print('You must use the -tags option when creating a new note')
            
        create_note(args.text, args.tags)
            
    if args.search:
        
        if args.text is not None:
            mynotes = find_text_in_note(args.text)
                
        if args.tags is not None:
            mynotes = find_by_tag(args.tags[0])
        
        print('Search found {n} note(s).'.format(n=len(mynotes)))
        for note in mynotes:
            print(str(note))
            
    if args.listtags:
        print("\n".join(get_tags()))
        
if __name__ == "__main__":
    run(sys.argv)    