"""/**
 * @author [Harshit Singh]
 * @Github [https://github.com/harshit740]
 * @create date 2021-03-03 12:39:36
 * @modify date 2021-03-03 12:39:36
 * @desc [Converting Autosys Jil Dump to Excel  Using Openpyxl]
 */"""

import os
import sys
from openpyxl import Workbook, load_workbook
import re

print("Jil to Excel")
jilFileName = ""
if len(sys.argv) < 2:
    print("No Arguments provided the jilfilename eg jil2db.py filename outputfilenameoptional without extension")
    exit(0)
else:
    jilFileName = sys.argv[1]

count =0
jilinArray = []
print("Jobs Extracted")
oneJob = {}
with open(jilFileName, "rt") as jil:
    jilLines = jil.readlines()
    for linesInJill in jilLines:
        if "insert_job:" in linesInJill:
            jilinArray.append(oneJob)
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
    jilinArray.append(oneJob)
    print(count)

"""with open("JilTestDump.txt", "wt") as newJil:
    for ar in jilinArray:
        for a in ar:
            if "jobName" in a:
                newJil.write("\n \n /* -----------------"+ar[a]+"----------------- */ \n \n")
            newJil.write(a+": "+ar[a]+"\n")"""
            
#fieldnames = ["jobName","start_times","run_calendar","exclude_calendar","days_of_week"]
#fieldnames = ["jobName","jobType","command","box_name","machine","owner","sap_chain_id","sap_client","sap_job_count","sap_job_name","sap_lang","sap_mon_child","sap_office","sap_release_option","sap_rfc_dest","sap_step_parms","days_of_week","run_calendar","exclude_calendar","owner","condition","start_times","start_mins","alarm_if_fail","max_run_alarm","description"]
fieldnames = ["jobName","jobType","box_name","command","machine","owner","permission","date_conditions","days_of_week","start_times","start_mins","run_window","run_calendar","exclude_calendar","condition","alarm_if_fail","max_run_alarm","min_run_alarm","must_start_times","description","std_out_file","std_err_file","watch_file","watch_interval","watch_file_min_size","box_success","term_run_time","max_exit_success","box_terminator","job_terminator","group","application","send_notification","profile","job_load","n_retrys","envvars","timezone","elevated","resources","priority","notification_emailaddress","notification_msg","std_in_file","fail_codes","box_failure","interactive","job_class","success_codes","auto_hold","ulimit","ftp_local_name","ftp_local_name_1","ftp_remote_name","ftp_server_name","ftp_server_port","ftp_transfer_direction","ftp_transfer_type","ftp_use_ssl","ftp_user_type","sap_chain_id","sap_client","sap_job_count","sap_job_name","sap_lang","sap_mon_child","sap_office","sap_release_option","sap_rfc_dest","sap_step_parms","scp_local_name","scp_local_user","scp_protocol","scp_remote_dir","scp_remote_name","scp_server_name","scp_server_name_2","scp_server_port","scp_target_os","scp_transfer_direction"]


print("Inserting Jobs to Excel selected Fields are \n")
print(fieldnames)
print("Number Of jobs Processod")
count = 0
wb = Workbook()
ws = wb.active
ws.append(fieldnames)
jilinArray.pop(0)
for ar in jilinArray:
    print(f"{count}", end="\r")
    values = []
    for k in fieldnames:
        if k in ar:
            values.append(ar[k])
        else:
            values.append(None)
    ws.append(values)
    count +=1

#for column_cells in ws.columns:
 #   length = max(len(str(cell.value)) for cell in column_cells)
  #  ws.column_dimensions[column_cells[0].column_letter].width = length
del jilinArray ,jilLines,

ws.column_dimensions["A"].width = 60
ws.auto_filter.ref = ws.dimensions
if len(sys.argv) >= 3:
    print("File Name Was Provided"+sys.argv[2])
    wb.save(sys.argv[2]+".xlsx")
else:
    print("File Name Was not provided using jil file name \t"+jilFileName)
    filename = jilFileName.split(".")[0] +".xlsx"
    wb.save(filename)
print("Excel File is Saved Job Completed ")
