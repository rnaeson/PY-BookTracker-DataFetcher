""" This script will extract the data from the Book Genome Project into a standized JSON output. Once the JSON has been extracted,
the data can be used in order to construct other data formats such as an AWS personalize ItemID csv file that can be used to feed
the AWS Personalize recommendations service. """

import inspect  # Get information about a function
import json     # Json Library  
import base64   # Encode image or other binary data to a storable format
import csv      # Output CSV Formatted Files
import sys      # Sys Library to exit
import os       # Builtin OS Library
import re       # Add Regex support to clean HTML tags
from pathlib import Path
THIS = f"{Path(__file__).stem}"
print(f"Executing: {THIS}...\n")

""" ********************  User Configuration Options:  ********************"""
LOGLEVEL = "INFO"
BOOKGENOME_INPUT_DIR = "Datasets/BookGenome/"
BOOKGENOME_OUTPUT_DIR = "OutPut/BookGenome/"
BOOKDATA = os.path.join(BOOKGENOME_INPUT_DIR, 'metadata.json')
RATINGDATA = os.path.join(BOOKGENOME_INPUT_DIR, 'ratings.json')
TAGDATA = os.path.join(BOOKGENOME_INPUT_DIR, 'tags.json')
BOOKS_JSON = os.path.join(BOOKGENOME_OUTPUT_DIR, 'books.json')
BOOKS_BIGDATA = os.path.join(BOOKGENOME_OUTPUT_DIR, 'books_bigdata.json')
"""************************************************************************"""

#************************************ LOGGER ************************************#
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



#************************************ Functions ************************************#
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
        log.error(f"An error has been encountered attempting to write the output file to the specified location: {fileName}:\n{e}")
        raise(e)


def ValidJson(jsonfile, loadFile = False):
    try:
        if loadFile:
            json.load(jsonfile)
        else:
            json.dumps(jsonfile)
    except ValueError as err:
        return False
    return True


def JsonFileToDict(json_file_location, bigdata=False):
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
        if bigdata:
            # Create a List to store each line result
            lineData = []
            lineErrorCount = 0
            # Open the File
            with open(json_file_location, 'r') as f:
                log.debug(f"Loading big data formatted data from: {json_file_location}")
                # For each line in file, check JSON, and if valid add to lineData list
                for line in f:
                    # log.debug(json.loads(line))
                    if ValidJson(json.loads(line)):
                        lineData.append(json.loads(line))
                    else:
                        log.warning(f"Encountered non-valid json in file: {line}")
                        lineErrorCount += 1
                # Check to make sure that the return object is the proper type.
                dataObj = lineData
                f.close()
        else:
            with open(json_file_location, 'r') as f:
                log.debug(f"Loading data from: {json_file_location}")
                dataObj = json.load(f)
                if not isinstance(dataObj, dict):
                    log.error(f"{json_file_location} LOAD FAILED: Invalid JSON:")
                    raise ValueError(f"Invalid JSON object: {json_file_location}")
                f.close()
        return dataObj
    except Exception as e:
        log.error(f"Error reading JSON file: {e}")
        return {}


if __name__ == "__main__":
    log.debug("Engaging warp drive... or just the file check... either or")

    try:
        # Check all Input files and Output file location
        if not os.path.isfile(BOOKDATA):
            fileError = BOOKDATA
        elif not os.path.isfile(RATINGDATA):
            fileError = RATINGDATA
        elif not os.path.isfile(TAGDATA):
            fileError = TAGDATA
        elif not os.path.isdir(BOOKGENOME_OUTPUT_DIR):
            fileError = BOOKGENOME_OUTPUT_DIR
        else:
            fileError = None

        if fileError is not None:
            
            log.error(f"{fileError} not found or does not exist. Please check the path and try again...")
            sys.exit(1)
        else:
            log.debug(f"Input/Output Paths Check succeeded!")

        # Open the Book Json File
        genomeBooks = JsonFileToDict(BOOKDATA, bigdata=True)
        log.debug(json.dumps(genomeBooks, indent=4))
        booksJson = {'books': genomeBooks}
        log.debug(f"{len(genomeBooks)} book records have been loaded; generating output files", True)
        WriteFile(BOOKS_JSON, booksJson)
        log.debug(f"{len(booksJson.get('books'))} book records have been output to {BOOKS_JSON}", True)
        WriteFile(BOOKS_BIGDATA, genomeBooks, bigdata=True)
        log.debug(f"{len(genomeBooks)} book records have been output to {BOOKS_BIGDATA}", True)
        """ {
                "item_id": 16827462,
                "url": "https://www.goodreads.com/book/show/11870085-the-fault-in-our-stars",
                "title": "The Fault in Our Stars",
                "authors": "John Green",
                "lang": "eng",
                "img": "https://images.gr-assets.com/books/1360206420m/11870085.jpg",
                "year": 2012,
                "description": "There is an alternate cover edition \u0001.\n\"I fell in love the way you fall asleep: slowly, then all at once.\"\nDespite the tumor-shrinking medical miracle that has bought her a few years, Hazel has never been anything but terminal, her final chapter inscribed upon diagnosis. But when a gorgeous plot twist named Augustus Waters suddenly appears at Cancer Kid Support Group, Hazel's story is about to be completely rewritten.\nInsightful, bold, irreverent, and raw, The Fault in Our Stars is award-winning author John Green's most ambitious and heartbreaking work yet, brilliantly exploring the funny, thrilling, and tragic business of being alive and in love."
            }"""
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to execute this ETL script. Please check logs for additioanl information.")