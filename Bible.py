#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Bible.py
#
# Module handling a internal Bible object
#
# Copyright (C) 2010-2018 Robert Hunt
# Author: Robert Hunt <Freely.Given.org@gmail.com>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling an internal Bible object.

A class which extends BibleWriter (which itself extends InternalBible).

TODO: Check if we really need this class at all???
"""

from gettext import gettext as _

LastModifiedDate = '2018-12-12' # by RJH
ShortProgName = "BibleObjects"
ProgName = "Bible object handler"
ProgVersion = '0.14'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import logging

import BibleOrgSysGlobals
from InternalBibleBook import InternalBibleBook
from BibleWriter import BibleWriter



#class BibleExtra:
    #"""
    #Class for handling Bible front and back matter.
    #"""

    #def __init__( self ):
        #"""
        #Constructor: creates an empty Bible extra object.
        #"""
        #self.sections = []
    ## end of __init__

    #def __str__( self ):
        #"""
        #This method returns the string representation of a Bible extra section.

        #@return: the name of a Bible object formatted as a string
        #@rtype: string
        #"""
        #result = _("BibleExtra object")
        #result += ('\n' if result else '') + "  " + _("Number of sections = {}").format(len(self.sections) )
        #return result
    ## end of __str__
## end of class BibleExtra


#class BibleDivision:
    #"""
    #Class for handling Bible divisions (like Old Testament and New Testament).
    #"""

    #def __init__( self ):
        #"""
        #Constructor: creates an empty Bible extra object.
        #"""
        #self.shortName, self.longName = '', ''
        #self.inputAbbreviations = []
        #self.bookCodes = []
    ## end of __init__

    #def __str__( self ):
        #"""
        #This method returns the string representation of a Bible division.

        #@return: the name of a Bible object formatted as a string
        #@rtype: string
        #"""
        #result = _("BibleDivision object")
        #result += ('\n' if result else '') + "  {} ({})".format(self.longName, self.shortName )
        #return result
    ## end of __str__
## end of class BibleDivision



class BibleBook ( InternalBibleBook ):
    """
    Class for handling a single Bible book.
        A Bible book consists of a list of tuples.
            Each tuple has two strings:
                a code to label information like section headings, paragraph text, etc.
                the content
        Chapter/Verse information is stored separately in an index (a dictionary)
            The dictionary index is a (C,V) tuple.
            The data is a tuple of
                index into data tuple (0..)
                offset into data tuple (0..)
            This means that the index has to be updated if the data is updated.
    """

    def __init__( self, containerBibleObject, BBB ):
        """
        Constructor: creates an empty Bible book.
        """
        if BibleOrgSysGlobals.debugFlag or BibleOrgSysGlobals.strictCheckingFlag or debuggingThisModule:
            if isinstance( containerBibleObject, str ):
                logging.critical( "containerBibleObject is a string '{}' (not a Bible object): presumably this is a test???".format( containerBibleObject ) )
            else: assert isinstance( containerBibleObject, Bible )

        InternalBibleBook.__init__( self, containerBibleObject, BBB )

        # Define our added data stores
        #self.shortName, self.longName = '', ''
        #self.inputAbbreviations = []
        #self.text = []
        #self.index = {}
        #self.textCodes = ( "ID", "RH1", "MT1", "MT2", "MS1", "MS2", "IOT", "IO1", "IO2", "IS1", "IS2", "InP", "SH1", "SH2", "SXR", "Pgr", "Chp", "Vrs", "Txt", "Qu1", "Qu2", "Qu3", "Qu4", "Blk", "Mar", "FNt", "XRf", "MR" )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book.

        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = _("BibleBook object")
        #result += ('\n' if result else '') + "  {} ({})".format(self.longName, self.shortName )
        #for line in self.text: result += ('\n' if result else '') + "  {}".format(repr(line) )
        return result
    # end of __str__

    #def append( self, stuff ):
        #"""
        #Append the stuff tuple to a Bible book.
        #"""
        #if BibleOrgSysGlobals.debugFlag: assert len(stuff) == 2
        #if BibleOrgSysGlobals.debugFlag: assert stuff[0] in self.textCodes
        #self.text.append( stuff )
    ## end of append

    #def createIndex( self ):
        #""" Create the chapter verse index for this book. """
        #self.index = {}
        #C, V = '0', '0'
        #for j,(code,text) in enumerate(self.text):
            #if code == 'Chp':
                #C, V = text, '0'
                #self.index[ (C,V) ] = j, 0
            #elif code == 'Vrs':
                #V = text
                #self.index[ (C,V) ] = j, 0
        ##print( self.index )
    ## end of createIndex
# end of class BibleBook



class Bible( BibleWriter ):
    """
    Class for handling an entire Bible.

    All the various different flavours of Bible (e.g., USFM, OSIS XML, CSV)
        are based on this class.
    """

    def __init__( self ):
        """
        Constructor: creates an empty Bible object.
        """
        BibleWriter.__init__( self )
        self.objectNameString = 'Bible object (generic/unknown type)'
        self.objectTypeString = 'Unknown'

        self.BibleOrganisationalSystem = None
        # Add our own extended data stores
        #self.metadata = {}
        #self.frontMatter = []
        #self.divisions = []
        #self.actualBooks = []
        #self.backMatter = []
# end of class Bible



def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( "{} V{}".format(ProgName, ProgVersion ) )

    # Since this is only designed to be a base class, it can't actually do much at all
    if BibleOrgSysGlobals.verbosityLevel > 0: print( "\nTest Bible…" )
    B = Bible()
    if BibleOrgSysGlobals.verbosityLevel > 0: print( B )

    #if 0: # No need for this here
        ## Test a single folder containing a USFM Bible
        #if BibleOrgSysGlobals.verbosityLevel > 0: print( "\nTest USFM Bible…" )
        #from USFMBible import USFMBible
        #name, encoding, testFolder = "Matigsalug", 'utf-8', "../../../../../Data/Work/Matigsalug/Bible/MBTV/" # You can put your test folder here
        #if os.access( testFolder, os.R_OK ):
            #UB = USFMBible( testFolder, name, encoding )
            #UB.load()
            #if BibleOrgSysGlobals.verbosityLevel > 0: print( UB )
            #if BibleOrgSysGlobals.strictCheckingFlag:
                #UB.check()
            #UB.doAllExports( "OutputFiles", wantPhotoBible=False, wantODFs=False, wantPDFs=False )
        #else: print( "Sorry, test folder {!r} is not readable on this computer.".format( testFolder ) )
# end of demo

if __name__ == '__main__':
    #multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser, exportAvailable=True )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of Bible.py
