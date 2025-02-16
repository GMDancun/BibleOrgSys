#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Door43ContentServiceOnline.py
#
# Module handling online DCS resources
#
# Copyright (C) 2019 Robert Hunt
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
This module interfaces with the online Bible versions available
    from Door43 content service (unfoldingWord) API.

In this module, we use:
    DCS = Door43 content service

We currently use version 1.4.1 of the DCS.

More details are available from https://api-info.readthedocs.io/en/latest/dcs.html
                            and https://git.door43.org/api/swagger.
"""

from gettext import gettext as _

LastModifiedDate = '2019-05-02' # by RJH
ShortProgName = "Door43ContentService"
ProgName = "Door43 Content Service online handler"
ProgVersion = '0.03'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


from singleton import singleton
import os, logging
import urllib.request
import json
import tempfile, zipfile
from datetime import datetime

import BibleOrgSysGlobals
from USFMBible import USFMBible


URL_BASE = 'https://git.door43.org/api/' # API endpoint
DCS_API_VERSION = '1'
URL_FULL_BASE = f'{URL_BASE}/v{DCS_API_VERSION}/'



@singleton # Can only ever have one instance
class DCSBibles:
    """
    Class to download and manipulate online DCS Bibles.

    """
    def __init__( self ):
        """
        Create the internal Bibles object.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( _("DCSBibles.__init__()…") )

        # See if the site is online by making a small call to get the API version
        self.onlineVersion = None
        result = self.getOnlineData( 'version' )
        #print( "version result", result )
        if result and isinstance( result, dict) and 'version' in result:
            self.onlineVersion = result['version']
            if debuggingThisModule and BibleOrgSysGlobals.verbosityLevel > 3:
                print( f"DCS API version {self.onlineVersion} is online." )
        self.languageList = self.versionList = self.volumeList = self.volumeNameDict = self.EnglishVolumeNameDict = None
    # end of DCSBibles.__init__


    def getOnlineData( self, fieldREST, additionalParameters=None ):
        """
        Given a string, e.g., "api/apiversion"
            Does an HTTP GET to our site.
            Receives the JSON result (hopefully)
            Converts the JSON bytes to a JSON string
            Loads the JSON string into a Python container.
            Returns the container.

        Returns None if the data cannot be fetched.
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( f"DCSBibles.getOnlineData( '{fieldREST}', '{additionalParameters}' )…" )

        requestString = f'{URL_FULL_BASE}{fieldREST}'
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "Request string is", repr(requestString) )
        try: HTTPResponseObject = urllib.request.urlopen( requestString )
        except urllib.error.URLError as err:
            #errorClass, exceptionInstance, traceback = sys.exc_info()
            #print( '{!r}  {!r}  {!r}'.format( errorClass, exceptionInstance, traceback ) )
            logging.error( "DCS URLError '{}' from {}".format( err, requestString ) )
            return None
        #print( "  HTTPResponseObject", HTTPResponseObject )
        contentType = HTTPResponseObject.info().get( 'content-type' )
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( f"    contentType='{contentType}'" )
        if 'application/json' in contentType:
            responseJSON = HTTPResponseObject.read()
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "      responseJSON", len(responseJSON), responseJSON[:100], '…' )
            responseJSONencoding = HTTPResponseObject.info().get_content_charset( 'utf-8' )
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "      responseJSONencoding", responseJSONencoding )
            responseSTR = responseJSON.decode( responseJSONencoding )
            if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                print( "      responseSTR", len(responseSTR), responseSTR[:100], '…' )
            return json.loads( responseSTR )
        else:
            if BibleOrgSysGlobals.debugFlag or debuggingThisModule:
                print( "    contentType", contentType )
            halt # Haven't had this contentType before
    # end of DCSBibles.getOnlineData


    def fetchAllBibles( self ):
        """
        Download the Bible lists from DCS.

        This can be quite slow.

        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( "DCSBibles.fetchAllBibles()…" )

        if BibleOrgSysGlobals.verbosityLevel > 1:
            print( _("Downloading list of available Bibles from DCS…") )

        if self.onlineVersion: # Get a list of available data sets
            self.BibleList = []
            # Does a case-insensitive search
            for searchText in ('Bible', 'ULT', 'UST',): # 'ULB', 'UDB'): # 7,227 if these are all included!!!
                pageNumber = 1
                while True:
                    if BibleOrgSysGlobals.verbosityLevel > 1:
                        print( f"  Getting '{searchText}' page {pageNumber}…" )
                    resultDict = self.getOnlineData( f'repos/search?q={searchText}&page={pageNumber}&limit=50' )
                    #print( f"  Result = {resultDict}" )
                    assert resultDict and isinstance( resultDict, dict) and  len(resultDict) == 2 \
                                    and resultDict['ok']==True
                    if not resultDict['data']: break # no more data
                    self.BibleList.extend( resultDict['data'] )
                    pageNumber += 1
            if BibleOrgSysGlobals.debugFlag: print( "  BibleList", len(self.BibleList) , self.BibleList )
        return self.BibleList
    # end of DCSBibles.fetchAllBibles


    #def fetchAllVersions( self ):
        #"""
        #Download the version lists from unfoldingWord.

        #This can be quite slow.

        #Populates self.versionList (323 entries as of 2014-10)

        #Each list entry is a dictionary, e.g.
            #{'version_name': '', 'version_code': 'ABB', 'english_name': ''}
            #{'version_name': '', 'version_code': 'ABM', 'english_name': ''}
            #{'version_name': '', 'version_code': 'ABS', 'english_name': ''}
            #…
            #{'version_name': 'Biblia de América', 'version_code': 'BDA', 'english_name': ' Biblia de America'}
            #{'version_name': 'Hermanos Libres del Ecuador', 'version_code': 'HLE', 'english_name': ' Hermanos Libres del Ecuador'}
            #{'version_name': '1545 Luther Bibel', 'version_code': 'L45', 'english_name': '1545 Luther Bibel'}
            #…
            #{'version_name': 'Yessan-Mayo Yamano Version', 'version_code': 'YYV', 'english_name': 'Yessan-Mayo Yamano Version'}
            #{'version_name': 'Yessan-Mayo Yawu', 'version_code': 'YWV', 'english_name': 'Yessan-Mayo Yawu'}
            #{'version_name': 'Ze Zoo Zersion', 'version_code': 'ZZQ', 'english_name': 'Ze Zoo Zersion'}
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("DCSBibles.fetchAllVersions()") )

        #if BibleOrgSysGlobals.verbosityLevel > 2:
            #print( _("Downloading list of available versions from unfoldingWord…") )

        #if self.onlineVersion: # Get a list of available data sets
            #self.versionList = self.getOnlineData( 'library/version' ) # Get an alphabetically ordered list of dictionaries -- one for each version
            #if BibleOrgSysGlobals.debugFlag: print( "  versionList", len(self.versionList) )#, self.versionList )
        #return self.versionList
    ## end of DCSBibles.fetchAllVersions


    def __str__( self ):
        """
        Create a string representation of the DCSBibles object.
        """
        indent = 2
        result = "DCS online Bibles object"
        if self.onlineVersion: result += ('\n' if result else '') + ' '*indent + _("Online version: {}").format( self.onlineVersion )
        if self.languageList: result += ('\n' if result else '') + ' '*indent + _("Languages: {}").format( len(self.languageList) )
        if self.versionList: result += ('\n' if result else '') + ' '*indent + _("Versions: {}").format( len(self.versionList) )
        if self.volumeList: result += ('\n' if result else '') + ' '*indent + _("Volumes: {}").format( len(self.volumeList) )
        if self.volumeNameDict: result += ('\n' if result else '') + ' '*indent + _("Displayable volumes: {}").format( len(self.volumeNameDict) )
        return result
    # end of DCSBibles.__str__


    #def searchNames( self, searchText ):
        #"""
        #"""
        #if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            #print( _("DCSBibles.searchNames( {!r} )").format( searchText ) )

        #searchTextUC = searchText.upper()
        #resultsList = []
        #for name in self.volumeNameDict:
            #if searchTextUC in name.upper():
                #for refNumber in self.volumeNameDict[name]:
                    #DAM = self.getDAM(refNumber)
                    #if BibleOrgSysGlobals.debugFlag:
                        #print( _("DAM: {}").format( DAM ) )
                        #if BibleOrgSysGlobals.debugFlag:
                            #assert DAM.endswith('2ET') or DAM.endswith('1ET') # O2 (OT) or N2 (NT), plus ET for text
                    #resultsList.append( (refNumber,DAM,) )
        #return resultsList
    ## end of DCSBibles.searchNames


    def searchRepos( self, repoOwner=None, repoTitle=None ):
        """
        Search thru the list of available online Bibles to find
            a match of the optional title and optional owner.

        Returns the dictionary for the resource
            (or a list of dictionaries if there's multiple matches)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( f"DCSBibles.searchRepos( {repoOwner!r}, {repoTitle!r} )" )

        resultsList = []
        for entryDict in self.BibleList:
            #print( 'entryDict', type(entryDict), len(entryDict), repr(entryDict), '\n' )
            assert entryDict and isinstance( entryDict, dict) and len(entryDict)>=23
            ownerName = entryDict['owner']['full_name']
            if not ownerName: ownerName = entryDict['owner']['username']
            if (repoOwner is None or repoOwner in ownerName) \
            and (repoTitle is None or repoTitle in entryDict['name']):
                resultsList.append( entryDict )
        if len(resultsList) == 1: return resultsList[0]
        return resultsList
    # end of DCSBibles.searchRepos
# end of class DCSBibles



class DCSBible( USFMBible ):
    """
    Class to download and manipulate an online Door43 Bible from the catalog.

    The interface provides a link to a zip file containing all of the USFM books.
    """
    def __init__( self, parameterOne, resourcesObject=None, downloadAllBooks=False ):
        """
        Create the Door43 cataloged Bible object.

        parameterOne can be:
            a catalog dictionary entry (and second parameter must be None)
        or
            an index into the BibleList in the resourcesObject passed as the second parameter
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( f"DCSBible.__init__( {parameterOne}, {resourcesObject}, {downloadAllBooks} )…" )

        if isinstance( parameterOne, dict ):
            assert resourcesObject is None
            resourceDict = parameterOne
        else:
            assert isinstance( parameterOne, int )
            assert resourcesObject # why ??? and isinstance( resourcesObject, Door43CatalogResources )
            resourceDict = resourcesObject.getBibleResourceDict( parameterOne )
        assert resourceDict and isinstance( resourceDict, dict )
        #print( 'resourceDict', resourceDict )
        #print( 'resourceDict', resourceDict.keys() )

        self.baseURL = resourceDict['html_url']
        #print( 'self.baseURL', self.baseURL )
        adjustedRepoName = resourceDict['full_name'].replace( '/', '--' )
        #print( 'adjustedRepoName', adjustedRepoName )
        desiredFolderName = BibleOrgSysGlobals.makeSafeFilename( adjustedRepoName )
        unzippedFolderPath = os.path.join( BibleOrgSysGlobals.DOWNLOADED_RESOURCES_FOLDER,
                                'Door43ContentServiceOnline/', f"{adjustedRepoName}/" )

        if downloadAllBooks:
            # See if files already exist and are current (so don't download again)
            alreadyDownloadedFlag = False
            if os.path.isdir( unzippedFolderPath ):
                #print( f"Issued: {resourceDict['issued']}" )
                updatedDatetime = datetime.strptime( resourceDict['updated_at'], '%Y-%m-%dT%H:%M:%SZ' )
                #print( f"updatedDatetime: {updatedDatetime}" )
                #print( f"folder: {os.stat(unzippedFolderPath).st_mtime}" )
                folderModifiedDatetime = datetime.fromtimestamp(os.stat(unzippedFolderPath).st_mtime)
                #print( f"folderModifiedDatetime: {folderModifiedDatetime}" )
                alreadyDownloadedFlag = folderModifiedDatetime > updatedDatetime
                #print( f"alreadyDownloadedFlag: {alreadyDownloadedFlag}" )

            if alreadyDownloadedFlag:
                if BibleOrgSysGlobals.verbosityLevel > 1:
                    print( "Skipping download because folder '{}' already exists.".format( unzippedFolderPath ) )
            else: # Download the zip file (containing all the USFM files, README.md, LICENSE.md, manifest.yaml, etc.)
                # TODO: Change to .tar.gz instead of zip
                zipURL = self.baseURL + '/archive/master.zip' # '/archive/master.tar.gz'
                if BibleOrgSysGlobals.verbosityLevel > 1:
                    print( "Downloading entire repo from '{}'…".format( zipURL ) )
                try: HTTPResponseObject = urllib.request.urlopen( zipURL )
                except urllib.error.URLError as err:
                    #errorClass, exceptionInstance, traceback = sys.exc_info()
                    #print( '{!r}  {!r}  {!r}'.format( errorClass, exceptionInstance, traceback ) )
                    logging.critical( "DCS URLError '{}' from {}".format( err, zipURL ) )
                    return
                # print( "  HTTPResponseObject", HTTPResponseObject )
                contentType = HTTPResponseObject.info().get( 'content-type' )
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( "    contentType", repr(contentType) )
                if contentType == 'application/octet-stream':
                    try: os.makedirs( unzippedFolderPath )
                    except FileExistsError: pass
                    downloadedData = HTTPResponseObject.read()
                    if BibleOrgSysGlobals.verbosityLevel > 0:
                        print( f"  Downloaded {len(downloadedData):,} bytes from '{zipURL}'" )
                    # Bug in Python up to 3.7 makes this not work for large aligned Bibles (3+ MB)
                    # myTempFile = tempfile.SpooledTemporaryFile()
                    myTempFile = tempfile.TemporaryFile()
                    myTempFile.write( downloadedData )
                    with zipfile.ZipFile( myTempFile ) as myzip:
                        # NOTE: Could be a security risk here
                        myzip.extractall( unzippedFolderPath )
                    myTempFile.close() # Automatically deletes the file
                else:
                    print( "    contentType", repr(contentType) )
                    halt # unknown content type
            self.downloadedAllBooks = True

            # There's probably a folder inside this folder
            folders = os.listdir( unzippedFolderPath )
            #print( 'folders', folders )
            assert len(folders) == 1 # else maybe a previous download failed -- just manually delete the folder
            desiredFolderName = folders[0] + '/'
            #print( 'desiredFolderName', desiredFolderName )
            USFMBible.__init__( self, os.path.join( unzippedFolderPath, desiredFolderName ),
                                                            givenName=resourceDict['name'] )
        else:
            self.downloadedAllBooks = False
            self.attemptedDownload = {}
            try: os.makedirs( unzippedFolderPath )
            except FileExistsError: pass
            USFMBible.__init__( self, unzippedFolderPath, givenName=resourceDict['name'] )
        self.objectNameString = 'DCS USFM Bible object'
    # end of DCSBible.__init__


    def loadBookIfNecessary( self, BBB ):
        """
        Download the book if necessary.

        TODO: This function doesn't check if the USFM book was downloaded by a previous run
                (and is still up-to-date)
        """
        if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
            print( f"DCSBible.loadBookIfNecessary( {BBB} )…" )

        if not self.downloadedAllBooks:
            if BBB not in self.attemptedDownload or not self.attemptedDownload[BBB]:
                self.attemptedDownload[BBB] = True

                # TODO: Change to .tar.gz instead of zip
                nn = BibleOrgSysGlobals.BibleBooksCodes.getReferenceNumber( BBB )
                if nn > 39: nn += 1 # DSC uses #41 for MAT (not 39)
                uBBB = BibleOrgSysGlobals.BibleBooksCodes.getUSFMAbbreviation( BBB ).upper()
                USFMfilename = f'{nn:02}-{uBBB}.usfm'
                zipURL = f'{self.baseURL}/raw/branch/master/{USFMfilename}'
                if BibleOrgSysGlobals.verbosityLevel > 1:
                    print( "Downloading {} file from '{}'…".format( BBB, zipURL ) )
                try: HTTPResponseObject = urllib.request.urlopen( zipURL )
                except urllib.error.HTTPError as err:
                    #errorClass, exceptionInstance, traceback = sys.exc_info()
                    #print( '{!r}  {!r}  {!r}'.format( errorClass, exceptionInstance, traceback ) )
                    logging.critical( "DCS HTTPError '{}' from {}".format( err, zipURL ) )
                    return
                except urllib.error.URLError as err:
                    #errorClass, exceptionInstance, traceback = sys.exc_info()
                    #print( '{!r}  {!r}  {!r}'.format( errorClass, exceptionInstance, traceback ) )
                    logging.critical( "DCS URLError '{}' from {}".format( err, zipURL ) )
                    return
                # print( "  HTTPResponseObject", HTTPResponseObject )
                contentType = HTTPResponseObject.info().get( 'content-type' )
                if BibleOrgSysGlobals.debugFlag and debuggingThisModule:
                    print( "    contentType", repr(contentType) )
                if contentType == 'text/plain; charset=utf-8':
                    downloadedData = HTTPResponseObject.read()
                    if BibleOrgSysGlobals.verbosityLevel > 0:
                        print( f"  Downloaded {len(downloadedData):,} bytes from '{zipURL}'" )
                    with open( os.path.join( self.sourceFolder, USFMfilename ), 'wt' ) as ourUSFMfile:
                        ourUSFMfile.write( downloadedData.decode( 'utf-8' ) )
                else:
                    print( "    contentType", repr(contentType) )
                    halt # unknown content type
                if not self.preloadDone:
                    self.preload()
            else:
                if BibleOrgSysGlobals.verbosityLevel > 2 or debuggingThisModule or BibleOrgSysGlobals.debugFlag:
                    print( f"{BBB} was already downloaded (or attempted)" )
                return

        USFMBible.loadBookIfNecessary( self, BBB )
    # end of DCSBible.loadBookIfNecessary
# end of class DCSBible



def demo():
    """
    Demonstrate how some of the above classes can be used.
    """
    from VerseReferences import SimpleVerseKey

    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion, end='\n\n' )

    if 1: # Test the DCSBibles class
        dcsBibles = DCSBibles()
        if BibleOrgSysGlobals.verbosityLevel > 0:
            print( dcsBibles, end='\n\n' )
        #dcsBibles.load() # takes a minute
        #print( dcsBibles )

        if 1:
            dcsBibles.fetchAllBibles()
            if BibleOrgSysGlobals.verbosityLevel > 0:
                print( "Bible list ({}):".format( len(dcsBibles.BibleList) ) )
            for j, BibleDict in enumerate( dcsBibles.BibleList ):
                ownerName = BibleDict['owner']['full_name']
                if not ownerName: ownerName = BibleDict['owner']['username']
                if BibleOrgSysGlobals.verbosityLevel > 1:
                    print( f"  Entry {j:3} '{BibleDict['name']}'  '{ownerName}'" )


    testRefs = ( ('GEN','1','1'), ('GEN','2','2'), ('JER','33','3'), ('MAL','4','6'),
                 ('MAT','1','1'), ('JHN','3','16'), ('JDE','1','14'), ('REV','22','21'), )

    if 1: # Test the DCSBible class with the ULT
        downloadAllBooks = True
        if BibleOrgSysGlobals.verbosityLevel > 0: print()
        searchResult = dcsBibles.searchRepos( 'unfoldingWord', 'en_ult' )
        #print( 'searchResult', searchResult )
        if searchResult and isinstance( searchResult, dict ):
            dcsBible1 = DCSBible( searchResult, downloadAllBooks=downloadAllBooks )
            try: dcsBible1.preload()
            except FileNotFoundError: assert downloadAllBooks == False
            if BibleOrgSysGlobals.verbosityLevel > 1:
                print( dcsBible1, end='\n\n' )
            for testRef in testRefs:
                verseKey = SimpleVerseKey( *testRef )
                if BibleOrgSysGlobals.verbosityLevel > 0:
                    print( verseKey )
                    print( " ", dcsBible1.getVerseDataList( verseKey ) )
        elif BibleOrgSysGlobals.verbosityLevel > 0:
            print( f"Unexpected search result: {searchResult}" )

    if 1: # Test the DCSBible class with the UST
        downloadAllBooks = False
        if BibleOrgSysGlobals.verbosityLevel > 0: print()
        searchResult = dcsBibles.searchRepos( 'unfoldingWord', 'en_ust' )
        #print( 'searchResult', searchResult )
        if searchResult and isinstance( searchResult, dict ):
            dcsBible1 = DCSBible( searchResult, downloadAllBooks=downloadAllBooks )
            try: dcsBible1.preload()
            except FileNotFoundError: assert downloadAllBooks == False
            if BibleOrgSysGlobals.verbosityLevel > 1:
                print( dcsBible1, end='\n\n' )
            for testRef in testRefs:
                verseKey = SimpleVerseKey( *testRef )
                if BibleOrgSysGlobals.verbosityLevel > 0:
                    print( verseKey )
                    print( " ", dcsBible1.getVerseDataList( verseKey ) )
        elif BibleOrgSysGlobals.verbosityLevel > 0:
            print( f"Unexpected search result: {searchResult}" )
# end of demo

if __name__ == '__main__':
    #from multiprocessing import freeze_support
    #freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of Door43ContentServiceOnline.py
