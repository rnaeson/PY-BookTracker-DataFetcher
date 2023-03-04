# BookTracker-DataFetcher

## Description:
This repository contains a python script that can be used to extractct certain data from the BookTracker BookShelf Desktop App. I personally use BookTracker to track my reading goals, page counts, and to generally catagorize and organize my books. I had a need to gather some base data about each book and especially wanted to be able to extract the Quotes that I had input into Booktracker, and built this script to do just that.

## Pre-Requisites:
There are no pre-requisites to running this script. All of the included libraries are Python built-in librarires. No pip installs required. It is HIGHLY advisable that you copy your BookTracker database and run this script against the copy. While no write operations are present in the execution of this script, its always safer to run external scripts against a database backup or copy instaead of the live version that is stored on iCloud. You must also be using the Desktop version of the app to execute this script. Upon installing the desktop app, the database file can be found in the following location once the Desktop app has been installed:  ```/Users/{USERNAME}/Library/Group\ Containers/group.com.simonemontalto.booktrack.coredata/library.sqlite```

## Variables:
