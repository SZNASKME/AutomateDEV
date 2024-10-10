import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createJson, createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI



def choiceTemplate():
    choice_message = [
        "Check Parent",
        "Check Children All Level",
        "Check Children One Level"
    ]
    
    for index, message in enumerate(choice_message):
        print(f"{index+1}. {message}")
    
    
    choice = input("Enter your choice: ")
    return choice




def main():
    auth = loadJson('Auth.json')
    userpass = auth['TTB']
    #userpass = auth['ASKME_STB']
    updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain = "https://ttbdevstb.stonebranch.cloud/resources"
    #domain = 'http://172.16.1.86:8080/uc/resources'
    updateURI(domain)
    choice = choiceTemplate()
    
if __name__ == '__main__':
    main()