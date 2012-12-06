============
User details
============

a user-details-doc is a JSON formatted document containing 
all relevant known details about a Connexions user.

It is supplied to any component of the system which needs
user details, and is served over a RESTful API over HTTP.



::

    Python:

        user = {
        "user_id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",
        "title": "Mr",
	"firstname": "Paul",
	"middlenames": "Richard",
	"lastname":    "Brian",
	"suffix":      "",
	"fullname": "Paul Brian",

        "email":   "paul@mikadosoftware.com",
        "homepage":  "www.mikadosoftware.com",
 
       "affiliation-institution": "Rice University",
       "affiliation-institution_url": "www.rice.edu"
       "preferredlang":  "English",
       "otherlangs"   :  "BadEnglish",
       "location"     :  "UK",
       "interests"    :  "ridin",
       "recommendations": [],
       "biography"    :  "I was born at a very early age.",
       "imageurl"        : "www.cnx.org/userimages/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383",

        "identifiers": ["http://openid.cnx.org/pbrian",
                        "paul@mikadosoftware.com"],
        "version": "0.0.1"
        }



       print json.dumps(user, sort_keys=True, indent=4)

As JSON::

 {
    "affiliation-institution": "Rice University", 
    "affiliation-institution_url": "www.rice.edu", 
    "biography": "I was born at a very early age.", 
    "email": "paul@mikadosoftware.com", 
    "firstname": "Paul", 
    "fullname": "Paul Brian", 
    "homepage": "www.mikadosoftware.com", 
    "identifiers": [
        "http://openid.cnx.org/pbrian", 
        "paul@mikadosoftware.com"
    ], 
    "imageurl": "www.cnx.org/userimages/org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
    "interests": "ridin and shootin", 
    "lastname": "Brian", 
    "location": "UK", 
    "middlenames": "Richard", 
    "otherlangs": "BadEnglish", 
    "preferredlang": "English", 
    "recommendations": [], 
    "suffix": "", 
    "title": "Mr", 
    "user_id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
    "version": "0.0.1"
 }


Due to limitations with the current SQLAlchemy model, I have limited the number of x:m realationships in the profile to the one most important - identifiers.
