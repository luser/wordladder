# A data store implemented with Berkeley DB.
# The only entry point is run_in_transaction, which
# you pass a function and optionally some arguments, and your
# function is called with the db as the first argument, and
# the rest of the arguments you passed after that.

import sys
import bsddb.db

try:
  from config import DATADIR
except ImportError:
  print >>sys.stderr, "You probably didn't copy config.py.dist to config.py and edit the settings correctly. Please do so."
  sys.exit(1)

class Rollback(Exception):
  pass

def run_in_transaction(func, *args, **kwargs):
  if "dbname" in kwargs:
    dbname = kwargs["dbname"]
  else:
    dbname = "game.db"
  dbe = bsddb.db.DBEnv()
  dbe.open(DATADIR, bsddb.db.DB_INIT_LOCK | bsddb.db.DB_CREATE | bsddb.db.DB_INIT_MPOOL | bsddb.db.DB_INIT_LOG | bsddb.db.DB_INIT_TXN)
  db = bsddb.db.DB(dbe)
  db.open(dbname, dbtype=bsddb.db.DB_BTREE, flags=bsddb.db.DB_CREATE)
  txn = dbe.txn_begin()
  commit = True
  try:
    result = func(db, *args)
  except Rollback:
    #XXX: should we handle other things here?
    commit = False
    result = None
  finally:
    if commit:
      txn.commit()
    else:
      txn.abort()
    db.close()
    dbe.close()
  return result
