import os
from os.path import abspath, dirname

DEBUG = True

APP_ROOT = abspath(dirname(__file__))

CDR_SERVICE_HOSTS = ("localhost", )
CDR_SOURCE_FOLDER = "/storage/switch_backups"

FILES = ("tar.bz2", "tar.gz")

if DEBUG:
    CDR_SERVICE_HOSTS = ("localhost",)
    CDR_SOURCE_FOLDER = os.path.join(APP_ROOT, "examples")

BAD_NUMBER_THRESHOLD = 50

UNBLOCK_CODES = ["200", "486"]  # have to be str
UNBLOCK_RING_TIME = 0  
UNBLOCK_DAY_RANGE = 10  # unblock when number is blocked over 10 days 

