import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.stbAPI import updateURI, updateAuth
from utils.createFile import updatePath


def updateTargetAPI(target_data):
    userpass = target_data['AUTH']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = target_data['DOMAIN']
    updateURI(domain_url)
    
    
def updateTargetFile(target_path):
    updatePath(target_path)