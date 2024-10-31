import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateURI, updateAuth
from utils.readFile import loadJson
from utils.createFile import createJson, createExcel