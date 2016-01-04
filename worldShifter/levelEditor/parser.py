#!/usr/bin/env python

#@DESC
'''
This module writes and reads/parses level data in the format defined
below:

OBJECT-TYPE
    COORDS

'''

import pickle as p
from const2 import *

def sanitise(string):
    """
    sanitises level data
    """
    ns = ''
    wspace = 0

    for each in string:
        if each != '\n' and each != ' ':
            ns += each
            wspace = 0

        if each == '\n':
            ns += ' '

        if each == ' ' and wspace == 0:
            ns += each
            wspace = 1

    liste = ns.split(' ')
    liste = [each for each in liste if each != '']

    return liste


def write_level():
    """
    Writes the level data
    """
    with open(itemDictFile, 'r') as myFile:
        itemDict = p.load(myFile)

    dumpString = ""

    for itemType in itemDict.keys():
        for coords in itemDict[itemType]:
            dumpString += itemType + "\n"
            dumpString += "    " + str(coords[0]) + " " + str(coords[1]) + "\n"

    dumpString += "SCREENSIZE\n"
    dumpString += "    " + str(SCREEN_W) + " " + str(SCREEN_H - PANEL_H) + "\n"
    with open(levelFile, 'w') as lFile:
        lFile.write(dumpString)

# TO BE USED ONLY BY THE MAIN PROGRAM
def parse_level():
    """
    parses level dump data to create a level
    """

    with open(levelFile, 'r') as lFile:
        dat = lFile.read()

    return sanitise(dat)
