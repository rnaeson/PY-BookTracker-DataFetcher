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
import sys      # Sys Library to exit
import os       # Builtin OS Library
import re       # Add Regex support to clean HTML tags
from io import BytesIO  # Binary Input/Output Library, used to decode blob binary data into a variable.
from urllib.request import urlopen  # Download images or other content
from PIL import Image # Perform Image validation on any included images

""" ********************  User Configuration Options:  ********************"""
LOGGERLEVEL = "INFO"
# BOOKTRACK_DB = "/Users/rnaeson/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite"
BOOKTRACK_DB = "InputData/library_v1.sqlite"
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
BOOKS_JSON_OUTPUT = "OutPutData/books_2022.json"
QUOTES_ATHENA_OUTPUT = "OutPutData/quotes_athena_2022.json"
BOOKS_ATHENA_OUTPUT = "OutPutData/books_athena_2022.json"
PERSONALIZE_INTERACTIONS_OUTPUT = "OutPutData/interactions.csv"
"""************************************************************************"""

# Non Configurable Global Constants
null = "null"
randomInt = random.randrange(1000, 1500)

# Instantiate Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", LOGGERLEVEL))
Log = logging.getLogger(f"BookTrack2Json/{__name__}")
print("\n") # Print an endline to move output further below cursor
Log.debug(" Initalizing connection to BookTrack...")


def logEvent(event, loglevel):
    """ Function that will log an event in the logger and print the event to std out. """
    print(event)

    if loglevel.lower() == "debug":
        Log.debug(f" {event}")
    elif loglevel.lower() == "info":
        Log.info(f" {event}")
    elif loglevel.lower() == "warning":
        Log.warning(f" {event}")
    elif loglevel.lower() == "error":
        Log.error(f" {event}")


def GetDbRecords():
    """ Function to run the query against the BookTrack sqlite database. 
    The function gathers all of the books, quotes, and metadata stored in the app. """

    Log.debug("Gathering BootTrack Data...")
    try:
        db_conn = sqlite3.connect(BOOKTRACK_DB)
        sql = db_conn.cursor()
        Log.debug("Connected to Booktrack DB, running query")
        sql.execute(BOOKTRACK_DB_QUERY)
        ItemRecordList = sql.fetchall()
        Log.debug("Query execution completed.")
        
        if ItemRecordList is None:
            logEvent("Database Query returned 0 results", "warning")
        else:
            logEvent(f"Database Query returned {len(ItemRecordList)} results", "debug")
        Log.debug("Closing connection to Booktrack DB")
        sql.close()
        db_conn.close()
        Log.debug("Connection to BookTrack DB closed, returning resultset.")
        return ItemRecordList
    except sqlite3.Error as sql_error:
        sql_response = sql_error.__dict__
        logEvent("There was an error retrieving quote records from the BookTrack sqlite database file:\n", "error")
        logEvent(f"{sql_response}", "error")
    return sql_response


def CapitalizeString(strObj):
    """ This function will simply take a string consisting of a string, divide that string by spaces,
    and then capitalize the first letter of each word. """

    Log.debug(f"Formatting String: {strObj}")
    try:
        if not strObj or strObj == "" or strObj == " " or strObj is None:
            logEvent(f"String Value: {strObj}, not valid string, returning null", "debug")
            return null
        
        strObj = strObj.lower()
        strWordList = []

        # Authors name is stored as "first last" all lower case
        splitString = strObj.split(" ")
        Log.debug(f"String Split: {splitString}")
        
        # Capitalize each first initial
        for word in splitString:
            strWordList.append(word.capitalize())
            Log.debug(f"Capitalized word list: {strWordList}")
            strResponse = ' '.join(strWordList)
            Log.debug(f"Returning properly formatted string: {strResponse}")
        return str(strResponse)
    except Exception as e:
        logEvent(f"An unexpected error occured attempting to format the input string {e}", "error")


def CleanHTMLTags(bookDescription):
    """ This function will simply take a string consisting of the books description, and will
    clean any HTML tags found within the description object. """

    Log.debug(f"Formatting book description: {bookDescription}")
    try:
        # cleanTags = re.compile('<.*?>')
        cleanTags = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        descriptionResponse = re.sub(cleanTags, '', bookDescription)
        Log.debug(f"Returning cleaned description object: {descriptionResponse}")
        return str(descriptionResponse)
    except Exception as e:
        logEvent(f"An unexpected error occured attempting to clean the books description {e}", "error")


def FetchQuotesList(quoteObj):
    """ This function will take a bytes plist input and convert the data to a properly formatted json string"""
    Log.debug("Fetch all quotes from the book record...")
    
    try:
        Log.debug(f"Input object is of type {type(quoteObj)}")

        quoteListResponse = []
        fetchedQuoteList = []
        
        # Setup Temp file to write blob to
        Log.debug("Converting input object to IO Bytes object")
        quoteBytesObj = BytesIO()
        quoteBytesObj.write(quoteObj)
        Log.debug("Rewinding cursor to position 0 of written IO Bytes object")
        quoteBytesObj.seek(0)
  
        # Parse the Apple Plist Object format and extract the quotes
        Log.debug("Loading IO Bytes apple plist file format and parsing...")
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
        Log.debug(f"{len(fetchedQuoteList)} quotes found.")
        Log.debug(f"Fetched Quotes: {fetchedQuoteList}")
            
        Log.debug("Cleaning quotes...")
        if fetchedQuoteList:
            for quote in fetchedQuoteList:
                Log.debug(f"Fetched quote is of type: {type(quote)}")
                Log.debug(quote)                
                cleanQuote = quote.encode("ascii", "ignore")
                cleanQuote = cleanQuote.decode()
                cleanQuote = cleanQuote.replace("\n", "")
                quoteListResponse.append(cleanQuote)
        Log.debug(f"Cleaned Quote List: {quoteListResponse}")
        return quoteListResponse
    except Exception as e:
        logEvent(f"An error was encountered attempting to convert the current quote record: {e}", "error")
        raise (e)


def ValidateImage(imgObj):
    """ Function to test a bytes64 encoded image string, validate that the image is valid and is of type jpg or png """
    Log.debug("Validating base64 image file")

    try:
        Log.debug(f"Attempting to open {type(imgObj)} image input object...")
        try:
            image = base64.b64decode(imgObj)
            img = Image.open(BytesIO(image))
            Log.debug(f"Base64 encoded image string contains a valid {img.format.lower()} image...")
            # print(dir(img))
        except Exception:
            raise Exception('file is not valid base64 image')
            logEvent("Base64 image string is NOT a valid b64 image...", "error")
            img.close()
            return False
        
        # Validate that the file is either a jpg, jpeg, or png file
        if img.format.lower() in ["jpg", "jpeg", "png"]:
            Log.debug(f"{img.format.lower()} image has been valided")
            img.close()
            return True
        else:
            img.close()
            return False
    except Exception as e:
        logEvent(f"An error was encountered attempting to validate the input image base64 string: {e}", "error")
        raise (e)


def FetchImage(imgRef):
    """ Function to take either an HTML or bytes object and format it appropriately to be stored as a base64 encoded object compatible with JSON """

    Log.debug(f"Checking input image type to determine proper fetch method...: {type(imgRef)}")
    try:
        if isinstance(imgRef, str) and 'http' in imgRef:
            Log.debug("Image URL Found... attempting to download image")
            try:
                b64image = base64.b64encode(urlopen(imgRef).read())
                valid = ValidateImage(b64image)
            except Exception as e:
                logEvent(f"An error was encountred attemtpting to download the image from the given URL: {imgRef}", "error")
                return null
            
            # If the image is a valid image file, then return the UTF-8 encoded value so the value can be stored in JSON
            if valid:
                Log.debug(f"B64 Image is of type: {type(b64image)}")
                Log.debug(f"Image: {b64image.decode('utf-8')}")
                return b64image.decode('utf-8')
            else:
                return null
        elif isinstance(imgRef, bytes):
            Log.debug("Image bytes object Found... attempting to validate image")

            # Caputre the byte stream
            Log.debug("Captureing IO Bytes image object")
            
            return null

            # Fetch the binary stream into a bytesIO object
            # imageBinary = BytesIO()
            # imageBinary.write(imgRef)
            # Log.debug("Rewinding cursor to position 0 of written IO Bytes image object")
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
        logEvent(f"An error was encountered attempting to convert the current input image image: {e}", "error")
        raise (e)


def CreateJSONCollection(bookObj):
    """This function will take a tuple input and convert the tuple to a properly formatted json object"""
    Log.debug("Creating book JSON object")
    bookJsonResponse = {}
    
    try:
        # Setup Temp file to write blob to
        if isinstance(bookObj, tuple):    
            # Assign Variables
            localImage = None           # ZLOCALIMAGE
            # Dates Nested Object:
            recordCreateDate = None     # ZCREATEDAT
            recordUpdatedDate = None    # ZUPDATEDAT
            bookReleaseDate = None      # ZRELEASEDATE
            bookPurchaseDate = None     # ZPURCHASEDATE
            bookReadStartDate = None    # ZSTARTREADINGDATE
            bookReadEndDate = None      # ZENDREADINGDATE
            # Metadata Nested Object:
            googleBookURL = None        # ZREMOTEIMAGEURL
            googleId = None             # ZGOOGLEID
            
            # Assign the values from the tuple to the proper variables
            # {Z_PK}
            bookId = bookObj[0] if isinstance(bookObj[0], int) else randomInt
            bookJsonResponse.update(id=bookId)

            # {ZTITLE}
            bookTitle = str(bookObj[1]) if bookObj[1] else null
            bookJsonResponse.update(title=bookTitle)

            # {ZAUTHORSNAMELASTNAMESEARCHABLE} Authors name is stored as "first last" all lower case
            author = CapitalizeString(bookObj[2]) if bookObj[2] else null
            bookJsonResponse.update(author=author)

            # {ZBookDescription} Strip any HTML tags from the description field.
            description = CleanHTMLTags(bookObj[3]) if bookObj[3] else null
            bookJsonResponse.update(description=description)

            # {ZSERIESSEARCHABLE} Series is stored as all lowercase Letters
            series = CapitalizeString(bookObj[4]) if bookObj[4] else null
            inSeries = True if series else False
            bookJsonResponse.update(in_series=inSeries, series=series)

            # {ZPAGECOUNT}
            pageCount = bookObj[5] if isinstance(bookObj[5], int) else 0
            bookJsonResponse.update(pageCount=pageCount)

            # {ZPUBLISHER}
            publisher = CapitalizeString(bookObj[6]) if bookObj[6] else null
            bookJsonResponse.update(publisher=publisher)
            
            # {ZISBN10}
            isbn10 = bookObj[7] if bookObj[7] else null
            bookJsonResponse.update(isbn10=isbn10)

            # {ZISBN13}
            isbn13 = bookObj[8] if bookObj[8] else null
            bookJsonResponse.update(isbn13=isbn13)

            # {ZTYPE}
            version = CapitalizeString(bookObj[9]) if bookObj[9] else null
            bookJsonResponse.update(version=version)

            # {ZAVERAGERATING}
            rating = int(bookObj[10]) if bookObj[10] else int(2.0)
            bookJsonResponse.update(rating=rating)
            
            # {ZQUOTELIST} Fetch the Quotes apple Plist object, and convert it to a string object
            quoteList = FetchQuotesList(bookObj[11]) if bookObj[11] else []
            bookJsonResponse.update(quotes=quoteList)
            
            # {ZCATEGORYLISTSEARCHABLE} Fetch list of Catagorie
            catSplit = bookObj[12].split(',') if isinstance(bookObj[12], str) else []
            categories = [category.strip(' ') for category in catSplit]
            bookJsonResponse.update(categories=categories)

            # {ZTAGLISTSEARCHABLE} Fetch list of Tags
            tagSplit = bookObj[13].split(',') if isinstance(bookObj[13], str) else []
            tags = [tag.strip() for tag in tagSplit]
            bookJsonResponse.update(tags=tags)

            # {ZPERSONALCOMMENT} Fetch any personal comments
            comments = str(bookObj[14]) if bookObj[14] else null
            bookJsonResponse.update(comments=comments)

            # {ZREMOTEIMAGEURL} Fetch and b64 encode an included image link
            image = FetchImage(bookObj[15]) if bookObj[15] else null
            bookJsonResponse.update(coverImage=image)
            # The following tests re-encoding the image and validating it to ensure its saved in correct format.
            # if bookJsonResponse.get('cover') != null:
                # stillValid = bookJsonResponse.get('cover').encode('utf-8')
                # print(stillValid)
                # print(ValidateImage(stillValid))
            
            # {ZLOCALIMAGE} Fetch the base64 encoded image
            # TODO: THIS STILL DOES NOT WORK... FILE FORMAT????
            image = FetchImage(bookObj[16]) if bookObj[16] else null
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
            googleUrl = bookObj[23] if bookObj[23] else null    # {ZGOOGLEBOOKURL}
            googleId = bookObj[24] if bookObj[24] else null    # {ZGOOGLEID}
            bookJsonResponse.update(
                googleUrl=googleUrl,
                googleId=googleId
            )
            return bookJsonResponse
        else:
            logEvent(f"The input book object is of an un-expected data type. Expected tuple, received type: {type(bookObj)}", "error")
        return jsonResponseObject
    except Exception as e:
        logEvent(f"An error was encountered attempting to convert the current book record: {e}", "error")
        raise (e)


def WriteFile(fileName, listFile, athenaFormat=False):
    """This function write the list files out as JSON files to the file system."""
    try:
        Log.debug("Writing data records to disk...")
        outFile = open(fileName, "w")
        if athenaFormat:
            for lineObj in listFile:
                outFile.write(f"{json.dumps(lineObj)}\n")
        else:
            outFile.write(json.dumps(listFile, indent=4))
        outFile.close()
    except Exception as e:
        logEvent(f"An error has been encountered attempting to write the output file to the specified location: {e}", "error")
        raise(e)


if __name__ == "__main__":
    try:
        # Confirm DB File Exists
        logEvent(f"DB File Found:\t{os.path.isfile(BOOKTRACK_DB)}", "debug")
        if os.path.isfile(BOOKTRACK_DB):
            print("Running Query...")
        else:
            print("Please specify the proper location of the BookTrack sqlite file and try again.\n")
            sys.exit(1)

        # --------------------------------
        # FETCH DATA FROM APP SQLITE DB
        # --------------------------------
        # Run the SQLite Query and check the result file type
        # Note that the sqlite fetchone() function returns a single tuple, fetchall() returns a list of tuples
        queryResults = GetDbRecords()
        Log.debug(f"queryResults are of type:\t{type(queryResults)}\n", "debug")
        Log.debug(f"Single Record Sample: {queryResults[0]}")

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
            logEvent(f"The queryResults object is of an un-expected data type. Expected tuple or list, received type: {type(queryResults)}", "error")
        

        # We have the full collection in JSON now, so create the data formats Athena data file format
        Log.debug(json.dumps(bookCollection, indent=4))
        WriteFile(BOOKS_JSON_OUTPUT, bookCollection, False)

        # # Write Athena Files
        athenaBookCollection = copy.deepcopy(bookCollection)
        for book in athenaBookCollection:
            book.pop('quotes')
        Log.debug(athenaBookCollection)
        WriteFile(BOOKS_ATHENA_OUTPUT, athenaBookCollection, True)

        athenaQuoteCollection = []
        for book in bookCollection:
            athenaBookId = book.get('id')
            athenaBookQuotes = book.get('quotes')
            for quote in athenaBookQuotes:
                athenaQuoteCollection.append({"id": athenaBookId, "quote": quote})
        Log.debug(athenaQuoteCollection)
        WriteFile(QUOTES_ATHENA_OUTPUT, athenaQuoteCollection, True)

        # Write Personalize Interactions File

        # Append the response to the Quote Collection
        # print(f"\nNumber of Quotes Found: {len(QuoteCollection)}")
        # print(f"Number of Books Cataloged: {len(BookCollection)}\n")
        
        # # Write files to disk
        # # print(json.dumps(QuoteCollection, indent=4))
        # # print(json.dumps(BookCollection, indent=4))
    except KeyboardInterrupt:
        logEvent("BookTrack2Json experienced an error fetching the requested data.", "error")


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