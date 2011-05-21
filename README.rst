MultiStorage
============
Service that will act as a storage for different applications providing a fairly
simple REST interface for managing the information and retrieving it.

Install
+++++++
Just run create_env.sh and you will end up with a nice virtual environment
(courtesy of virtualenv) with all the requirements installed.

Usage
+++++
Each application willing to interact with the storage will use an application id
provided, and for each kind of data that it will store a collection name should
be set in the url.
With these two rules in mind the *urls* will be like this:

**/appID/collectionName/**

This urls will accomplish the following regex:

**/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]*)**

**GET**, **POST**, **PUT**, **HEAD** and **DELETE** methods will used and each
one of them, with the urls, will represent a different action in the system.

* REST interface

  * Operations over collections

      * Collection exists (HEAD)
        /appID/collectionName/
      * List Information retrieval (GET)
        /appID/collectionName/
      * Posting (POST)
        /appID/collectionName/
      * Delete collection (DELETE)
        /appID/collectionName/

  * Operation ove items

      * Check for existence (HEAD)
        /appID/collectionName/id
      * Retrieve one item information (GET)
        /appID/collectionName/id
      * Updating (PUT)
        /appID/collectionName/id
      * Deleting (DELETE)
        /appID/collectionName/id

* JSON as information markup
* Cache
* Auth
