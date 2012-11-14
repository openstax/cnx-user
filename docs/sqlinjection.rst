============================
SQL Injection and SQLAlchemy
============================

Or, Ross, stop scaring me like that.
====================================

THe following line is used in a search function in the user database::

    q = q.filter(User.fullname.like("%%%s%%" % namefrag))

This wraps "%" around a variable, and passes it as the "LIKE" term to a database.
There is, quite rightly, concern that this may be a vector for SQL Injection.

However, SQLAlchemy is designed to help avoid these issues, and as such it passes the 
LIKE term not as part of a string but as a bindparam (escaped 


WOrked Example
--------------

Firstly, we use `Little Bobby Tables <http://http://xkcd.com/327/>`_ to force a likely error:: 

    >>> x = q.filter(usermodel.User.fullname.like("%user%'; DROP TABLE identifier;"))
    >>> rs = x.all()

echo from SA::

    INFO:sqlalchemy.engine.base.Engine:SELECT cnxuser.user_id AS
    ...
    FROM cnxuser 
    WHERE cnxuser.fullname LIKE %(fullname_1)s
    2012-11-14 13:14:35,954 INFO sqlalchemy.engine.base.Engine {'fullname_1': "%user%'; DROP TABLE identifier;"}

  
postgresql log::

    mail, cnxuser.version AS cnxuser_version 
    FROM cnxuser 
    WHERE cnxuser.fullname LIKE '%user%''; DROP TABLE identifier;'
                                       ^^^

Summary
-------

Whilst I have no claim to infallibility here, and will happily defer
to more knowledgeable tests, I beleive the above demonstrates the
basic SA approach - the python functions generate prepared statements
that always follow sensible excaping rules - the SQL injection line
that in a string formatting approach would have resulted in a
vulnerability results in a properly excaped and quoted line, that will
never match a real user.

I would be tempted to use the sanitise SQL function as a security
alert.


Setting up logging etc
======================


SA::

    echo=True at engine creation point


    import logging
    logging.basicConfig(filename='/tmp/db.log')
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


postgresql::


    postgresql.conf changes:


    log_collector="on"
    log_location="/path/dir"
    log_statements="all"


