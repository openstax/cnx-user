============
User details
============

a user-details-doc is a JSON formatted document containing 
all relevant known details about a Connexions user.

It is supplied to any component of the system which needs
user details, and is served over a RESTful API over HTTP.

 




::

    Python:

        user = {"id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",
        
        "name":{
                   "title": "Mr",
                   "firstname": "Paul",
                   "middlenames": "Richard",
                   "lastname":    "Brian",
                   "suffix":      "",
                   "fullname": "Paul Brian",
                },
         "contact":{ 
                   "email":   "paul@mikadosoftware.com",
                   "homepage":  "www.mikadosoftware.com",
                  },
         "background":{
                      "affiliations": [{"institution": "Rice University",
                                        "institution_url": "www.rice.edu"
                                        },
                                       {"institution": "School Of Hard Knocks",
                                        "institution_url": "www.allover.com"
                                        },
                                       ],
                      "preferredlang":  "English",
                      "otherlangs"   :  ["BadEnglish",  "DrunkenEnglish"],
                      "location"     :  "UK",
                      "interests"    :  ["ridin", "shootin", "fishin"],
                      "recommendations": [],
                      "biography"    :  "I was born at a very early age.",
                      "imageurl"        : "www.cnx.org/userimages/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",
                      

         }

        "identifiers": ["https://www.google.com/accounts/o8/id?id=AItOawlc7oYk8MNlwBgxCwMhLDqzXq1BXA4abbk",                    "http://openid.cnx.org/pbrian",
                        "paul@mikadosoftware.com"],
        "version": "0.0.1"
        }



       print json.dumps(user, sort_keys=True, indent=4)

As JSON::

    {
	"background": {
	    "affiliations": [
		{
		    "institution": "Rice University", 
		    "institution_url": "www.rice.edu"
		}, 
		{
		    "institution": "School Of Hard Knocks", 
		    "institution_url": "www.allover.com"
		}
	    ], 
	    "biography": "I was born at a very early age.", 
	    "imageurl": "www.cnx.org/userimages/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
	    "interests": [
		"ridin", 
		"shootin", 
		"fishin"
	    ], 
	    "location": "UK", 
	    "otherlangs": [
		"BadEnglish", 
		"DrunkenEnglish"
	    ], 
	    "preferredlang": "English", 
	    "recommendations": []
	}, 
	"contact": {
	    "email": "paul@mikadosoftware.com", 
	    "homepage": "www.mikadosoftware.com"
	}, 
	"id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
	"identifiers": [
	    "https://www.google.com/accounts/o8/id?id=AItOawlc7oYk8MNlwBgxCwMhLDqzXq1BXA4abbk", 
	    "http://openid.cnx.org/pbrian", 
	    "paul@mikadosoftware.com"
	], 
	"name": {
	    "firstname": "Paul", 
	    "fullname": "Paul Brian", 
	    "lastname": "Brian", 
	    "middlenames": "Richard", 
	    "suffix": "", 
	    "title": "Mr"
	}, 
	"version": "0.0.1"
    }
