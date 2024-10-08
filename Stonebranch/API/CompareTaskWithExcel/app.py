import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createExcel import createExcel
from utils.createFile import createJson
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI



def choiceTemplate():
    print("1. Check Parent")
    




def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    #domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    
    df = getDataExcel()
    
    
    
    
    
if __name__ == '__main__':
    main()