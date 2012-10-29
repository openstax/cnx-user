from rhaptos2.user import usermodel
import psycopg2
from nose import with_setup
import json

confd= {
 'bamboo_appnamespace': 'rhaptos2repo',
 'bamboo_archive_root': '/tmp/cnx/archive',
 'bamboo_code_root': '/home/pbrian/src/rhaptos2.repo',
 'bamboo_confdir': '/tmp/confdir',
 'bamboo_deployagent': 'deployagent',
 'bamboo_deployagent_keypath': '/home/pbrian/.ssh/deployagent',
 'bamboo_install_to': 'www.frozone.mikadosoftware.com::www.frozone.mikadosoftware.com',
 'bamboo_logserverfqdn': 'log.frozone.mikadosoftware.com',
 'bamboo_logserverport': '5147',
 'bamboo_modusdir': '/home/pbrian/src/bamboo.recipies/recipies/',
 'bamboo_remote_build_root': '/home/deployagent/',
 'bamboo_stage_root': '/tmp/cnx/stage/rhaptos2.repo',
 'bamboo_userserver': 'http://www.frozone.mikadosoftware.com:81/user',
 'bamboo_venvpath': '/tmp/cnx/venv/t1',
 'bamboo_www_server_root': '/usr/share/www/nginx/www',
 'bamboo_xunitfilepath': '/tmp/cnx/nosetests.xml',

 'rhaptos2user_cdn_server_name': 'localhost:5000',
 'rhaptos2user_loglevel': 'DEBUG',


 'rhaptos2user_pgdbname': 'repouser',
 'rhaptos2user_pghost': 'devlog.office.mikadosoftware.com',
 'rhaptos2user_pgpassword': 'pass1',
 'rhaptos2user_pgpoolsize': '5',
 'rhaptos2user_pgusername': 'repouser',
 'rhaptos2user_statsd_host': 'log.frozone.mikadosoftware.com',
 'rhaptos2user_statsd_port': '8125',
 'rhaptos2user_use_logging': 'Y',
 'rhaptos2user_www_server_name': 'localhost:5000'}


CONFD=confd


def clean_dbase():
    conn = psycopg2.connect("""dbname='%(rhaptos2user_pgdbname)s'\
                             user='%(rhaptos2user_pgusername)s' \
                             host='%(rhaptos2user_pghost)s' \
                             password='%(rhaptos2user_pgpassword)s'""" % CONFD);
    c = conn.cursor()
    c.execute("TRUNCATE TABLE public.identifier CASCADE;")
    conn.commit()
    c.execute("TRUNCATE TABLE public.user CASCADE;")
    conn.commit()
    conn.close()

def populate_dbase():
    """ """
    ben_dict = {"identifier": [{u'identifierstring': u'http://openid.cnx.org/user1',
                                u'identifiertype': u'openid',
                                u'user_id': u'org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383'}],

             "id": "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383", 
             "version": "1.0", 
             "firstname": "Benjamin", 
             "lastname" : "Franklin",
             "email"    : "ben@cnx.org"
             }

    u = usermodel.User()
    u = usermodel.populate_user(ben_dict, u)
    u.user_id = "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383"
    print "adding", u, u.firstname, u.user_id
    usermodel.UserSession.add(u)
    usermodel.UserSession.commit()
   

def setup():
    usermodel.init_mod(CONFD)     
    populate_dbase()
        
            
def teardown():
    clean_dbase() #### .. todo:: in setup / teardown use transactions and rollback please///


##################################

def test_DbaseIsUp():
    """ """
    conn = psycopg2.connect("""dbname='%(rhaptos2user_pgdbname)s'\
                             user='%(rhaptos2user_pgusername)s' \
                             host='%(rhaptos2user_pghost)s' \
                             password='%(rhaptos2user_pgpassword)s'""" % CONFD);
    c = conn.cursor()
    c.execute("Select 1;")
    rs = c.fetchall()
    assert rs[0] == (1,)



incomingd = {u'user_id': None,
 u'firstname': u'peter',
 u'identifier': [{u'identifierstring': u'x343435',
                  u'identifiertype': u'openid',
                  u'user_id': u'x3'}],
 u'lastname': u'meee',
 u'middlename': u'R'
 }

json_new_user = json.dumps(incomingd)


@with_setup(setup, teardown)
def test_connect2db():
    usermodel.post_user(None, json_new_user)
    

@with_setup(setup, teardown)
def test_retrieve_known_user_id():
    jsonstr = usermodel.get_user(None, "org.cnx.user.f9647df6-cc6e-4885-9b53-254aa55a3383")
    d = json.loads(jsonstr)
    assert d['lastname'] == 'Franklin'


@with_setup(setup, teardown)
def test_lastname_search():
    pass




#c.execute("SELECT * FROM public.module;")
#rs = c.fetchall()
#print rs

