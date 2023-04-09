""" BookTrack App Field List:
        Z_PK - Primary Key (Id)
        Z_ENT - (All set to 1)
        Z_OPT - (Reference to another ?? table)
        ZPAGECOUNT - Page Count (In-Table)
        ZREAD - (All set to 0)
        ZSERIES - Book Series (In ZCDSERIES table [Z_PK, Z_ENT, Z_OPT, ZNAME])
        ZSHELF - Shelf (All Null)
        ZAVERAGERATING - Book Rating (In Table)
        ZCREATEDAT - Record Creation Date (In Table, Unknown Format 675442888.62018)
        ZENDREADINGDATE - Read Date (In Table, Unknown Format 675442888.62018)
        ZLOANEDDATE - Loaned Date (In Table, All Null)
        ZPURCHASEDATE - Book Purchase Date (In Table, Unknown Format 665510640)
        ZRELEASEDATE - Book Release Date (In Table, Unknown Format 665510640)
        ZSTARTREADINGDATE - Reading Date (In Table, Unknown Format, both above mixed)
        ZUPDATEAT - Record Update Date (In Table, Unknown Format 675442888.62018)
        ZAUTHORSLASTNAMENAMESEARCHABLE - Authors name Last name first (In Table)
        ZAUTHORSNAMELASTNAMESEARCHABLE - Authors name First name first (firstname lastname) (In Table)
        ZBOOKDESCRPTION - Book Description (In Table)
        ZBOOKSHELFSEARCHABLE - No Shelves, zzzzz all fields 
        ZCATEGORIESSEACHABLE - All colomns null 
        ZCATEGORYLISTSEARCHABLE - List of applied book categories in comma separated format (In Table)
        ZGOODREADSID - All Null
        ZGOODREADSURL - All Null
        ZGOOGLEBOOKURL - URL Format
        ZGOOGLEID - Google ID
        ZID - Repeat of Google ID
        ZISBN10 - ISBN 10 digit format (In Table)
        ZISBN13 - ISBN 13 digit format (In Table)
        ZLANGUAGE - All set to en
        ZLOANEDLISTSEARCHABLE - All colomns set to zzzzz
        ZLOCATIONSEARCHABLE - All colomns set to zzzzz
        ZPERSONALCOMMENT - In Table comments
        ZPUBLISHER - Book Publisher (In Table)
        ZREADSTATUS - Value of 'read' or 'reading'
        ZREMOTEIMAGEURL - null or URL of image
        ZSERIESSEARCHABLE - Book Series (In Table)
        ZSHELFSHEARCHABLE - All colomns set to zzzzz
        ZSTATE - All set to Bookshelf
        ZTAGLISTSEARCHABLE - Book Tags, comma separated lists
        ZTHUMBNAILREMOTEIMAGEURL - URL or null
        ZTITLE - Book Title (In-Table)
        ZTYPE - Physical Book or Digital Book
        ZAUTHORLIST - All set Null
        ZCATEGORIES - Book Catagories (In-Table) All Set Null
        ZQUOTELIST - Book Recorded Quotes (In-Table) BLOB of Quotes
        ZLOCALIMAGE - BLOB of Image.
    """
import logging  # Logging Library
import sqlite3  # Relational Database Library
import plistlib # Parse Apple PList File Formats
import json     # Json Library  
import base64   # Encode image or other binary data to a storable format
import random   # Generate Random integers
import time     # Validate unix epoch time strings
import copy     # Deep copy the book dictionary
import csv      # Output CSV Formatted Files
import sys      # Sys Library to exit
import os       # Builtin OS Library
import re       # Add Regex support to clean HTML tags
from io import BytesIO  # Binary Input/Output Library, used to decode blob binary data into a variable.
from urllib.request import urlopen  # Download images or other content
from PIL import Image # Perform Image validation on any included images
from pathlib import Path
THIS = f"{Path(__file__).stem}"
print(f"Executing: {THIS}...\n")

""" ********************  User Configuration Options:  ********************"""
loadLegacyDB = False # True uses library_v1.sqlite, False uses library_v2.sqlite (2023-Current)
LOGLEVEL = "INFO"
# BOOKTRACK_DB = "/Users/rnaeson/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite"
BOOKTRACK_DB = "Datasets/BookTracker/library_v1.sqlite" if loadLegacyDB else "Datasets/BookTracker/library_v2.sqlite"
BOOKTRACK_DB_QUERY = """SELECT
Z_PK,
ZTITLE,
ZAUTHORSNAMELASTNAMESEARCHABLE,
ZBookDescription,
ZSERIESSEARCHABLE,
ZPAGECOUNT,
ZPUBLISHER,
ZISBN10,
ZISBN13,
ZTYPE,
ZAVERAGERATING,
ZQUOTELIST,
ZCATEGORYLISTSEARCHABLE,
ZTAGLISTSEARCHABLE,
ZPERSONALCOMMENT,
ZREMOTEIMAGEURL,
ZLOCALIMAGE,
ZCREATEDAT,
ZUPDATEDAT,
ZRELEASEDATE,
ZPURCHASEDATE,
ZSTARTREADINGDATE,
ZENDREADINGDATE,
ZGOOGLEBOOKURL,
ZGOOGLEID
FROM ZCDBOOK;
"""
BOOKTRACK_INPUT_DIR = "Datasets/BookTracker/"
BOOKTRACK_OUTPUT_DIR = "Output/BookTracker/"
# Output
BOOKS_JSON = os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_2022.json') if loadLegacyDB else os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_2023.json')
BOOKS_BIGDATA = os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_bigdata_2022.json') if loadLegacyDB else os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_bigdata_2023.json')
BOOKS_BIGDATA_NO_QUOTES = os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_bigdata_noQuotes_2022.json') if loadLegacyDB else os.path.join(BOOKTRACK_OUTPUT_DIR, 'books_bigdata_noQuotes_2023.json')
QUOTES_JSON = os.path.join(BOOKTRACK_OUTPUT_DIR, 'quotes_2022.json') if loadLegacyDB else os.path.join(BOOKTRACK_OUTPUT_DIR, 'quotes_2023.json')
QUOTES_BIGDATA = os.path.join(BOOKTRACK_OUTPUT_DIR, 'quotes_bigdata_2022.json') if loadLegacyDB else os.path.join(BOOKTRACK_OUTPUT_DIR, 'quotes_bigdata_2023.json')

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
def GetDbRecords():
    """ Function to run the query against the BookTrack sqlite database. 
    The function gathers all of the books, quotes, and metadata stored in the app. """

    log.debug("Gathering BootTrack Data...")
    try:
        db_conn = sqlite3.connect(BOOKTRACK_DB)
        sql = db_conn.cursor()
        log.debug("Connected to Booktrack DB, running query")
        sql.execute(BOOKTRACK_DB_QUERY)
        ItemRecordList = sql.fetchall()
        log.debug("Query execution completed.")
        
        if ItemRecordList is None:
            log.warning("Database Query returned 0 results")
        else:
            log.debug(f"Database Query returned {len(ItemRecordList)} results")
        log.debug("Closing connection to Booktrack DB")
        sql.close()
        db_conn.close()
        log.debug("Connection to BookTrack DB closed, returning resultset.")
        return ItemRecordList
    except sqlite3.Error as sql_error:
        sql_response = sql_error.__dict__
        log.error("There was an error retrieving quote records from the BookTrack sqlite database file:\n")
        log.error(f"{sql_response}")
    return sql_response


def CapitalizeString(strObj):
    """ This function will simply take a string consisting of a string, divide that string by spaces,
    and then capitalize the first letter of each word. """

    log.debug(f"Formatting String: {strObj}")
    try:
        if not strObj or strObj == "" or strObj == " " or strObj is None:
            log.debug(f"String Value: {strObj}, not valid string, returning null")
            return None
        
        strObj = strObj.lower()
        strWordList = []

        # Authors name is stored as "first last" all lower case
        splitString = strObj.split(" ")
        log.debug(f"String Split: {splitString}")
        
        # Capitalize each first initial
        for word in splitString:
            strWordList.append(word.capitalize())
            log.debug(f"Capitalized word list: {strWordList}")
            strResponse = ' '.join(strWordList)
            log.debug(f"Returning properly formatted string: {strResponse}")
        return str(strResponse)
    except Exception as e:
        log.error(f"An unexpected error occured attempting to format the input string {e}")


def CleanHTMLTags(bookDescription):
    """ This function will simply take a string consisting of the books description, and will
    clean any HTML tags found within the description object. """

    log.debug(f"Formatting book description: {bookDescription}")
    try:
        # cleanTags = re.compile('<.*?>')
        cleanTags = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        descriptionResponse = re.sub(cleanTags, '', bookDescription)
        descriptionResponse = descriptionResponse.encode("ascii", "ignore")
        descriptionResponse = descriptionResponse.decode()
        log.debug(f"Returning cleaned description object: {descriptionResponse}")
        return str(descriptionResponse)
    except Exception as e:
        log.error(f"An unexpected error occured attempting to clean the books description {e}")


def FetchQuotesList(quoteObj):
    """ This function will take a bytes plist input and convert the data to a properly formatted json string"""
    log.debug("Fetch all quotes from the book record...")
    
    try:
        log.debug(f"Input object is of type {type(quoteObj)}")

        quoteListResponse = []
        fetchedQuoteList = []
        
        # Setup Temp file to write blob to
        log.debug("Converting input object to IO Bytes object")
        quoteBytesObj = BytesIO()
        quoteBytesObj.write(quoteObj)
        log.debug("Rewinding cursor to position 0 of written IO Bytes object")
        quoteBytesObj.seek(0)
  
        # Parse the Apple Plist Object format and extract the quotes
        log.debug("Loading IO Bytes apple plist file format and parsing...")
        quoteList = plistlib.loads(quoteBytesObj.read()).get('$objects')
        quoteBytesObj.close()
        for quote in quoteList:
            if '$null' in quote:
                pass
            elif ('NS.objects' in quote or '$classname' in quote) and isinstance(quote, dict):
                pass
            elif isinstance(quote, dict):
                for key, value in quote.items():
                    if 'NS.string' in key:
                        fetchedQuoteList.append(value)
                    else:
                        pass
            else:
                fetchedQuoteList.append(quote)
        log.debug(f"{len(fetchedQuoteList)} quotes found.")
        log.debug(f"Fetched Quotes: {fetchedQuoteList}")
            
        log.debug("Cleaning quotes...")
        if fetchedQuoteList:
            for quote in fetchedQuoteList:
                log.debug(f"Fetched quote is of type: {type(quote)}")
                log.debug(quote)                
                cleanQuote = quote.encode("ascii", "ignore")
                cleanQuote = cleanQuote.decode()
                cleanQuote = cleanQuote.replace("\n", "")
                quoteListResponse.append(cleanQuote)
        log.debug(f"Cleaned Quote List: {quoteListResponse}")
        return quoteListResponse
    except Exception as e:
        logEvent(f"An error was encountered attempting to convert the current quote record: {e}", "error")
        raise (e)


def ValidateImage(imgObj):
    """ Function to test a bytes64 encoded image string, validate that the image is valid and is of type jpg or png """
    log.debug("Validating base64 image file")

    try:
        log.debug(f"Attempting to open {type(imgObj)} image input object...")
        try:
            image = base64.b64decode(imgObj)
            img = Image.open(BytesIO(image))
            log.debug(f"Base64 encoded image string contains a valid {img.format.lower()} image...")
            # print(dir(img))
        except Exception:
            raise Exception('file is not valid base64 image')
            log.error("Base64 image string is NOT a valid b64 image...")
            img.close()
            return False
        
        # Validate that the file is either a jpg, jpeg, or png file
        if img.format.lower() in ["jpg", "jpeg", "png"]:
            log.debug(f"{img.format.lower()} image has been valided")
            img.close()
            return True
        else:
            img.close()
            return False
    except Exception as e:
        log.error(f"An error was encountered attempting to validate the input image base64 string: {e}")
        raise (e)


def FetchImage(imgRef):
    """ Function to take either an HTML or bytes object and format it appropriately to be stored as a base64 encoded object compatible with JSON """
    log.debug(f"Checking input image type to determine proper fetch method...: {type(imgRef)}")
    try:
        if isinstance(imgRef, str) and 'http' in imgRef:
            log.debug("Image URL Found... attempting to download image")
            try:
                b64image = base64.b64encode(urlopen(imgRef).read())
                valid = ValidateImage(b64image)
            except Exception as e:
                log.error(f"An error was encountred attemtpting to download the image from the given URL: {imgRef}")
                return None
            
            # If the image is a valid image file, then return the UTF-8 encoded value so the value can be stored in JSON
            if valid:
                log.debug(f"B64 Image is of type: {type(b64image)}")
                log.debug(f"Image: {b64image.decode('utf-8')}")
                return b64image.decode('utf-8')
            else:
                return None
        elif isinstance(imgRef, bytes):
            log.debug("Image bytes object Found... attempting to validate image")

            # Caputre the byte stream
            log.debug("Captureing IO Bytes image object")  
            return None

            # Fetch the binary stream into a bytesIO object
            # imageBinary = BytesIO()
            # imageBinary.write(imgRef)
            # log.debug("Rewinding cursor to position 0 of written IO Bytes image object")
            # imageBinary.seek(0)

            # with open("raw_dump", "wb") as file:
            #     file.write(imageBinary.read())
            # sys.exit(0)
            
            # print(ValidateImage(b64Image))
            """<class 'bytes'> FOUND
            ÿØÿàJFIFØØÿáExifMMJ(iZØØ X 
            acspAPPLAPPLöÖÓ-applÊ%M8ÕÑêí8Photoshop 3.08BIM8BIM%ÔÙ²é øBûÿâ4ICC_PROFILE$applmntrRGB XYZ á
            descüecprtd#wtptrXYZgXYZ°bXYZÄrTRCØ chadø,bTRCØ gTRCØ desc
            Display P3textCopyright Apple Inc., 2017XYZ óQÌXYZ ß=¿ÿÿÿ»XYZ J¿±7
            """
            # print(b64Image.decode('latin-1'))
            # print(b64Image.decode('latin-1'))

            # Open the bytes content
            # ValidateImage(b64Image)
            # print(plistlib.loads(imageBinary.read()))
            
            # print(plistlib.loads(imgRef.read()))   
            # print(imgRef)
    except Exception as e:
        log.error(f"An error was encountered attempting to convert the current input image image: {e}")
        raise (e)


def CreateJSONCollection(bookObj):
    """This function will take a tuple input and convert the tuple to a properly formatted json object"""
    log.debug("Creating book JSON object")
    bookJsonResponse = {}
    
    try:
        # Setup Temp file to write blob to
        if isinstance(bookObj, tuple):                
            # Assign the values from the tuple to the proper variables
            # {Z_PK}
            bookId = bookObj[0] if isinstance(bookObj[0], int) else random.randrange(1000, 1500)
            bookJsonResponse.update(id=bookId)

            # {ZTITLE}
            bookTitle = str(bookObj[1]) if bookObj[1] else None
            bookJsonResponse.update(title=bookTitle)

            # {ZAUTHORSNAMELASTNAMESEARCHABLE} Authors name is stored as "first last" all lower case
            author = CapitalizeString(bookObj[2]) if bookObj[2] else None
            bookJsonResponse.update(author=author)

            # {ZBookDescription} Strip any HTML tags from the description field.
            description = CleanHTMLTags(bookObj[3]) if bookObj[3] else None
            bookJsonResponse.update(description=description)

            # {ZSERIESSEARCHABLE} Series is stored as all lowercase Letters
            series = CapitalizeString(bookObj[4]) if bookObj[4] else None
            inSeries = True if series else False
            bookJsonResponse.update(in_series=inSeries, series=series)

            # {ZPAGECOUNT}
            pageCount = bookObj[5] if isinstance(bookObj[5], int) else 0
            bookJsonResponse.update(pageCount=pageCount)

            # {ZPUBLISHER}
            publisher = CapitalizeString(bookObj[6]) if bookObj[6] else None
            bookJsonResponse.update(publisher=publisher)
            
            # {ZISBN10}
            isbn10 = bookObj[7] if bookObj[7] else None
            bookJsonResponse.update(isbn10=isbn10)

            # {ZISBN13}
            isbn13 = bookObj[8] if bookObj[8] else None
            bookJsonResponse.update(isbn13=isbn13)

            # {ZTYPE}
            version = CapitalizeString(bookObj[9]) if bookObj[9] else None
            bookJsonResponse.update(version=version)

            # {ZAVERAGERATING}
            rating = int(bookObj[10]) if bookObj[10] else int(2.0)
            bookJsonResponse.update(rating=rating)
            
            # {ZQUOTELIST} Fetch the Quotes apple Plist object, and convert it to a string object
            quoteList = FetchQuotesList(bookObj[11]) if bookObj[11] else []
            bookJsonResponse.update(quotes=quoteList, quoteCount=len(quoteList))
            
            # {ZCATEGORYLISTSEARCHABLE} Fetch list of Catagorie
            catSplit = bookObj[12].split(',') if isinstance(bookObj[12], str) else []
            categories = [category.strip(' ') for category in catSplit]
            bookJsonResponse.update(categories=categories)

            # {ZTAGLISTSEARCHABLE} Fetch list of Tags
            tagSplit = bookObj[13].split(',') if isinstance(bookObj[13], str) else []
            tags = [tag.strip() for tag in tagSplit]
            bookJsonResponse.update(tags=tags)

            # {ZPERSONALCOMMENT} Fetch any personal comments
            comments = str(bookObj[14]) if bookObj[14] else None
            bookJsonResponse.update(comments=comments)

            # {ZREMOTEIMAGEURL} Fetch and b64 encode an included image link
            image = FetchImage(bookObj[15]) if bookObj[15] else None
            bookJsonResponse.update(coverImage=image)
            # The following tests re-encoding the image and validating it to ensure its saved in correct format.
            # if bookJsonResponse.get('cover') != None:
                # stillValid = bookJsonResponse.get('cover').encode('utf-8')
                # print(stillValid)
                # print(ValidateImage(stillValid))
            
            # {ZLOCALIMAGE} Fetch the base64 encoded image
            # TODO: THIS STILL DOES NOT WORK... FILE FORMAT????
            image = FetchImage(bookObj[16]) if bookObj[16] else None
            # bookJsonResponse.update(cover=image)
            
            # Fetch timestamp fields and convert to epoch time
            createdAt = bookObj[17] if bookObj[17] else 0        # {ZCREATEDAT}
            updatedAt = bookObj[18] if bookObj[18] else 0        # {ZUPDATEDAT}
            releaseDate = bookObj[19] if bookObj[19] else 0      # {ZRELEASEDATE}
            purchaseDate = bookObj[20] if bookObj[20] else 0     # {ZPURCHASEDATE}
            readDateStart = bookObj[21] if bookObj[21] else 0    # {ZSTARTREADINGDATE}
            readDateEnd = bookObj[22] if bookObj[22] else 0      # {ZENDREADINGDATE}
            bookJsonResponse.update(
                recordCreated=createdAt,
                recordUpdated=updatedAt,
                released=releaseDate,
                purchased=purchaseDate,
                startRead=readDateStart,
                finishRead=readDateEnd
            )

            # Fetch google URL and Google ID
            googleUrl = bookObj[23] if bookObj[23] else None    # {ZGOOGLEBOOKURL}
            googleId = bookObj[24] if bookObj[24] else None    # {ZGOOGLEID}
            bookJsonResponse.update(
                googleUrl=googleUrl,
                googleId=googleId
            )
            return bookJsonResponse
        else:
            log.error(f"The input book object is of an un-expected data type. Expected tuple, received type: {type(bookObj)}")
        return jsonResponseObject
    except Exception as e:
        log.error(f"An error was encountered attempting to convert the current book record: {e}")
        raise (e)


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


if __name__ == "__main__":
    try:
        # Confirm DB File Exists
        log.debug(f"DB File Found:\t{os.path.isfile(BOOKTRACK_DB)}")
        if os.path.isfile(BOOKTRACK_DB):
            log.info("Running Query against BookTrack Database...")
        else:
            print("Please specify the proper location of the BookTrack sqlite file and try again.\n")
            sys.exit(1)

        # --------------------------------
        # FETCH DATA FROM APP SQLITE DB
        # --------------------------------
        # Run the SQLite Query and check the result file type
        # Note that the sqlite fetchone() function returns a single tuple, fetchall() returns a list of tuples
        queryResults = GetDbRecords()
        log.debug(f"queryResults are of type:\t{type(queryResults)}\n")
        log.debug(f"Single Record Sample: {queryResults[0]}")

        # # Create a list variable that will hold all of the extracted and processed Quotes
        # # Create a list variable that will hold all of the extracted and processed Books
        bookCollection = []
        # QuoteCollection = []

        # --------------------------------
        # CREATE JSON OUTPUTS
        # --------------------------------
        # Convert the query results tuple object to a proper JSON object
        if isinstance(queryResults, tuple):
            bookCollection = CreateJSONCollection(queryResults)
        elif isinstance(queryResults, list):
            # Fetch each object
            for book in queryResults:
                bookJson = CreateJSONCollection(book)
                bookCollection.append(bookJson)
        else:
            log.error(f"The queryResults object is of an un-expected data type. Expected tuple or list, received type: {type(queryResults)}")
        

        # We have the full collection in JSON now, so create the data formats bigdata data file format
        log.debug(json.dumps(bookCollection[0], indent=4))
        booksJson = {"books": bookCollection}
        WriteFile(BOOKS_JSON, booksJson, False)
        log.debug(f"{len(bookCollection)} book records have been output to {BOOKS_JSON}", True)

        # Write bigdata Files, remove quotes attribute so it can be its own secondary object
        # Full Object in BigData Format
        bigdataBookCollection = copy.deepcopy(bookCollection)
        WriteFile(BOOKS_BIGDATA, bigdataBookCollection, True)
        log.debug(f"{len(bigdataBookCollection)} book records have been output to {BOOKS_BIGDATA}", True)
        # Remove Quotes, and output new BigData Object
        for book in bigdataBookCollection:
            book.pop('quotes')
            book.pop('quoteCount')
        log.debug(bigdataBookCollection)
        WriteFile(BOOKS_BIGDATA_NO_QUOTES, bigdataBookCollection, True)
        log.debug(f"{len(bigdataBookCollection)} book records stripped of quotes have been output to {BOOKS_BIGDATA_NO_QUOTES}", True)

        # Create Quotes Object, and Output in both standard JSON as well as BigData formats
        bigdataQuoteCollection = []
        for book in bookCollection:
            bookId = book.get('id')
            title = book.get('title')
            isbn10 = book.get('isbn10')
            isbn13 = book.get('isbn13')
            bigdataBookQuotes = book.get('quotes')
            for quote in bigdataBookQuotes:
                bigdataQuoteCollection.append({"id": bookId, "title": title, "isbn10": isbn10, "isbn13": isbn13, "quote": quote})
        quotesJSON = {"quotes": bigdataQuoteCollection}
        WriteFile(QUOTES_JSON, quotesJSON, False)
        log.debug(f"{len(bigdataQuoteCollection)} book quote records have been output to {QUOTES_JSON}", True)
        WriteFile(QUOTES_BIGDATA, bigdataQuoteCollection, True)
        log.debug(f"{len(bigdataQuoteCollection)} book quote records have been output to {QUOTES_BIGDATA}", True)
    except KeyboardInterrupt:
        log.error("BookTrack2Json experienced an error fetching the requested data.")

"""
QuoteDict = {
    'Quote': f"{Quote}",
    'Source': {
        'Title': f"{BookTitle}",
        'Source Type': "Book",
        'Author': f"{Author}",
        'Page': 0,
        'Genre': [],
        'Origin': None
    },
    'Type': "Quote",
    'Favorite': False,
    'Tags': TagSplit
}
"""
