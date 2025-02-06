import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.stbAPI import updateURI, updateAuth, updateTaskAPI, getTaskAPI
from utils.readFile import loadJson
from utils.createFile import createJson
from utils.readExcel import getDataExcel
from utils.createFile import createExcel










def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    domain = domain_url['1.161']
    updateURI(domain)
    
    df_job_new = getDataExcel('Get New Task from Excel')

    