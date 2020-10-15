import os
from datetime import timedelta

# You need to replace the next values with the appropriate values for your configuration

class Config:

	DEBUG = True
	# SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

	basedir = os.path.abspath(os.path.dirname(__file__))
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = "mysql://root@localhost/url_short_db"

	# JWT_SECRET_KEY = "mysecretkey"
	# JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=480)

	# SOURCE_NAME    = ["quickinsure"]
