#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ISO_639_3_Languages.py
#
# Module handling ISO_639_3
#
# Copyright (C) 2010-2019 Robert Hunt
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
Module handling ISO_639_3_Languages.
"""

from gettext import gettext as _

LastModifiedDate = '2019-09-19' # by RJH
ShortProgName = "ISOLanguages"
ProgName = "ISO 639_3_Languages handler"
ProgVersion = '0.85'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import os

from singleton import singleton
import BibleOrgSysGlobals


@singleton # Can only ever have one instance
class ISO_639_3_Languages:
    """
    Class for handling ISO_639_3_Languages.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor:
        """
        self.__IDDict, self.__NameDict = None, None # We'll import into this in loadData
    # end of ISO_639_3_Languages.__init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.

        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "ISO_639_3_Languages object"
        if BibleOrgSysGlobals.debugFlag: assert len(self.__IDDict) == len(self.__NameDict)
        result += ('\n' if result else '') + "  Number of entries = {}".format( len(self.__IDDict) )
        return result
    # end of ISO_639_3_Languages.__str__

    def loadData( self, XMLFilepath=None ):
        """ Loads the pickle or XML data file and imports it to dictionary format (if not done already). """
        if not self.__IDDict and not self.__NameDict: # Don't do this unnecessarily
            # See if we can load from the pickle file (faster than loading from the XML)
            dataFilepath = os.path.join( os.path.dirname(__file__), "DataFiles/" )
            standardXMLFilepath = os.path.join( dataFilepath, "iso_639_3.xml" )
            standardPickleFilepath = os.path.join( dataFilepath, "DerivedFiles", "iso_639_3_Languages_Tables.pickle" )
            if XMLFilepath is None \
            and os.access( standardPickleFilepath, os.R_OK ) \
            and os.stat(standardPickleFilepath).st_mtime > os.stat(standardXMLFilepath).st_mtime \
            and os.stat(standardPickleFilepath).st_ctime > os.stat(standardXMLFilepath).st_ctime: # There's a newer pickle file
                import pickle
                if BibleOrgSysGlobals.verbosityLevel > 2: print( "Loading pickle file {}…".format( standardPickleFilepath ) )
                with open( standardPickleFilepath, 'rb') as pickleFile:
                    self.__IDDict, self.__NameDict = pickle.load( pickleFile ) # The protocol version used is detected automatically, so we do not have to specify it
            else: # We have to load the XML
                from ISO_639_3_LanguagesConverter import ISO_639_3_LanguagesConverter
                self._lgC = ISO_639_3_LanguagesConverter()
                self._lgC.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
                self.__IDDict, self.__NameDict = self._lgC.importDataToPython() # Get the various dictionaries organised for quick lookup
                del self._lgC # Now the converter class (that handles the XML) is no longer needed
        return self
    # end of ISO_639_3_Languages.loadData

    def __len__( self ):
        """ Returns the number of languages loaded. """
        assert len(self.__IDDict) >= len(self.__NameDict)
        return len(self.__IDDict)

    def isValidLanguageCode( self, ccc ):
        """ Returns True or False. """
        return ccc in self.__IDDict

    def getLanguageName( self, ccc ):
        """ Return the language name for the given language code. """
        return self.__IDDict[ccc][0] # The first field is the name

    def getScope( self, ccc ):
        """ Return the scope ('I','M' or 'S') for the given language code.
                I = individual language
                M = macrolanguage
                S = special code """
        return self.__IDDict[ccc][1] # The second field is the scope

    def getType( self, ccc ):
        """ Return the type ('A','C','E','H','L' or 'S') for the given language code.
                A = ancient (extinct since ancient times)
                C = constructed
                E = extinct (in recent times)
                H = historical (distinct from its modern form)
                L = living
                S = special code """
        return self.__IDDict[ccc][2] # The third field is the type

    def getPart1Code( self, ccc ):
        """ Return the optional 2-character ISO 639-1 code for the given language code (or None). """
        return self.__IDDict[ccc][3] # The fourth field is the (optional) part1code

    def getPart2Code( self, ccc ):
        """ Return the optional 3-character ISO 639-2B code for the given language code (or None). """
        return self.__IDDict[ccc][4] # The fifth field is the (optional) part2code

    def getLanguageCode( self, name ):
        """ Return the 3-character code for the given language name (or None if one can't be found). """
        UCName = name.upper() # Convert to UPPERCASE for searching
        if UCName in self.__NameDict: return self.__NameDict[UCName]

    def getNameMatches( self, namePortion ):
        """ Return a list of matching names for the given part of a name.
            This is slow because it is a brute-force search.
        """
        UCNamePortion = namePortion.upper()
        results = []
        for UCName in self.__NameDict:
            if UCNamePortion in UCName:
                ccc = self.__NameDict[UCName]
                results.append( self.__IDDict[ccc][0] ) # Get the mixed case language name
        return results
# end of ISO_639_3_Languages class


def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if BibleOrgSysGlobals.verbosityLevel > 1: print( ProgNameVersion )

    # Demo the languages object
    lg = ISO_639_3_Languages().loadData() # Doesn't reload the XML unnecessarily :)
    print( lg ) # Just print a summary
    for testCode in ('qwq','mbt','MBT','abk',):
        print( "  Testing {}…".format( testCode ) )
        if not lg.isValidLanguageCode( testCode ):
            print( "    {} not found".format( testCode ) )
        else:
            print( "    {} -> {}".format( testCode, lg.getLanguageName( testCode ) ) )
            print( "    Scope is {}, Type is {}".format( lg.getScope(testCode), lg.getType(testCode) ) )
            part1Code, part2Code = lg.getPart1Code(testCode), lg.getPart2Code(testCode)
            if part1Code is not None: print( "    Part1 code is {}".format(part1Code) )
            if part2Code is not None: print( "    Part2 code is {}".format(part2Code) )
    for testName in ('English','German','Deutsch','French','Ayta, Abellen','Manobo, Matigsalug','Manobo','SomeName',):
        print( "  Testing {}…".format( testName ) )
        code = lg.getLanguageCode( testName )
        if code is None:
            print( "    {} not found".format( testName ) )
        else:
            print( "    {} -> {}".format( testName, code ) )
    for testNamePortion in ('English','German','Deutsch','French','Ayta, Abellen','Manobo, Matigsalug','Manobo','SomeName',):
        print( "  Testing {}…".format( testNamePortion ) )
        matches = lg.getNameMatches( testNamePortion )
        for match in matches:
            print( "    Found {} = {}".format( lg.getLanguageCode(match), match ) )
        else: print( "    {} not found".format( testNamePortion ) )
# end of demo

if __name__ == '__main__':
    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of ISO_639_3_Languages.py
