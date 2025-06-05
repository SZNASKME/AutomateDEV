import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from io import StringIO
from utils.createFile import createExcel
from utils.readFile import loadJson
from utils.stbAPI import updateAuth, updateURI, updateAPIAuth, getAuditListAPI

EXCEL_NAME = 'Audit Case.xlsx'

audit_configs_temp = {
    
}




def getAudit():
    
    audit_configs = audit_configs_temp.copy()
    audit_configs['auditType'] = 9
    
    
    response = getAuditListAPI(audit_configs)
    if response.status_code == 200:
        print("Report generated successfully")
        data = response.json()
        
        
        return data
    else:
        print("Error generating report")
        return None
    
    
    
    
def main():
    auth = loadJson('Auth.json')
    #userpass = auth['TTB']
    userpass = auth['TTB_PROD']
    updateAPIAuth(userpass['API_KEY'])
    #updateAuth(userpass['USERNAME'], userpass['PASSWORD'])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['TTB_PROD']
    updateURI(domain)
    audit_list = getAudit()
    
    #filtered_df = df[df['Audit Type'] == 'User Login']
    print(audit_list)
    
    
    #createExcel(EXCEL_NAME, ('Audit Login', ))
    

if __name__ == '__main__':
    main()
    
    
## Get specific task report