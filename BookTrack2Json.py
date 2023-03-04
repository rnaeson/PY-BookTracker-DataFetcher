import sqlite3  # Relational Database Library
import logging  # Logging Library
import plistlib # Parse Apple PList File Formats
import json     # Json Library
import os       # Builtin OS Library
from io import BytesIO  # Binary Input/Output Library, used to decode blob binary data into a variable.

# BookTrackDB = "/Users/rnaeson/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite"
# The following assumes that the SQLite DB file has been copied to the same directory that this script lives. It can be changed
# by altering the location specified by the BookTrackDB Variable.
BookTrackDB = "library.sqlite"
Query = "SELECT ZTITLE, ZAUTHORSNAMELASTNAMESEARCHABLE, ZQUOTELIST, ZTAGLISTSEARCHABLE, ZBookDescription, ZISBN13 FROM ZCDBOOK;"
QuotesOutputFile = "quotes_2023.json"
BooksOutputFile = "books_2023.json"

def GetQuoteList():
    """This function will run the query against the BookTrack database to gather all of the quotes stored in the app"""
    logging.debug("Gathering BootTrack Information...")
    try:
        db_conn = sqlite3.connect(BookTrackDB)
        sql = db_conn.cursor()
        sql.execute(Query)
        QuoteList = sql.fetchall()
        if QuoteList is None:
            logging.error("No Records Returned")
        else:
            logging.debug("Quotes found...")
        sql.close()
        db_conn.close()
        return QuoteList
    except sqlite3.Error as sql_error:
        sql_response = sql_error.__dict__
        logging.error("There was an issue retrieving quote records from BookTrack: ")
        logging.error(sql_response)
    return sql_response

def CatalogBook(quoteObj):
    """This function will take a tuple input and convert the tuple to a properly formatted json object"""
    logging.debug("Creating book meta object")
    try:
        # Setup Temp file to write blob to
        if isinstance(quoteObj, tuple):    
            # Assign Variables
            BookTitle = None
            Author = None
            Description = None
            Isbn = None
            Tags = None

            # Assign the values from the tuple to the proper variables
            BookTitle = quoteObj[0]
            AuthorFullName = quoteObj[1].split(" ")
            AuthorNameFix = []
            
            # Capitalize Each First Initial
            for Name in AuthorFullName:
                AuthorNameFix.append(Name.capitalize())
            Author = ' '.join(AuthorNameFix)

            # Gather Tags
            Tags = quoteObj[3]
            TagSplit = Tags.split(',')
            
            # Assign Description and Isbn
            Description = quoteObj[4]
            Isbn = quoteObj[5]
            
            # This can be used to simulate non quote data for recommendations.
            BookObjectResponse = {
                'Title': f"{BookTitle}",
                'Author': f"{Author}",
                'Description': f"{Description}",
                'ISBN': f"{Isbn}",
                'Favorite': False,
                'Tags': TagSplit
            }
            # print(f"\n\n{json.dumps(BookObjectResponse, indent=4)}\n\n")
        else:
            logging.error(f"The QueryResult object is of an un-expected data type. Expected tuple, received type: {type(QueryResult)}")
            print(f"The QueryResult object is of an un-expected data type. Expected tuple, received type: {type(QueryResult)}")
        return BookObjectResponse
    except Exception as e:
        logging.error(f"An error was encountered attempting to convert the current book record: {e}")
        raise (e)

def FetchQuotes(quoteObj):
    """This function will take a tuple input and convert the tuple to a properly formatted json object"""
    logging.debug("Fetch all quotes from the book record...")
    try:
        # Setup Temp file to write blob to
        if isinstance(quoteObj, tuple):
            QuoteBinary = BytesIO()
            QuoteBinary.write(quoteObj[2])
            QuoteBinary.seek(0)
    
            # Assign Variables
            BookTitle = None
            Author = None
            QuoteList = []

            # Assign the values from the tuple to the proper variables
            BookTitle = quoteObj[0]
            AuthorFullName = quoteObj[1].split(" ")
            AuthorNameFix = []
            
            # Capitalize Each First Initial
            for Name in AuthorFullName:
                AuthorNameFix.append(Name.capitalize())
            Author = ' '.join(AuthorNameFix)

            # Gather Tags
            Tags = quoteObj[3]
            TagSplit = Tags.split(',')
            
            # Parse the Apple Plist Object format and extract the quotes
            QuoteObj = plistlib.loads(QuoteBinary.read()).get('$objects')
            
            for item in QuoteObj:
                if '$null' in item:
                    pass
                elif ('NS.objects' in item or '$classname' in item) and isinstance(item, dict):
                    pass
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if key == 'NS.string':
                            QuoteList.append(value)
                        else:
                            pass
                else:
                    QuoteList.append(item)            
            
            # If the item has a quote then print it
            QuoteObjectResponse = []
            if QuoteList:
                # print(f"Title:\t{BookTitle}")
                # print(f"Author:\t{Author}")
                # print(f"Quote:\t{type(Quote)}")
                # print(f"Quote Count:\t{len(QuoteList)}")
                # print(f"{QuoteList}\n")

                for Quote in QuoteList:
                    Quote = Quote.strip()
                    Quote = Quote.replace("\n", " ")
                    Quote = Quote.replace("\u2019", "'")
                
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
                    QuoteObjectResponse.append(QuoteDict)
            # print(f"\n\n{json.dumps(QuoteObjectResponse, indent=4)}\n\n")
            return QuoteObjectResponse
        else:
            logging.error(f"The QueryResult object is of an un-expected data type. Expected tuple, received type: {type(QueryResult)}")
            print(f"The QueryResult object is of an un-expected data type. Expected tuple, received type: {type(QueryResult)}")
    except Exception as e:
        logging.error(f"An error was encountered attempting to convert the current quote record: {e}")
        raise (e)

def Write2File(fileName, listFile):
    """This function write the list files out as JSON files to the file system."""
    try:
        logging.debug("Writeing data records to disk...")
        File = open(fileName, "w")
        File.write(listFile)    
        File.close()
    except Exception as e:
        logging.error(f"An error has been encountered attempting to write the output file to the specified location: {e}")
        raise(e)


if __name__ == "__main__":
    try:
        # Confirm DB File Exists
        print(f"\nDB File Found:\t{os.path.isfile(BookTrackDB)}")
        print("Running Query...")

        # --------------------------------
        # FETCH DATA FROM APP SQLITE DB
        # --------------------------------
        # Run the SQLite Query and check the result file type
        # Note that the sqlite fetchone() function returns a single tuple, fetchall() returns a list of tuples
        QueryResult = GetQuoteList()
        print(f"QueryResult is of type:\t{type(QueryResult)}\n")

        # Create a list variable that will hold all of the extracted and processed Quotes
        # Create a list variable that will hold all of the extracted and processed Books
        QuoteCollection = []
        BookCollection = []

        # --------------------------------
        # FETCH QUOTES & FETCH BOOK LIST
        # --------------------------------
        # Convert the quote tuple object to a proper JSON object
        if isinstance(QueryResult, tuple):
            QuoteCollection = FetchQuotes(QueryResult)
            BookCollection = CatalogBook(QueryResult)
        elif isinstance(QueryResult, list):
            # Fetch Quotes
            for Quote in QueryResult:
                ProcessedQuotes = FetchQuotes(Quote)
                QuoteCollection += ProcessedQuotes
            # Catalog Book
            for Book in QueryResult:
                if isinstance(Book, tuple):
                    BookObject = CatalogBook(Book)
                    BookCollection.append(BookObject)
                else:
                    print(Book)
                    break
        else:
            logging.error(f"The QueryResult object is of an un-expected data type. Expected tuple or list, received type: {type(QueryResult)}")

        # Append the response to the Quote Collection
        print(f"\nNumber of Quotes Found: {len(QuoteCollection)}")
        print(f"Number of Books Cataloged: {len(BookCollection)}\n")
        
        # Write files to disk
        # print(json.dumps(QuoteCollection, indent=4))
        # print(json.dumps(BookCollection, indent=4))
        Write2File(QuotesOutputFile, json.dumps(QuoteCollection, indent=4))
        Write2File(BooksOutputFile, json.dumps(BookCollection, indent=4))
    except KeyboardInterrupt:
        print("BookTrack2Json experienced an error fetching the requested data.")
