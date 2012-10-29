

from rhaptos2.user import backend, usermodel

shell_conf = { 'rhaptos2user_pgdbname': 'repouser',
 'rhaptos2user_pghost': 'devlog.office.mikadosoftware.com',
 'rhaptos2user_pgpassword': 'pass1',
 'rhaptos2user_pgpoolsize': '5',
 'rhaptos2user_pgusername': 'repouser'}

import test_db
test_db.clean_dbase()
usermodel.init_mod(test_db.CONFD)
print usermodel.UserSession
test_db.populate_dbase()

print "You are now in shall, without access to Flask APp, bnut with dbase"

