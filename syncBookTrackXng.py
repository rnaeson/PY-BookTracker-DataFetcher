""" DESCRIPTOIN: This script will... 

Links:
http://wwww.somewhere.on/the/tubs
"""

import inspect  # Get information about a function
import json     # Json Library  
import sys      # Sys Library to exit
import os       # Builtin OS Library
import hashlib  # Compare Quote Objects

from pathlib import Path
THIS = f"{Path(__file__).stem}"
print(f"Executing: {THIS}...\n")

""" ********************  User Configuration Options:  ********************"""
LOGLEVEL = "INFO"
OUTPUT_DIR = "OutPut/BookTracker/"
BOOKTRACK_JSON_V1 = os.path.join(OUTPUT_DIR, 'books_2022.json')
BOOKTRACK_JSON_V2 = os.path.join(OUTPUT_DIR, 'books_2023.json')
BOOKXNG_JSON = "OutPut/BookXng/books.json"
"""************************************ LOGGER ************************************"""
import logging  # Logging Library
class LogEvent:
    def __init__(self, LogLevel="INFO", LoggerId=__name__, FilePath=None):
        ''' Init the class'''
        self.logLevel = LogLevel.upper() if LogLevel.lower() in ['debug', 'info', 'warning', 'error'] else os.environ.get("LOGLEVEL", "INFO")
        self.logName = LoggerId
        self.id = LoggerId
        # TODO: CHECK FILEPATH AND DO FILE STREAM THINGS
        
        # Instantiate Logger
        logFormatter = logging.Formatter(fmt=' %(levelname)-8s :: %(name)s :: %(message)s')
        self.LOGGER = logging.getLogger(self.logName)
        self.LOGGER.setLevel(self.logLevel)
        self.LOGGER.info(f"Logger instantiated and set to loglevel: {self.logLevel}")
        
        # Stream Handler for console
        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setLevel(self.logLevel)
        self.consoleHandler.setFormatter(logFormatter)
        self.LOGGER.addHandler(self.consoleHandler)

    def debug(self, event, show=False):
        self.LOGGER.debug(event)
        if show:
            print(f"CONSOLE DEBUG: --> {event}")
    def info(self, event, show=False):
        self.LOGGER.info(event)
        if show:
            print(f"CONSOLE INFO: --> {event}")
    def warning(self, event, show=False):
        self.LOGGER.warning(event)
        if show:
            print(f"CONSOLE WARNING: --> {event}")
    def error(self, event, show=False):
        self.LOGGER.error(event)
        if show:
            print(f"CONSOLE ERROR: --> {event}")
log = LogEvent(LOGLEVEL, THIS)
# If you always want a message to go to conosle, simply add true to the show attribute for the messge call
# log.debug("Engaging warp drive", True)
# CONSOLE DEBUG: --> Engaging warp drive



#************************************ FUNCTIONS ************************************#
def ValidJson(jsonfile, loadFile = False):
    try:
        if loadFile:
            json.load(jsonfile)
        else:
            json.dumps(jsonfile)
    except ValueError as err:
        return False
    return True



def JsonFileToDict(json_file_location):
    try:
        # Create Response Object
        dataObj = {}
        log.debug(f"Validating file location: {json_file_location}") 
        
        # Check File Locations for Valididity
        if not os.path.isfile(json_file_location):
            log.error(f"Invalid file path: {json_file_location}")
            raise ValueError(f"Invalid file path: {json_file_location}")
        # Open the File
        log.debug(f"Opening file: {json_file_location}")
        # If BigData Flag was passed, then break the file read into lines, and return a list of objects.
        with open(json_file_location, 'r') as f:
            log.debug(f"Loading data from: {json_file_location}", True)
            dataObj = json.load(f)
            if not isinstance(dataObj, dict):
                log.error(f"{json_file_location} LOAD FAILED: Invalid JSON:")
                raise ValueError(f"Invalid JSON object: {json_file_location}")
            f.close()
        return dataObj
    except Exception as e:
        log.error(f"Error reading JSON file: {json_file_location}-->\n{e}")
        return {}



def WriteFile(fileName, listFile, bigdata=False):
    """This function write the list files out as JSON files to the file system."""
    try:
        log.debug("Writing data records to disk...")
        outFile = open(fileName, "w")
        if bigdata:
            for lineObj in listFile:
                outFile.write(f"{json.dumps(lineObj)}\n")
        else:
            outFile.write(json.dumps(listFile, indent=4))
        outFile.close()
    except Exception as e:
        log.error(f"An error has been encountered attempting to write the output file to the specified location: {e}")
        raise(e)

#************************************ MAIN ************************************#
if __name__ == "__main__":
    log.debug("Engaging warp drive... or just the file check... either or")
    
    try:
        '''**************************** CHECK FILEPATHS ****************************'''
        # Check all Input files and Output file location
        if not os.path.isdir(OUTPUT_DIR):
            fileError = OUTPUT_DIR
        elif not os.path.isfile(BOOKTRACK_JSON_V1):
            fileError = BOOKTRACK_JSON_V1
        elif not os.path.isfile(BOOKTRACK_JSON_V2):
            fileError = BOOKTRACK_JSON_V2
        elif not os.path.isfile(BOOKXNG_JSON):
            fileError = BOOKXNG_JSON
        else:
            fileError = None
        # If an error occurred opening any of the file paths, then exit out
        if fileError is not None:
            log.error(f"{fileError} not found or does not exist. Please check the path and try again...")
            sys.exit(1)
        else:
            log.debug(f"Input/Output Paths Check succeeded!")


        '''**************************** Do the Things ****************************'''
        # Open the JSON files that will be used for the lookup / aggragation merge

        # Open BookTrack and Bookxng Output json files
        # These are the outputs of parseBookTracker, and parseBookXng files in this project
        bookTrackJsonV1 = JsonFileToDict(BOOKTRACK_JSON_V1)
        bookTrackJsonV2 = JsonFileToDict(BOOKTRACK_JSON_V2)
        bookXngJson = JsonFileToDict(BOOKXNG_JSON)

        # Start with merging the 2 book objects
        legacyBooks = bookTrackJsonV1.get('books')
        currentBooks = bookTrackJsonV2.get('books')
        bookXngBooks = bookXngJson.get('books')

        log.info(f"{len(legacyBooks)} Legacy Books found!")
        log.info(f"{len(currentBooks)} Current Books found!")

        updatedQuotes = 0
        for book in currentBooks:
            title = book.get('title')
            quoteCount = book.get('quoteCount')
            quotesList = book.get('quotes')

            #************************************ MERGE QUOTES ************************************#
            # Cycle through the legacy book objects and compare quote Counts
            for legBook in legacyBooks:
                if legBook.get('title') == title:
                    legQuoteCount = legBook.get('quoteCount')
                    if legQuoteCount > 0 and legQuoteCount != quoteCount:
                        log.info(f"{title} has {quoteCount} quotes, legacy records contains {legQuoteCount}... updating current record")
                        if quoteCount == legQuoteCount:
                            pass
                        elif quoteCount > legQuoteCount:
                            log.warning(f"Inconsistancy Found... {title} has more quotes in current record set ({quoteCount}) then the legacy record set ({legQuoteCount})")
                            pass
                        elif legQuoteCount > quoteCount:
                            if quoteCount != 0:
                                log.warning(f"\nQUOTES may be lost, the current title ({title}) has quotes registred ({quoteCount}) but the legacy record has more ({legQuoteCount})")
                                log.warning(f"\n\n{json.dumps(book.get('quotes'), indent=4)}\n\n{json.dumps(legBook.get('quotes'), indent=4)}\n\n")
                                proceed = input("Should the record be updated? (Yes/No)\n")
                                if proceed.lower() == "yes":
                                    book['quotes'] = legBook.get('quotes')
                                    book['quoteCount'] = len(legBook.get('quotes'))
                                    log.info(f"Updated: New Quote Count is now: {len(book.get('quotes'))}")
                                    updatedQuotes += (legQuoteCount - quoteCount)
                                else:
                                    log.info(f"Update Skipped: Quote Count is still: {len(book.get('quotes'))}")
                            elif quoteCount == 0:
                                log.info(f"Current Quote Count for {title} --> {len(quotesList)}")
                                book['quotes'] = legBook.get('quotes')
                                book['quoteCount'] = len(legBook.get('quotes'))
                                log.info(f"New Quote Count is now: {len(book.get('quotes'))}")
                                updatedQuotes += len(book.get('quotes'))
        log.info(f"{updatedQuotes} quotes have been added to the new book json object")



        #************************************ COORELATE TO BOOKXNG ************************************#
        matchedRecords = 0
        matchConfirmedRecords = 0
        for bookItem in bookXngBooks:
            bookTitle = bookItem.get('title')
            isbn = bookItem.get('isbn')

            # For each of the books in the monster list, iterate through each item in the BookTrack list and try and find a match
            for book in currentBooks:
                if bookTitle == book.get('title'):
                    log.info(f"TITLE MATCH FOUND: {bookTitle} --> {book.get('title')}")
                    book['bookId'] = isbn
                    matchedRecords += 1
                    if isbn == book.get('isbn10'):
                        log.debug(f"ISNB MATCH FOUND: {bookTitle} --> {book.get('title')}", True)
                        matchConfirmedRecords += 1
        log.info(f"{matchedRecords}/{len(currentBooks)} books were title matched between the two databases. {matchConfirmedRecords}/{matchedRecords} of those were also ISBN matched")

        # Finally, make things consistant, search for any keys in our BookTracker books object that does not have a bookId key, and add one with a default value of 0
        defaultIdsAdded = 0
        for book in currentBooks:
            if not book.get('bookId'):
                book['bookId'] = 0
                defaultIdsAdded += 1
        log.info(f"{defaultIdsAdded} book records where updated to include the bookId: 0 attribute")

        # Some of the title matched items may have been duplicates so lets do a final math check,
        # and while we are at it create one final list that contains only the items that we could match against the BookXng Dataset
        matchedBookCollection = []
        bookItemFound = 0
        for book in currentBooks:
            if book.get('bookId') != 0:
                bookItemFound += 1
                matchedBookCollection.append(book)
        log.info(f"Math check found and confirmed {bookItemFound}/{len(currentBooks)-defaultIdsAdded} items that were previously matched")


        #************************************ OUTPUT Aggregated Objects ************************************#
        # First lets output back to JSON
        aggregatedJson = {'books': currentBooks}
        WriteFile(os.path.join(OUTPUT_DIR, 'books_aggregated.json'), aggregatedJson, bigdata=False)
        WriteFile(os.path.join(OUTPUT_DIR, 'books_aggregated_bigdata.json'), currentBooks, bigdata=True)
        
        # Match Only Outputs
        matchedBooksJson = {'books': matchedBookCollection}
        WriteFile(os.path.join(OUTPUT_DIR, 'books_matched.json'), matchedBooksJson, bigdata=False)
        WriteFile(os.path.join(OUTPUT_DIR, 'books_matched_bigdata.json'), matchedBookCollection, bigdata=True)

        # Create Quotes Object, and Output in both standard JSON as well as BigData formats
        quoteCollection = []
        matchedQuoteCollection = []
        for book in currentBooks:
            bookId = book.get('bookId') if book.get('bookId') != 0 else book.get('isbn13').replace('-', '')
            title = book.get('title')
            isbn10 = book.get('isbn10')
            isbn13 = book.get('isbn13')
            bookQuotes = book.get('quotes')
            for quote in bookQuotes:
                quoteCollection.append({"id": bookId, "title": title, "isbn10": isbn10, "isbn13": isbn13, "quote": quote})
                if book.get('bookId') != 0:
                    matchedQuoteCollection.append({"id": bookId, "title": title, "isbn10": isbn10, "isbn13": isbn13, "quote": quote})
        quotesJSON = {"quotes": quoteCollection}
        matchedQuotesJson = {'quotes': matchedQuoteCollection}
        WriteFile(os.path.join(OUTPUT_DIR, 'quotes_aggregated.json'), quotesJSON, bigdata=False)
        WriteFile(os.path.join(OUTPUT_DIR, 'quotes_aggregated_bigdata.json'), quoteCollection, bigdata=True)
        # Matched Only
        WriteFile(os.path.join(OUTPUT_DIR, 'quotes_matched.json'), matchedQuotesJson, bigdata=False)
        WriteFile(os.path.join(OUTPUT_DIR, 'quotes_matched_bigdata.json'), matchedQuoteCollection, bigdata=True)
        
        # Create the Aggregated Book outputs with quotes removed.
        for book in currentBooks:
            book.pop('quotes')
            book.pop('quoteCount')
        WriteFile(os.path.join(OUTPUT_DIR, 'books_aggregated_noQuotes.json'), currentBooks, bigdata=True)
        log.info("ETL Script Completed Successfully!\n\n")
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to execute this ETL script. Please check logs for additioanl information.")
