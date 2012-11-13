=============
rhaptos2.user
=============

install and run

use buildvenv.sh from bamboo.scaffold/bamboo/scaffold/scripts to create
an virtualenv suitable for running this package.

THen activate the venv and 

  cd rhaptos2.user/rhaptos2/user
  python run.py --debug --conf=../../local.ini

Adjust local.ini as needed.

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

3. You should be able to successfully 

   http://localhost:5000 - hello world
   http://localhost:5000/users/ - json list of dbase (max 25, solely for dev)
   http://localhost:5000/user/?user=org.cnx.user-80eeb317-2bb9-4230-8f1f-d62509d2bf4f
   (adjust thsi last one with uuid from above)




