# BookTracker-DataFetcher

## Description:
This repository contains a python script that can be used to extractct certain data from the BookTracker BookShelf Desktop App. I personally use BookTracker to track my reading goals, page counts, and to generally catagorize and organize my books. I had a need to gather some base data about each book and especially wanted to be able to extract the Quotes that I had input into Booktracker, and built this script to do just that.

## Pre-Requisites:
There are no pre-requisites to running this script. All of the included libraries are Python built-in librarires. No pip installs required. It is HIGHLY advisable that you copy your BookTracker database and run this script against the copy. While no write operations are present in the execution of this script, its always safer to run external scripts against a database backup or copy instaead of the live version that is stored on iCloud. You must also be using the Desktop version of the app to execute this script. Upon installing the desktop app, the database file can be found in the following location once the Desktop app has been installed:  ```/Users/{USERNAME}/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite```

## Variables:
* BookTrackDB - Variable to reference the location of the Booktracker application sqlite database.
* Query - Query to run against the Booktracker application sqlite database.
* QuotesOutputFile - Variable to reference the output location where the Quotes JSON output will be written
* BooksOutputFile - Variable to reference the output location where the Books JSON output will be written

## Output:
The script outputs a file that has a focus around quotes, and another file that has a focus around the books stored in the App. Examples of both can be found below.

### Quotes.json Output File Format:

```json
[
    {
        "Quote": "You can't set yourself on fire to keep someone else warm [116]",
        "Source": {
            "Title": "Runes for Beginners",
            "Source Type": "Book",
            "Author": "Lisa Chamberlain",
            "Page": 0,
            "Genre": [],
            "Origin": null
        },
        "Type": "Quote",
        "Favorite": false,
        "Tags": [
            "afterlife & reincarnation",
            "hardcover",
            "historical",
            "informational",
            "mythology",
            "non-fiction",
            "reference",
            "runes",
            "spirituality",
            "vikings"
        ]
    },
    {
        "Quote": "Life is a dream from which we all must wake before we can dream again. [102]",
        "Source": {
            "Title": "The Fires of Heaven",
            "Source Type": "Book",
            "Author": "Robert Jordan",
            "Page": 0,
            "Genre": [],
            "Origin": null
        },
        "Type": "Quote",
        "Favorite": false,
        "Tags": [
            "action & adventure",
            "afterlife & reincarnation",
            "epic fantasy",
            "fantasy",
            "favorites",
            "fiction",
            "hardcover",
            "kindle",
            "recommendation",
            "series"
        ]
    }
]
```

### Books.json Output File Format:

```json
[
    {
        "Title": "The Song of Achilles (Enhanced Edition)",
        "Author": "Madeline Miller",
        "Description": "<p>Enter the world of Homer's ancient Greece with the enhanced e-book edition of The Song of Achilles. This edition lets you further engage with this compelling story through video interviews with Madeline Miller and Gregory Maguire, bestselling author of the Wicked series, clips from the audio book at the start of each chapter, an illustrated map, and a pop-up gallery featuring over 40 images and descriptions of the characters, armor, and ships found in the book.</p><p>The legend begins...</p><p>Greece in the age of heroes. Patroclus, an awkward young prince, has been exiled to the kingdom of Phthia to be raised in the shadow of King Peleus and his golden son, Achilles. \"\"The best of all the Greeks\"\"\u2014strong, beautiful, and the child of a goddess\u2014Achilles is everything the shamed Patroclus is not. Yet despite their differences, the boys become steadfast companions. Their bond deepens as they grow into young men and become skilled in the arts of war and medicine\u2014much to the displeasure and the fury of Achilles' mother, Thetis, a cruel sea goddess with a hatred of mortals.</p><p>When word comes that Helen of Sparta has been kidnapped, the men of Greece, bound by blood and oath, must lay siege to Troy in her name. Seduced by the promise of a glorious destiny, Achilles joins their cause, and torn between love and fear for his friend, Patroclus follows. Little do they know that the Fates will test them both as never before and demand a terrible sacrifice.</p><p>Built on the groundwork of the Iliad, Madeline Miller's page-turning, profoundly moving, and blisteringly paced retelling of the epic Trojan War marks the launch of a dazzling career.</p><p>Please note that due to the large file size of these special features this enhanced e-book may take longer to download then a standard e-book.</p>",
        "ISBN": "9780062201881",
        "Favorite": false,
        "Tags": [
            "action & adventure",
            "fantasy",
            "favorites",
            "fiction",
            "hardcover",
            "inspirational",
            "leadership",
            "mythology",
            "romance"
        ]
    },
    {
        "Title": "Ready Player One",
        "Author": "Ernest Cline",
        "Description": "<p>At once wildly original and stuffed with irresistible nostalgia, READY PLAYER ONE is a spectacularly genre-busting, ambitious, and charming debut\u2014part quest novel, part love story, and part virtual space opera set in a universe where spell-slinging mages battle giant Japanese robots, entire planets are inspired by <i>Blade Runner</i>, and flying DeLoreans achieve light speed.<br> <br> It\u2019s the year 2044, and the real world is an ugly place.<br> <br> Like most of humanity, Wade Watts escapes his grim surroundings by spending his waking hours jacked into the OASIS, a sprawling virtual utopia that lets you be anything you want to be, a place where you can live and play and fall in love on any of ten thousand planets.<br> <br> And like most of humanity, Wade dreams of being the one to discover the ultimate lottery ticket that lies concealed within this virtual world.\u00a0For somewhere inside this giant networked playground, OASIS creator James Halliday has hidden a series of fiendish puzzles that will yield massive fortune\u2014and remarkable power\u2014to whoever can unlock them.\u00a0\u00a0<br> <br> For years, millions have struggled fruitlessly to attain this prize, knowing only that Halliday\u2019s riddles are based in the pop culture he loved\u2014that of the late twentieth century.\u00a0And for years, millions have found in this quest another means of escape, retreating into happy, obsessive study of Halliday\u2019s icons. Like many of his contemporaries, Wade is as comfortable debating the finer points of John Hughes\u2019s oeuvre, playing Pac-Man, or reciting Devo lyrics as he is scrounging power to run his OASIS rig.<br> <br> And then Wade stumbles upon the first puzzle.<br> <br> Suddenly the whole world is watching, and thousands of competitors join the hunt\u2014among them certain powerful players who are willing to commit very real murder to beat Wade to this prize. Now the only way for Wade to survive and preserve everything he knows is to <i>win</i>. But to do so, he may have to leave behind his oh-so-perfect virtual existence and face up to life\u2014and love\u2014in the real world he\u2019s always been so desperate to escape.\u00a0<br> \u00a0<br> A world at stake.<br> A quest for the ultimate prize.<br> <b>Are you ready?</b></p>",
        "ISBN": "9780307887436",
        "Favorite": false,
        "Tags": [
            "action & adventure",
            "computer science",
            "fantasy",
            "fiction",
            "hardcover"
        ]
    },
    {
        "Title": "A Feast for Crows",
        "Author": "George R. R. Martin",
        "Description": "<b><b>THE BOOK BEHIND THE FOURTH SEASON OF THE ACCLAIMED HBO SERIES <i>GAME OF THRONES</i></b><br></b><br>Few books have captivated the imagination and won the devotion and praise of readers and critics everywhere as has George R. R. Martin's monumental epic cycle of high fantasy. Now, in <i>A Feast for Crows</i>, Martin delivers the long-awaited fourth book of his landmark series, as a kingdom torn asunder finds itself at last on the brink of peace . . . only to be launched on an even more terrifying course of destruction.<br><br><b>A FEAST FOR CROWS<br><br></b>It seems too good to be true. After centuries of bitter strife and fatal treachery, the seven powers dividing the land have decimated one another into an uneasy truce. Or so it appears. . . . With the death of the monstrous King Joffrey, Cersei is ruling as regent in King's Landing. Robb Stark's demise has broken the back of the Northern rebels, and his siblings are scattered throughout the kingdom like seeds on barren soil. Few legitimate claims to the once desperately sought Iron Throne still exist\u2014or they are held in hands too weak or too distant to wield them effectively. The war, which raged out of control for so long, has burned itself out. <br><br>But as in the aftermath of any climactic struggle, it is not long before the survivors, outlaws, renegades, and carrion eaters start to gather, picking over the bones of the dead and fighting for the spoils of the soon-to-be dead. Now in the Seven Kingdoms, as the human crows assemble over a banquet of ashes, daring new plots and dangerous new alliances are formed, while surprising faces\u2014some familiar, others only just appearing\u2014are seen emerging from an ominous twilight of past struggles and chaos to take up the challenges ahead. <br><br>It is a time when the wise and the ambitious, the deceitful and the strong will acquire the skills, the power, and the magic to survive the stark and terrible times that lie before them. It is a time for nobles and commoners, soldiers and sorcerers, assassins and sages to come together and stake their fortunes . . . and their lives. For at a feast for crows, many are the guests\u2014but only a few are the survivors.<br><br><br><i>From the Hardcover edition.</i>",
        "ISBN": "9780553582024",
        "Favorite": false,
        "Tags": [
            "action & adventure",
            "fantasy",
            "fiction",
            "hardcover"
        ]
    }
]
```

## Script Execution:
Copy the BookTracker application sqlite database file ```library.sqlite``` to the same directory as this script, or change the variable to reference the database file's location and then execute the script with the following command:
```python3 -m BookTrack2Json.py```