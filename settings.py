import os
from os.path import abspath, dirname, join

DEBUG = True

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
    "host": "192.168.99.100", #"185.143.173.48", #138.201.126.113
    "database": "bad_numbers"
}

# DB_CONNECTION = {
#     "user": "user_bad_numbers",
#     "password": "QAZxsw321",
#     "host": "209.126.127.64",
#     "database": "bad_numbers"
# }

