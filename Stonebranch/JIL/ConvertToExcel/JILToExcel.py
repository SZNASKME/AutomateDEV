import sys
import os
import pandas as pd
import re
from datetime import datetime
from openpyxl import load_workbook

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.readExcel import getExcelProcess
from utils.readFile import readFolderTextFiles
from utils.createFile import createExcel


OUTPUT_PATH = "\\output\\"

JIL_FILENAME = "jobfile.txt"
STDCAL_FILENAME = "stdcal.txt"
EXTCAL_FILENAME = "extcal.txt"

JIL_EXCELNAME = "_JIL.xlsx"
STDCAL_EXCELNAME = "_stdcal.xlsx"
EXTCAL_EXCELNAME = "_extcal.xlsx"

JIL_SHEETNAME = "Sheet"
STDCAL_SHEETNAME = "Sheet"
EXTCAL_SHEETNAME = "Sheet"


jil_fieldnames = ["jobName","jobType","box_name","command","machine","owner","permission","date_conditions","days_of_week","start_times","start_mins","run_window","run_calendar","exclude_calendar","condition","alarm_if_fail","max_run_alarm","min_run_alarm","must_start_times","description","std_out_file","std_err_file","watch_file","watch_interval","watch_file_min_size","box_success","term_run_time","max_exit_success","box_terminator","job_terminator","group","application","send_notification","profile","job_load","n_retrys","envvars","timezone","elevated","resources","priority","notification_emailaddress","notification_msg","std_in_file","fail_codes","box_failure","interactive","job_class","success_codes","auto_hold","ulimit","ftp_local_name","ftp_local_name_1","ftp_remote_name","ftp_server_name","ftp_server_port","ftp_transfer_direction","ftp_transfer_type","ftp_use_ssl","ftp_user_type","sap_chain_id","sap_client","sap_job_count","sap_job_name","sap_lang","sap_mon_child","sap_office","sap_release_option","sap_rfc_dest","sap_step_parms","scp_local_name","scp_local_user","scp_protocol","scp_remote_dir","scp_remote_name","scp_server_name","scp_server_name_2","scp_server_port","scp_target_os","scp_transfer_direction"]

def readJILFile(jil_filepath):
    count =0
    jil_in_array = []
    print("Jobs Extracted")
    oneJob = {}
    with open(jil_filepath, "rt") as jil:
        jilLines = jil.readlines()
        for linesInJill in jilLines:
            if "insert_job:" in linesInJill:
                jil_in_array.append(oneJob)
                linesInJill = linesInJill.strip()
                jobName = re.findall(r'insert_job:(.*?)job_type:', linesInJill)[0]
                jobType = linesInJill.split("job_type:")[1]
                oneJob = {}
                oneJob["jobName"] = str(jobName).strip()
                oneJob["jobType"] = str(jobType).strip()
                count +=1
                print(f"{count}", end="\r")
            else:
                linesInJill = linesInJill.strip()
                if linesInJill != "\n" and "/* ----" not in linesInJill and linesInJill != "":
                    if "description:" in linesInJill:
                        spli = linesInJill.split("description:")
                        oneJob["description"] = str(spli[1]).replace("\"","")
                    elif "start_times" in linesInJill:
                        spli = linesInJill.split("start_times:")
                        oneJob["start_times"] = str(spli[1]).replace("\"","")
                    elif "command:" in linesInJill:
                        spli = linesInJill.split("command:")
                        oneJob["command"] = str(spli[1]).strip()               
                    else:
                        spli = linesInJill.split(":",1)
                        oneJob[str(spli[0]).strip()] = str(spli[1]).strip().replace("\"","")
        jil_in_array.append(oneJob)
        print(count)
    jil_in_array.pop(0)
    return jil_in_array


def customExcel(output_file_path):
    wb = load_workbook(output_file_path)
    ws = wb.active
    ws.column_dimensions["A"].width = 60
    ws.auto_filter.ref = ws.dimensions
    wb.save(output_file_path)
    print("Custom Edited Excel Successfully")

############################################################################################################
def stdcelParseData(lines):
    data = []
    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith("calendar:"):
            if current_entry:
                data.append(current_entry)
            current_entry = {'calendar': line.split(":")[1].strip()}
        else:
            date_str = line.replace(' 00:00', '')
            date_object = datetime.strptime(date_str, '%m/%d/%Y')
            if date_object.year >= 2022:
                current_entry.setdefault(f'Year_{date_object.year}', []).append(date_str)
    if current_entry:
        data.append(current_entry)
    return data

############################################################################################################
def extcelParseData(lines):
    data = []
    current_entry = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if key == 'extended_calendar':
            if current_entry:
                data.append(current_entry)
            current_entry = {'extended_calendar': value}
        else:
            current_entry[key] = value
    if current_entry:
        data.append(current_entry)
    return data




def main():
    current_path = os.path.dirname(__file__)
    folder_path = input("Enter the folder path: ")
    jil_except_path = input("Enter the jil except path ('n' -> skip): ")
    date_file_format = input("Enter the date file format: ")
    files = readFolderTextFiles(folder_path, STDCAL_FILENAME, EXTCAL_FILENAME)
    jil_path = folder_path + "\\"+ JIL_FILENAME
    jil_in_array = readJILFile(jil_path)
    if jil_except_path != 'n':
        df_jil_except = getExcelProcess(jil_except_path)
        jil_except_list = df_jil_except['jobName'].tolist()
        jil_in_array = [job for job in jil_in_array if job['jobName'] not in jil_except_list]
        
    stdcel_parsed_data = stdcelParseData(files[STDCAL_FILENAME])
    extcel_parsed_data = extcelParseData(files[EXTCAL_FILENAME])
    df_jil = pd.DataFrame(jil_in_array, columns = jil_fieldnames)
    df_stdcal = pd.DataFrame(stdcel_parsed_data)
    df_extcal = pd.DataFrame(extcel_parsed_data)
    jil_output_file = current_path + OUTPUT_PATH + date_file_format + JIL_EXCELNAME
    stdcal_output_file = current_path + OUTPUT_PATH + date_file_format + STDCAL_EXCELNAME
    extcal_output_file = current_path + OUTPUT_PATH + date_file_format + EXTCAL_EXCELNAME
    createExcel(jil_output_file, (JIL_SHEETNAME, df_jil))
    customExcel(jil_output_file)
    createExcel(stdcal_output_file, (STDCAL_SHEETNAME, df_stdcal))
    createExcel(extcal_output_file, (EXTCAL_SHEETNAME, df_extcal))
    
    
if __name__ == "__main__":
    main()
    