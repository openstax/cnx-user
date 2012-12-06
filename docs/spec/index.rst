===================
Draft specification
===================


User ID
-------


We shall create a new, distributable and federatable user id of the
follwoing form::

   org.cnx.users.f81d4fae-7dec-11d0-a765-00a0c91e6bf6

It is the repository domain name reversed, with uuid in urn string
format.  This will give us a globally unique userid that is globally
unique, linked to originating repo, so it can be traced back to a
given source and fairly easily details requested from it.





User Media Type 
---------------

A user media type is a JSON formatted document,
A user-profile-document contains all user personal 
information we store.  Its fields are shown in :doc:`user-details`


API
===

We shall support the following APIs


GET user-details
----------------

::

  curl http://www.cnx.org/user/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383

You should expect ::

    HTTP/1.1 200 OK
    Server: nginx
    Date: Fri, 12 Oct 2012 23:33:14 GMT
    Content-Type: application/json; charset=utf-8
    Connection: keep-alive
    Status: 200 OK
    X-cnx-user-detail-version: 0.0.1

Errors
------

There are two supported errors

* sending a malformed user id, that does not match parser.
  Not supported in version 0.0.1

* 404 - Not found
  We could not find that user at this user-detail-store.
  A future service may be able to onward search for details

  


POST user-details
-----------------


A POST request with a minimum document set out::

    {
	 "id": null,
	 "identifiers": [
	     "http://openid.cnx.org/pbrian"
			],
	 "version": "0.0.1"
    }

The above fields MUST be supplied, including the null ID
If those fields are not supplied a 422 error will be generated.

If any fields sent do not match the schema for the version, a 422 error will be generated

Any other fields in the user-detail document scheme MAY
be included.

Otherwise a 201 processing will be generated.



PUT user-details
----------------


A PUT request with a minimum document set out::

    {
	 "id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",
	 "identifiers": [
	     "http://openid.cnx.org/pbrian"
			],
	 "version": "0.0.1",
	 "name":{
		       "title": "Mr",
		       "firstname": "Paul",
		       "middlenames": "Richard",
		       "lastname":    "Brian",
		       "suffix":      "",
		       "fullname": "Paul Brian",
		       },
    }


All the fields sent in a PUT are replacing - they will completely replace
all other fields in the document.

It is an error not to supply at least one identifer and a valid, already existing
id. 

Any other fields in the user-detail document scheme MAY
be included, and will be overwritten.


Delete user detail
------------------

Not yet supported



Search
------

Single-term search in 0.0.1

An important part of user details is the search function.
We shall take the google-style approach::


    curl http://www.cnx.org/user/search?q=paul

    q -> query
    term -> all characters following q= will be assumed to 
            be a single search term across email, fullname fields

The results will be a JSON doc containing id, fullname, email and known identifers::
   
    {
    "id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
    "identifiers": [
        "https://www.google.com/accounts/o8/id?id=AItOawlc7oYk8MNlwBgxCwMhLDqzXq1BXA4abbk", 
        "http://openid.cnx.org/pbrian", 
        "paul@mikadosoftware.com"
    ], 
    "name": {"fullname": "Paul Brian"}
    }

Errors
------

A malformed query url will recv 422 error

