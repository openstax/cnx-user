
from testconfig import config
import psycopg2
import datetime
from rhaptos2.user.backend import db_session

"""

this is
for setup and teardown features for the testing (and prepopulation)
of rhaptos2.user

We need to teardown the backend portion each time - else we find 
we are hanging onto connections we should not.  THe pooling does not 
work if we do not end the session.

"""

############### admin tools for nose
def setup():
    clean_dbase() 
    populate_dbase()
            
def teardown():
    """
    """
    db_session.remove()

def get_conn(config):
        
    conn = psycopg2.connect("""dbname='%(pgdbname)s'\
                             user='%(pgusername)s' \
                             host='%(pghost)s' \
                             password='%(pgpassword)s'""" % config['app']);
    return conn    

def clean_dbase():
    conn = get_conn(config)
    c = conn.cursor()
    c.execute("TRUNCATE TABLE public.cnxidentifier CASCADE;")
    conn.commit()
    c.execute("TRUNCATE TABLE public.cnxuser CASCADE;")
    conn.commit()
    conn.close()



def populate_dbase():
    """SHould be usermodel agnostic """

    mkuser("https://paulbrian.myopenid.com",
            "Paul Brian", "org.cnx.user-75e06194-baee-4395-8e1a-566b656f6920")
    mkuser("https://rossreedstrom.myopenid.com",
            "Ross Reedstrom1", "org.cnx.user-d5a29da4-652f-430a-8137-76dd7f00f213")
    mkuser("https://edwoodward.myopenid.com",
            "Ed Woodward", "org.cnx.user-41db63c4-2452-4b7c-9c63-1942ad321113")
    mkuser("https://philschatz.myopenid.com",
            "Phil Schatz", "org.cnx.user-1adf9d40-ad86-4432-a9e9-d74436235c42")
    mkuser("https://michaelmulich.myopenid.com",
            "Michael Mulich", "org.cnx.user-a5e5680e-bfa8-407d-a870-61ba45683261")
    
    
def mkuser(openidstr, fullname, user_id):
    """ """

    user_sql = """INSERT INTO cnxuser 
                  (user_id, title, firstname, middlename, 
                   lastname, suffix, fullname, interests, 
                   affiliationinstitution_url, affiliationinstitution, 
                   preferredlang, otherlangs, imageurl, 
                   location, biography, recommendations, 
                   homepage, email, version) VALUES 
                   (%(user_id)s, %(title)s, %(firstname)s, 
                    %(middlename)s, %(lastname)s, %(suffix)s, 
                    %(fullname)s, %(interests)s, %(affiliationinstitution_url)s,
                    %(affiliationinstitution)s, %(preferredlang)s, 
                    %(otherlangs)s, %(imageurl)s, %(location)s, 
                    %(biography)s, %(recommendations)s, %(homepage)s, 
                    %(email)s, %(version)s)"""

    dt = datetime.datetime.today().isoformat()

    user_dict =  {'interests': None, 'user_id': user_id, 'suffix': None, 
                  'firstname': None, 'otherlangs': None, 'middlename': None, 
                  'lastname': None, 'imageurl': None, 'title': None, 
                  'affiliationinstitution_url': None, 'fullname': fullname, 
                  'version': None, 'location': None, 'recommendations': None, 
                  'preferredlang': None, 'affiliationinstitution': None, 
                  'homepage': None, 'email': None, 'biography': dt}


    id_sql= """INSERT INTO cnxidentifier (identifierstring, 
                                           identifiertype, 
                                           user_id) VALUES 
                          (%(identifierstring)s, 
                           %(identifiertype)s, %(user_id)s)"""

    id_dict = {'identifierstring': openidstr, 
               'user_id': user_id, 
               'identifiertype': 'openid'}
    ### now execute the above in a TRANS
    conn = get_conn(config)
    c = conn.cursor()
    c.execute(user_sql, user_dict)
    c.execute(id_sql, id_dict)
    conn.commit()
    conn.close()
