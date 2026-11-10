import os
import configparser

# read config.ini and keys.ini  from the same folder as this file, no matter where you run the program from
configPath = os.path.join(os.path.dirname(__file__), "config.ini")
keysPath = os.path.join(os.path.dirname(__file__), "keys.ini")

config = configparser.ConfigParser()
if not config.read(configPath):
    raise SystemExit("Can't find config.ini next to config.py (looked in " + path + ")")

keys = configparser.ConfigParser()
if not keys.read(keysPath):
    raise SystemExit("Can't find keys.ini next to config.py (looked in " + path + ")")

LATITUDE = float(keys["settings"]["lat"])
LONGITUDE = float(keys["settings"]["lon"])
#FEEDER_URL = settings["feeder"]["url"]
#NOTIFY_URL = settings["notify"]["url"]
#ROUTESET_URL = settings["routes"]["url"]
