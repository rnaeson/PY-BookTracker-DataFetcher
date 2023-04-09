# BookTracker-DataFetcher

## Description:
This repository contains python scripts that can be used to extractct certain data from the Apple/IOS BookTracker BookShelf Desktop App, along with 2 other book drive datasets, namely the GroupLens BookGenome project and Book Crossing. I personally use BookTracker to track my reading goals, page counts, and to generally catagorize and organize my books. I had a need to gather some base data about each book and especially wanted to be able to extract the Quotes that I had input into Booktracker, and built this script to do just that.

## Pre-Requisites:
PIL is used to download images from included image links, so a `pip install -r requirements.txt` should be performed prior to running the parsseBookTracker.py file. It is HIGHLY advisable that you copy your BookTracker database and run this script against the copy. While no write operations are present in the execution of this script, its always safer to run external scripts against a database backup or copy instaead of the live version that is stored on iCloud. You must also be using the Desktop version of the app to execute this script. Upon installing the desktop app, the database file can be found in the following location once the Desktop app has been installed:  ```/Users/{USERNAME}/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite```

## Scripts:
* parseBookXng - This script can be used to parse the [Book-Xng Collection files](http://www2.informatik.uni-freiburg.de/~cziegler/BX/). The script will produce a standard JSON output, bigdata formatted output, and personalize items, ratings, and interactions data.
* parseBookGenome - This script can be used to parse the [GroupLens BookGenome](https://grouplens.org/datasets/book-genome/). The script will produce a standard JSON output file and bigdata formatted output file.
* parseBookTracker - This script will parse a [BookTracker](https://booktrack.app/) database and extract books, quotes, and book metadata from the database. The script will produce a standard JSON output file, big data formatted file, and quote files. (2 versions curently as I have an old database on my old AppleId, and new on the new AppleId)
* syncBookTrackXng - This script will merge 2 versions of results from a parseBookTracker exectution. It will merge any quotes found in the old data set into the new data set. It will then compare each book item with the 200K+ items in the BookXng database (TODO: Add Book Genome data to that data search), and add proper ISBNs to match. It will then write out aggragated book, quote, big data formatted versions of both aggragated files, and matched only versions (Where the book object was found in the BookXng dataset) as well.


## Output:
The script outputs a file that has a focus around quotes, and another file that has a focus around the books stored in the App. Examples of both can be found below.

### Quotes.json Output File Format:

```json
{
    "quotes": [
        {
            "id": "9780553582024",
            "title": "A Feast for Crows",
            "isbn10": "055358202",
            "isbn13": "9780553582024",
            "quote": "Words are like arrows, once loosened you cannot call them back (33)"
        },
        {
            "id": "9781798967652",
            "title": "On Writing and Worldbuilding",
            "isbn10": "1798967650",
            "isbn13": "9781798967652",
            "quote": "Yelling into a pillow that you don't know how to write is more of a prerequisite to being a writer than anything else. [16]"
        },
        {
            "id": "9781798967652",
            "title": "On Writing and Worldbuilding",
            "isbn10": "1798967650",
            "isbn13": "9781798967652",
            "quote": "\"I think there are two types of writers, the architects and the gardeners. The architects plan everything ahead of time, like an architect building a house. They know how many rooms are going to be in the house, what kind of roof they're going to have, where the wires are going to run, what kind of plumbing there's going to be. They have the whole thing designed and blueprinted out before they even nail the first board up. The gardeners dig a hole, drop in a seed and water it. They kind of know what seed it is, they know if they planted a fantasy seed or mystery seed or whatever. But as the plant comes up and they water it, they don't know how many branches it's going to have, they find out as it grows. - George RR Martin [226]"
        }
}
```

### Books.json Output File Format:

```json
{
    "books": [
        {
            "id": 1,
            "title": "Generation One",
            "author": "Pittacus Lore",
            "description": "The first book in a pulse-pounding new series thats set in the world of the #1 New York Times bestselling I Am Number Four series. The war may be overbut for the next generation, the battle has just begun!It has been over a year since the invasion of Earth was thwarted in Pittacus Lores United as One. But in order to win, our alien allies known as the Garde unleashed their Loric energy that spread throughout the globe. Now human teenagers have begun to develop incredible powers of their own, known as Legacies.To help these incredible and potentially dangerous individualsand put the world at easethe Garde have created an academy where they can train this new generation to control their powers and hopefully one day help mankind. But not everyone thinks thats the best use of their talents. And the teens may need to use their Legacies sooner than they ever imagined. Perfect for fans of Marvels X-Men and Rick Yanceys The 5th Wave, this epic new series follows a diverse cast of teens as they struggle to hone their abilities and decide what, if anything, they should do with them. As a spin-off of the bestselling I Am Number Four series, those familiar with the original books and newcomers alike will devour this fast-paced, action-packed sci-fi adventure.",
            "in_series": true,
            "series": "I Am Number Four",
            "pageCount": 404,
            "publisher": "Harpercollins",
            "isbn10": "0062493744",
            "isbn13": "9780062493743",
            "version": "Physicalbook",
            "rating": 2,
            "quotes": [],
            "quoteCount": 0,
            "categories": [
                "action & adventure",
                "alien contact topic",
                "fantasy",
                "fiction",
                "science & technology",
                "science fiction",
                "space travel"
            ],
            "tags": [
                "action & adventure",
                "fantasy",
                "fiction",
                "hardcover",
                "science fiction",
                "space travel"
            ],
            "comments": null,
            "coverImage": null,
            "recordCreated": 694808193.316531,
            "recordUpdated": 699600946.584253,
            "released": 520207200,
            "purchased": 597279600,
            "startRead": 599526000,
            "finishRead": 600735600,
            "googleUrl": null,
            "googleId": "lbwovgAACAAJ",
            "bookId": 0
        },
        {
            "id": 2,
            "title": "The Song of Achilles (Enhanced Edition)",
            "author": "Madeline Miller",
            "description": "Enter the world of Homer's ancient Greece with the enhanced e-book edition of The Song of Achilles. This edition lets you further engage with this compelling story through video interviews with Madeline Miller and Gregory Maguire, bestselling author of the Wicked series, clips from the audio book at the start of each chapter, an illustrated map, and a pop-up gallery featuring over 40 images and descriptions of the characters, armor, and ships found in the book.The legend begins...Greece in the age of heroes. Patroclus, an awkward young prince, has been exiled to the kingdom of Phthia to be raised in the shadow of King Peleus and his golden son, Achilles. \"\"The best of all the Greeks\"\"strong, beautiful, and the child of a goddessAchilles is everything the shamed Patroclus is not. Yet despite their differences, the boys become steadfast companions. Their bond deepens as they grow into young men and become skilled in the arts of war and medicinemuch to the displeasure and the fury of Achilles' mother, Thetis, a cruel sea goddess with a hatred of mortals.When word comes that Helen of Sparta has been kidnapped, the men of Greece, bound by blood and oath, must lay siege to Troy in her name. Seduced by the promise of a glorious destiny, Achilles joins their cause, and torn between love and fear for his friend, Patroclus follows. Little do they know that the Fates will test them both as never before and demand a terrible sacrifice.Built on the groundwork of the Iliad, Madeline Miller's page-turning, profoundly moving, and blisteringly paced retelling of the epic Trojan War marks the launch of a dazzling career.Please note that due to the large file size of these special features this enhanced e-book may take longer to download then a standard e-book.",
            "in_series": true,
            "series": "Greek Mythology",
            "pageCount": 378,
            "publisher": "Harpercollins",
            "isbn10": "0062201883",
            "isbn13": "9780062201881",
            "version": "Physicalbook",
            "rating": 2,
            "quotes": [],
            "quoteCount": 0,
            "categories": [
                "action & adventure",
                "epic",
                "fairy tales",
                "fiction",
                "folk tales",
                "history",
                "leadership",
                "legends & mythology",
                "military",
                "mythology",
                "philosophy",
                "romance"
            ],
            "tags": [
                "action & adventure",
                "fantasy",
                "favorites",
                "fiction",
                "hardcover",
                "inspirational",
                "leadership",
                "mythology",
                "romance"
            ],
            "comments": null,
            "coverImage": null,
            "recordCreated": 694808193.357333,
            "recordUpdated": 694808195.09378,
            "released": 352681200,
            "purchased": 652917600,
            "startRead": 653695200,
            "finishRead": 654127200,
            "googleUrl": null,
            "googleId": "wkgdEAAAQBAJ",
            "bookId": 0
        }
}
```

> Latest Outputs can be found in the Outputs folder for all script exectutions


## Script Execution:
Copy the BookTracker application sqlite database file ```library.sqlite``` to the Datasets/BookTracker folder in the same directory as this script, or change the variable to reference the database file's location and then execute the script with the following command:
```python3 parseBookTracker.py```


## TODO:
Update this readme with better details on the other script executions, or break those out into their own project / repositories, and document each one accordingly. Right now under deadline, no time to make all the things pretty