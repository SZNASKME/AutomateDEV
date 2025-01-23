import sys
import os
import json
import pandas as pd
import xmltodict


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.stbAPI import updateURI, updateAuth, runReportAPI
from utils.readFile import loadJson
from utils.createFile import prepareOutputFile



run_report_temp = {
    "reporttitle": None,
    "visibility": None,
}

def getForecastReport(format_str):
    run_report = run_report_temp.copy()
    run_report["reporttitle"] = "Forecast"
    run_report["visibility"] = "Me"
    response = runReportAPI(run_report, format_str = format_str)
    if response.status_code == 200:
        return response
    else:
        return None


def choiceTemplate():
    while True:
        print("Forecast Report : Select the output format")
        print("1. CSV")
        print("2. JSON")
        print("3. XML")
        input_choice = input("Enter your choice: ")
        if input_choice in ["1", "2", "3"]:
            return input_choice
        else:
            print("Invalid input. Please try again.")
            continue


def getChoice(input_choice):
    if input_choice == "1":
        return "csv"
    elif input_choice == "2":
        return "json"
    elif input_choice == "3":
        return "xml"
    else:
        return None



            
def main():
    auth = loadJson('auth.json')
    userpass = auth['ASKME_STB']
    updateAuth(userpass["USERNAME"], userpass["PASSWORD"])
    domain_url = loadJson('Domain.json')
    #domain = domain_url['TTB_UAT']
    domain = domain_url['1.86']
    updateURI(domain)
    input_choice = choiceTemplate()
    format_str = getChoice(input_choice)
    forecast_report = getForecastReport(format_str)
    prepareOutputFile(forecast_report,"forecast_report", format_str, "Forecast Report")
    
    
if __name__ == '__main__':
    main()