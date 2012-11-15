=============
rhaptos2.user
=============

Installation:

1. create a clean venv and populate from requirements.txt

   virtualenv ~/venvs/foobar -r rhaptos2.user/requirements.txt

2. run setup.py develop against common and user

   . bin/activate
   cd rhaptos2.common
   python setup.py develop

   cd rhaptos2.user
   python setup.py develop

3. cd rhaptos2.user/rhaptos/user
   python run.py --debug --config=../../local.ini

4. adjust local.ini as needed, the defaults give you access to a
   postgresdbase now. (Yea security !)


5. You should be able to successfully 

   http://localhost:5000 - hello world
   http://localhost:5000/users/ - json list of dbase (max 25, solely for dev)
   http://localhost:5000/user/?user=org.cnx.user-80eeb317-2bb9-4230-8f1f-d62509d2bf4f
   (adjust thsi last one with uuid from above)


6. Also note shell.py will give you a command line to dbase for testing usermodel

::



    (vuser)user(convert2newconf)$ python -i shell.py 
    Connecting to Database:
    www.frozone.mikadosoftware.com
    You are now in shell, without access to Flask App, but with dbase
    You may want to review prepopulate.py for notes on prepopulating the dbase during development
    >>> q = db_session.query(usermodel.User)
    >>> q.all()
    [<rhaptos2.user.usermodel.User object at 0x807476950>]
    >>> 


Notes to be tidied up later::

 You will need a SSL-enabled IP based access to a postgresql server (9.1 tested, a bit)
 Add user conneciton string details to local.ini

 notes for setting postgres::


    create user test1 with password 'xxx';
    create database dbtest;
    GRANT ALL PRIVILEGES ON dbtest to usertest;

    pg_hba.conf - set addresses for md5 to all
    postgres,conf - set listenaddresses to all, use SSL and password encryption on
    sudo service postgresql restart

    test access from psql -d dbtest -U usertest -h www.frozone.mikadosoftware.com


 First steps:

 1. enter the venv and 

    python -i shell.py

 This should instantiate the database and store one user in the dbase
 This is a genuine openid (I'll add them a persona soon) - so you can authenticate 
 against them, password is pass1 (I think)

 2. Now try running the app as above



