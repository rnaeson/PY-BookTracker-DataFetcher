""" This script will extract the data from the Book Crossing Project into a standized JSON output. Once the JSON has been extracted,
the data can be used in order to construct other data formats such as an AWS personalize ItemID csv file that can be used to feed
the AWS Personalize recommendations service. 

http://www2.informatik.uni-freiburg.de/~cziegler/BX/
"""

import inspect  # Get information about a function
import json     # Json Library  
import base64   # Encode image or other binary data to a storable format
import random   # Everyone needs a little randomness in their lives...
import time     # Used to generate date date
import csv      # Output CSV Formatted Files
import sys      # Sys Library to exit
import os       # Builtin OS Library
import re       # Add Regex support to clean HTML tags
from pathlib import Path
THIS = f"{Path(__file__).stem}"
print(f"Executing: {THIS}...\n")

""" ********************  User Configuration Options:  ********************"""
LOGLEVEL = "INFO"
BOOKXNG_INPUT_DIR = "Datasets/BookXng/"
BOOKXNG_OUTPUT_DIR = "Output/BookXng/"
# Input
BOOKDATA = os.path.join(BOOKXNG_INPUT_DIR, 'BX-Books.csv')
RATINGDATA = os.path.join(BOOKXNG_INPUT_DIR, 'BX-Book-Ratings.csv')
USERDATA = os.path.join(BOOKXNG_INPUT_DIR, 'BX-Users.csv')
# Output
BOOKS_JSON = os.path.join(BOOKXNG_OUTPUT_DIR, 'books.json')
BOOKS_JSON_BYISBN = os.path.join(BOOKXNG_OUTPUT_DIR, 'books_byIsbn.json')
BOOKS_BIGDATA = os.path.join(BOOKXNG_OUTPUT_DIR, 'books_bigdata.json')

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


def CsVFileToDict(csv_file_location, delimiter=","):
    try:
        # Check File location
        if not os.path.isfile(csv_file_location):
            raise ValueError(f"Invalid file path: {csv_file_location}")
        # Open the CSV file, load into Dictionary, and return the dictionary.
        with open(csv_file_location, 'r', encoding='mac_roman', newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            data = [row for row in reader]
            if ValidJson(data):
                return data
            else:
                log.warning(f"Parse failure: non-valid JSON detected\n{data}")
                return {}
    except Exception as e:
        print(f"Error reading CSV file: {e}")
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
        log.error(f"An error has been encountered attempting to write the output file to the specified location: {fileName}:\n{e}")
        raise(e)


def PersonalizeUsers(userObj):
    """ Export an AWS Personalize Users CSV that can be used for item recommendations """
    log.info("Creating AWS Personalize Users CSV")
    try:   
        OutputFile = f"{os.path.join(BOOKXNG_OUTPUT_DIR, 'users.csv')}"

        # Get the field names
        fieldNames = []
        for k in userObj[0].keys():
            fieldNames.append(k)

        # Define CSV Header Row
        csvHeader = ['USER_ID', 'LOCATION', 'AGE']
        csvData = []

        for user in userObj:
            csvData.append({
                csvHeader[0]: user.get(fieldNames[0]),
                csvHeader[1]: user.get(fieldNames[1]),
                csvHeader[2]: user.get(fieldNames[2])
            })

        # Open the File and start dumping the datas
        with open(OutputFile, "w", newline='') as userFile:
            userWriter = csv.DictWriter(userFile, fieldnames=csvHeader)
            userWriter.writeheader()
            for user in csvData:
                userWriter.writerow(user)
            userWriter.writerow({'USER_ID': '420000', 'LOCATION': 'amsterdam, netherlands', 'AGE': 44})
            userFile.close()
        log.debug(f"Csv Users file has been written to: {OutputFile}")
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to write the personalize user file.")


def PersonalizeRatings(ratingsObj):
    """ Export an AWS Personalize Interactions CSV that can be used for item recommendations """
    log.info("Creating AWS Personalize Ratings CSV")
    try:   
        OutputFile = f"{os.path.join(BOOKXNG_OUTPUT_DIR, 'interactions.csv')}"

        # Get the field names
        fieldNames = []
        for k in ratingsObj[0].keys():
            fieldNames.append(k)

        # Define CSV Header Row
        csvHeader = ['USER_ID', 'ITEM_ID', 'EVENT_TYPE', 'EVENT_VALUE', 'TIMESTAMP']
        csvData = []

        # For each object, structure the object accordingly and add a random timestamp.
        for rating in ratingsObj:
            csvData.append({
                csvHeader[0]: rating.get(fieldNames[0]),
                csvHeader[1]: rating.get(fieldNames[1]),
                csvHeader[2]: int(FetchRandomDate()),
                csvHeader[3]: "watch"
            })
        
#         for rating in ratingsObj:
#             csvData.append({
#                 csvHeader[0]: rating.get(fieldNames[0]),
#                 csvHeader[1]: rating.get(fieldNames[1]),
#                 csvHeader[2]: "Watch",
#                 csvHeader[3]: rating.get(fieldNames[2]),
#                 csvHeader[4]: FetchRandomDate()
#             })

        # Open the File and start dumping the datas
        with open(OutputFile, "w", newline='') as ratingsFile:
            interactionWriter = csv.DictWriter(ratingsFile, fieldnames=csvHeader)
            interactionWriter.writeheader()
            for rating in csvData:
                interactionWriter.writerow(rating)
            ratingsFile.close()
        log.debug(f"Csv Ratings file has been written to: {OutputFile}")
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to write the personalize interactions file.")


def PersonalizeItems(itemsObj):
    """ Export an AWS Personalize Items CSV that can be used for item recommendations """
    log.info("Creating AWS Personalize Items CSV")
    try:   
        OutputFile = f"{os.path.join(BOOKXNG_OUTPUT_DIR, 'items.csv')}"

        # Get the field names
        fieldNames = []
        for k in itemsObj[0].keys():
            fieldNames.append(k)

        # Define CSV Header Row
        csvHeader = ['ITEM_ID', 'GENRES', 'GENRE_L2', 'GENRE_L3', 'PRODUCT_DESCRIPTION', 'CONTENT_OWNER', 'CREATION_TIMESTAMP']
        csvData = []

        # For each object, structure the object accordingly and add a random timestamp.
        for item in itemsObj:
            csvData.append({
                csvHeader[0]: item.get(fieldNames[0]),
                csvHeader[1]: item.get(fieldNames[2]),
                csvHeader[2]: "categories",
                csvHeader[3]: "tags",
                csvHeader[4]: "description",
                csvHeader[5]: item.get(fieldNames[4]),
                csvHeader[6]: FetchRandomDate()
            })

        # Open the File and start dumping the datas
        with open(OutputFile, "w", newline='') as itemsFile:
            itemWriter = csv.DictWriter(itemsFile, fieldnames=csvHeader)
            itemWriter.writeheader()
            for item in csvData:
                itemWriter.writerow(item)
            itemsFile.close()
        log.debug(f"Csv Items file has been written to: {OutputFile}")
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to write the personalize items file.")


def FetchRandomDate():
    """ Fucnction to return a random date from the last decade """
    # TODO: Make the start time, end time & timeformat settable
    timeFormat = "%m/%d/%Y %I:%M %p"
    
    startTime = time.mktime(time.strptime("1/1/2000 12:00 AM", timeFormat))
    endTime = time.mktime(time.strptime("4/1/2023 12:00 AM", timeFormat))

    dealersChoice = startTime + random.random() * (endTime - startTime)
    log.debug(f"Generated: {dealersChoice} -> {time.strftime(timeFormat, time.localtime(dealersChoice))}")
    return dealersChoice


#************************************ MAIN ************************************#
if __name__ == "__main__":
    log.debug("Engaging warp drive... or just the file check... either or")
    
    try:
        '''**************************** CHECK FILEPATHS ****************************'''
        # Check all Input files and Output file location
        if not os.path.isfile(BOOKDATA):
            fileError = BOOKDATA
        elif not os.path.isfile(RATINGDATA):
            fileError = RATINGDATA
        elif not os.path.isfile(USERDATA):
            fileError = USERDATA
        elif not os.path.isdir(BOOKXNG_OUTPUT_DIR):
            fileError = BOOKXNG_OUTPUT_DIR
        else:
            fileError = None
        # If an error occurred opening any of the file paths, then exit out
        if fileError is not None:
            log.error(f"{fileError} not found or does not exist. Please check the path and try again...")
            sys.exit(1)
        else:
            log.debug(f"Input/Output Paths Check succeeded!")
        
        

        '''**************************** FETCH DATASETS ****************************'''
        #********************* BOOK COLLECTION and PERSONALIZE ITEMS  *********************#
        # Open the csv files, the return is the dictionary versions.
        # bookCollection will return a  list of dicts this will be used for dataset output
        log.debug("\nFetching books CSV and converting to JSON...\n")
        bookCollection = CsVFileToDict(BOOKDATA, delimiter=";")
        print("\n")
        log.debug(f"{len(bookCollection)} book records loaded: --> \n{json.dumps(bookCollection[0], indent=4)}", True)
        PersonalizeItems(bookCollection)
        log.debug(f"{len(bookCollection)} book records have been output to {os.path.join(BOOKXNG_OUTPUT_DIR, 'items.csv')}", True)
        """ {
                "ISBN": "0195153448",
                "Book-Title": "Classical Mythology",
                "Book-Author": "Mark P. O. Morford",
                "Year-Of-Publication": "2002",
                "Publisher": "Oxford University Press",
                "Image-URL-S": "http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg",
                "Image-URL-M": "http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg",
                "Image-URL-L": "http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg"
            }"""
        

        #********************* PERSONALIZE RATINGS  *********************#
        # ratingsCollection will return a list of rating dict objects that will be combined with the book items.
        log.debug("\nFetching book ratings CSV and converting to JSON...\n")
        ratingsCollection = CsVFileToDict(RATINGDATA, delimiter=";")
        print("\n")
        log.debug(f"{len(ratingsCollection)} book rating records loaded: --> \n{json.dumps(ratingsCollection[0], indent=4)}", True)
        PersonalizeRatings(ratingsCollection)
        log.debug(f"{len(ratingsCollection)} book rating records have been output to {os.path.join(BOOKXNG_OUTPUT_DIR, 'ratings.csv')}", True)
        print("\n")
        """ {
                "User-ID": "276725",
                "ISBN": "034545104X",
                "Book-Rating": "0"
            }"""
        
        
        #********************* PERSONALIZE USERS  *********************#
        # usersCollection will return a list of user dict objects that will be combined with the book items.
        log.debug("\nFetching book readers CSV and converting to JSON...\n")
        usersCollection = CsVFileToDict(USERDATA, delimiter=";")
        print("\n")
        log.debug(f"{len(usersCollection)} book user records loaded: --> \n{json.dumps(usersCollection[0], indent=4)}", True)
        PersonalizeUsers(usersCollection)
        log.debug(f"{len(usersCollection)} book user records have been output to {os.path.join(BOOKXNG_OUTPUT_DIR, 'users.csv')}", True)
        print("\n")
        """ {
                "User-ID": "1",f
                "Location": "nyc, new york, usa",
                "Age": "NULL"
            }"""
        


        '''**************************** Compress Lists into Dictionary ****************************'''
        transformedBookCollection = []
        for book in bookCollection:
            bookDict = {}
            bookDict.update(
                isbn=book.get('ISBN'),
                title=book.get('Book-Title'),
                author=book.get('Book-Author'),
                published=book.get('Year-Of-Publication'),
                publisher=book.get('Publisher'),
                imageLinks={
                        "small": book.get('Image-URL-S'),
                        "medium": book.get('Image-URL-M'),
                        "large": book.get('Image-URL-L')
                }
            )
            transformedBookCollection.append(bookDict)
        
        #********************* Normalized {books: [transformedBookCollection]} JSON  *********************#
        # Use the constructed object above to output a single 'books' key with the list of objects as the value
        log.debug("\nConstructing and writing normalized JSON: { books: [transformedBookCollection] }...\n")
        print("\n")
        bookJson = {"books": transformedBookCollection}
        log.debug(f"{len(bookJson.get('books'))} book user records loaded: --> \n{json.dumps(bookJson.get('books')[0], indent=4)}", True)
        WriteFile(BOOKS_JSON, bookJson, bigdata=False)
        log.debug(f"{len(transformedBookCollection)} book records have been output to {BOOKS_JSON}", True)
        print("\n")


        #********************* By ISBN {1234567890: [bookCollection]} JSON  *********************#
        # Create a JSON object that is constructed with ISBN keys, to full object list values
        log.debug("\nConstructing and writing ISBN keyed JSON: { 1234567890: [bookCollection] }...\n")
        print("\n")
        bookByIsbnJson = {}
        for book in transformedBookCollection:
            bookByIsbnJson[book.get('isbn')] = book
        WriteFile(BOOKS_JSON_BYISBN, bookByIsbnJson, bigdata=False)
        log.debug(f"{len(transformedBookCollection)} book records have been output to {BOOKS_JSON_BYISBN}", True)
        print("\n")


        #********************* BigData format {isbn: 1234567890, title: Game of Thrones, etc..}  *********************#
        # Create list to outptut the big data format
        log.debug("\nConstructing and writing bigdata format of each book as its own JSON: { isbn: 1234567890, title: Game of Thrones, etc.. }\n")
        print("\n")
        WriteFile(BOOKS_BIGDATA, transformedBookCollection, bigdata=True)
        log.debug(f"{len(transformedBookCollection)} book records have been output to {BOOKS_BIGDATA}", True)
        print("\n")

        log.info("ETL Script Completed Successfully!\n\n")
    except KeyboardInterrupt:
        log.error("An Unexpected errror occurred while attempting to execute this ETL script. Please check logs for additioanl information.")
