#!/usr/bin/env python
# -*- coding: ascii -*-

# Generic/Built-in
import sys, argparse
import urllib, json
import datetime

# Other Libs
from tinydb import TinyDB, Query

""" Making use of Redmine API to track items for Kanban flow measurement / measuring cycle time

'Having a Kanban board and not being able to measure cycle time is like having a surfboard and not knowing how to swim.'
Comment on 'Measure cycle time (lead time)' - Steve Pryce - https://www.redmine.org/boards/1/topics/49667

This really should be a standard feature. As should time spent in each status.

__author__ = "Alan McNatty"
__copyright__ = "Copyright 2019, Pizza Talk"
__credits__ = ["Alan McNatty"]
__license__ = "MPL 2.0"
__version__ = "0.1.0"
__maintainer__ = "Alan McNatty"
__email__ = "alan@catalyst.net.nz"
__status__ = "Dev"

"""

# {code}

dbase = 'redmine_db.json'                          # Our reporting DB
key   = ''                                         # Redmine API key
base  = ''                                         # Redmine instance
proj  = '/projects/my-demo-project'                # Our project
board = 'Work In Progress'                         # Our Kanban board
start = 'Ready'
stop  = 'Done'

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-d", "--database", help="Database name for storing Redmine item / status details.")
    parser.add_argument("-b", "--base", required=True, help="Base URL for the Redmine instance.")
    parser.add_argument("-p", "--project", help="Redmine project name.")
    parser.add_argument("-k", "--key", required=True, help="Redmine api key.")
    parser.add_argument("-r", "--reset", dest='reset', action='store_true', help="Reset the database.")
    parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    parser.add_argument("-P", "--print",dest='print_only',action='store_true', help="Print only.")
    parser.add_argument("-K", "--board", help="Kanban Board or (Target) Version.")
    options = parser.parse_args(args)
    return options

# -- override any defaults (above)
options = getOptions(sys.argv[1:])
if options.base:
    base = options.base
if options.project:
    proj = '/projects/' + options.project
if options.key:
    key = options.key
if options.database:
    dbase = options.database
if options.board:
    board = options.board

# -- functions

def getStatus(s):
    url = base + "/issue_statuses.json"
    url =  url + '?key=' + key

    response = urllib.urlopen(url)
    j = json.loads(response.read())

    for x in j['issue_statuses']:
        if x['name'] == s:
            return x['id']

def getWIP(n):
    url = base + proj + "/versions.json"
    url =  url + '?key=' + key

    response = urllib.urlopen(url)
    j = json.loads(response.read())

    for x in j['versions']:
        if x['name'] == n:
            return x['id']

def getIssue(i):
    url = base + "/issues/" + str(i) + ".json?key=" + key

    response = urllib.urlopen(url)
    j = json.loads(response.read())

    return j['issue']

def findNewIssues(v, s):
    url = base + proj + "/issues.json?status_id=" + str(s) + "&fixed_version_id=" + str(v)
    url =  url + '&key=' + key

    response = urllib.urlopen(url)
    j = json.loads(response.read())

    Issue = Query()
    for x in j['issues']:
        if not db.search(Issue.id == x['id']):
            x['ready_on'] = x['updated_on'] # a custom field for newly identified 'ready' issues
            if not x.has_key('closed_on'): 
                x['closed_on'] = ""
            if not x.has_key('estimated_hours'): 
                warning("WARNING: RM#" + str(x['id']) + " 'ready' and assigned to " + x['assigned_to']['name'] + " but not sized!")
                x['estimated_hours'] = 0
            db.insert( x ) 
            debug( "DEBUG: adding RM#" + str(x['id']) + "," + x['updated_on'] + ", " + x['assigned_to']['name'])
        else: # TODO - maybe don't update these?
            if x.has_key('closed_on'): 
                x['closed_on'] = ""
                db.update({'closed_on': x['closed_on']}, Issue.id == x['id'])
                debug("DEBUG: previously closed - resetting closed on for RM#" + str(x['id']))
            if x.has_key('estimated_hours'): 
                db.update({'estimated_hours': x['estimated_hours']}, Issue.id == x['id'])
                debug("DEBUG: updating estimated hours for RM#" + str(x['id']))

            db.update({'updated_on': x['updated_on'], 'assigned_to': x['assigned_to'] }, Issue.id == x['id'])
            debug("DEBUG: updating updated on, assigned to for RM#" + str(x['id']))

def updateExisting(s):
    Issue = Query()
    for x in db.search(Issue.closed_on == ""): # this avoids those that move to done but haven't updated closed date yet
        i = getIssue(x['id'])
        if i['status'] == s: # TODO check if closed_on is still "" and set now() ???
            db.update({'closed_on': i['closed_on']}, Issue.id == x['id'])
            debug("DEBUG: status is " + s + ", updating closed on RM#" + str(x['id']))
            
def printDB():
    print "id,created_on,ready_on,updated_on,closed_on,estimated_hours,time_in_minutes"
    for x in db: # TODO do the calendar maths here to report on hours between start and stop
        mins = 0 
        if x['ready_on'] != "" and x['closed_on'] != "": 
            r = datetime.datetime.strptime(x['ready_on'], "%Y-%m-%dT%H:%M:%SZ")
            d = datetime.datetime.strptime(x['closed_on'], "%Y-%m-%dT%H:%M:%SZ")
            dd = d - r
            mins = divmod(dd.days * 86400 + dd.seconds, 60)[0]
        print str(x['id']) + "," + x['created_on'] + "," + x['ready_on'] + "," + x['updated_on'] + "," + x['closed_on'] + "," + str(x['estimated_hours']) + "," + str(mins)

def debug(s):
    _print(s, False)

def warning(s):
    _print(s, True)

def _print(s, e=False):
    if e:
       print >> sys.stderr, s 
    elif options.verbose:
        print s

# -- MAIN --

db = TinyDB(dbase)

if options.reset:
    if options.verbose:
        print "DEBUG: resetting database"
    db.purge()
    db.all()

if not options.print_only: 
    # check board for any unseen 'ready' wip, then check if known ones are now 'done'
    board_id = getWIP(board)
    findNewIssues(board_id, getStatus(start))
    updateExisting(getStatus(stop))

# print (CSV) our view of the world
printDB()
