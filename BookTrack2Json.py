import sqlite3  # Relational Database Library
import logging  # Logging Library
import plistlib # Parse Apple PList File Formats
import json     # Json Library
import os       # Builtin OS Library
from io import BytesIO  # Binary Input/Output Library, used to decode blob binary data into a variable.

# BookTrackDB = "/Users/rnaeson/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite"
BookTrackDB = "library.sqlite"
Query = "SELECT ZTITLE, ZAUTHORSNAMELASTNAMESEARCHABLE, ZQUOTELIST FROM ZCDBOOK;"

def GetQuoteList():
    """This function will run the query against the BookTrack database to gather all of the quotes stored in the app"""
    logging.debug("Gathering BootTrack Information...")
    try:
        db_conn = sqlite3.connect(BookTrackDB)
        sql = db_conn.cursor()
        sql.execute(Query)
        quotelist = sql.fetchall()
        if quotelist is None:
            logging.error("No Records Returned")
        else:
            logging.debug("Quotes found...")
        sql.close()
        db_conn.close()
        return quotelist
    except sqlite3.Error as sql_error:
        sql_response = sql_error.__dict__
        logging.error("There was an issue retrieving quote records from BookTrack: ")
        logging.error(sql_response)
    return sql_response

def Convert2Dict(quoteObj):
    """This function will take a tuple input and convert the tuple to a properly formatted json object"""
    logging.debug("Converting Tuple to JSON...")
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
            # TODO: If the item has no quote, send the item back but keep it as a separate object
            # with just the book title and author. This can be used to simulate non quote data for recommendatons.
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
                        'Tags': []
                    }
                    QuoteObjectResponse.append(QuoteDict)
            # print(f"\n\n{json.dumps(QuoteObjectResponse, indent=4)}\n\n")
            return QuoteObjectResponse
        else:
            logging.error(f"The QueryResult object is of an un-expected data type. Expected tuple, recieved type: {type(QueryResult)}")
            print(f"The QueryResult object is of an un-expected data type. Expected tuple, recieved type: {type(QueryResult)}")
    except Exception as e:
        logging.error(f"An error was encountered attempting to convert the current quote record: {e}")
        raise (e)

if __name__ == "__main__":
    try:
        # Confirm DB File Exists
        print(f"\nDB File Found:\t{os.path.isfile(BookTrackDB)}")
        print("Running Query...")

        # Create a list variable that will hold all of the extracted and processed Quotes
        QuoteCollection = []

        # Run the SQLite Query and check the result file type
        # Note that the sqllite fetchone() function returns a single tuple, fetchall() returns a list of tuples
        QueryResult = GetQuoteList()
        print(f"QueryResult is of type:\t{type(QueryResult)}\n")

        # Convert the quote tuple object to a proper JSON object
        if isinstance(QueryResult, tuple):
            QuoteCollection = Convert2Dict(QueryResult)
        elif isinstance(QueryResult, list):
            for Quote in QueryResult:
                ProcessedQuotes = Convert2Dict(Quote)
                QuoteCollection += ProcessedQuotes
        else:
            logging.error(f"The QueryResult object is of an un-expected data type. Expected tuple or list, recieved type: {type(QueryResult)}")
        
        # Append the response to the Quote Collection
        print(f"\n\nNumber of Quotes Found: {len(QuoteCollection)}")
        print(json.dumps(QuoteCollection, indent=4))
    except KeyboardInterrupt:
        print("BookTrack2Json experienced an error fetching the requested data.")
