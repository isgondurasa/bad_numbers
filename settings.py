import os
from os.path import abspath, dirname, join

DEBUG = False

PORT = "9090"

APP_ROOT = abspath(dirname(__file__))

CDR_SERVICE_HOSTS = ("138.201.126.113", )
USERNAME = "andrey"
PASSWORD = "6hfv6EEW"
CDR_SOURCE_FOLDER = "/storage/switch_backups"

LOCAL_FILE_FOLDER = join(APP_ROOT, "tmp")

FILES = ("tar.bz2", "tar.gz", "")

if DEBUG:
    CDR_SERVICE_HOSTS = ("localhost",)
    CDR_SOURCE_FOLDER = os.path.join(APP_ROOT, "examples")

BAD_NUMBER_THRESHOLD = 50

UNBLOCK_CODES = ["200", "486"]  # have to be str
UNBLOCK_RING_TIME = 0
UNBLOCK_DAY_RANGE = 10  # unblock when number is blocked over 10 days

DB_CONNECTION = {
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "185.143.173.48",
    "database": "bad_numbers"
}
