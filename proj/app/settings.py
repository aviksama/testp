"""
the module is used for all global and app specific settings like database connection and defining constants
constants declared in the module are in uppercase
settings declared in global_scope are also imported for convention
it is important to set `server_timezone` as per the actual server's timezone to avoid discrepancies you may not be
        required to declare the variable if the server is running on UTC timezone.
"""
from __future__ import unicode_literals
import os
import base64
import pymongo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


environ = os.environ
# ##### encryptions #####
X_SECRET_KEY = base64.b64decode(environ.get('INTERNAL_SALT', 'gcX2U6spLYas'))  # Password and TOTP Hashing
X_AES_KEY = base64.b64decode(environ.get('INTERNAL_AES_KEY', 'brWgC69fBXguWRm+vc6o1wru5tiR8sBQVVbMMrb8o8A='))
X_SEPERATOR = '--sep--'
AES_KEY = base64.b64decode(environ.get('AES_KEY', '+Do7ww7gessUV3h0yUAqAFZ2nU8htQcXXPPh9GgSM8U='))
SHARED_SALT = base64.b64decode(environ.get('SHARED_SALT', 'xB0GDEzZTlU='))

MUSER = os.environ.get('MDBUSER', '')
MPASS = os.environ.get('MDBPASS', '')

client = pymongo.MongoClient(f"mongodb+srv://{MUSER}:{MPASS}@cluster0.yvdzf.mongodb.net/DB?retryWrites=true&w=majority")
db = client.DB

PGUSER = os.environ.get('PGUSER', '')
PGPASS = os.environ.get('PGPASS', '')
engine = create_engine(f'postgresql+psycopg2://{PGUSER}:{PGPASS}@localhost/testp')
Session = sessionmaker(bind=engine)