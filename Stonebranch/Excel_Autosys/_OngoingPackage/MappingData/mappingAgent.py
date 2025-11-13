import sys
import os
import json
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.readExcel import getDataExcel
from utils.createFile import createExcel, createJson

OUTPUT_EXCEL_NAME = 'Machine-Job Mapping.xlsx'
OUTPUT_MACHINE_SHEETNAME = 'Machine-Job Summary'
OUTPUT_MAIN_BOX_SHEETNAME = 'Main Box Summary'
OUTPUT_RESULT_SHEETNAME = 'Machine Result'
OUTPUT_SHEETNAME_LOG = 'Machine-Job Log'

JOBNAME_COLUMN = 'jobName'
BOXNAME_COLUMN = 'box_name'
JOBTYPE_COLUMN = 'jobType'
MAINBOX_COLUMN = 'Main_Box'
MACHINE_COLUMN = 'machine'
OWNER_COLUMN = 'owner'


sys.setrecursionlimit(10000)


def findingmachineAndJob(df):
    main_box_analysis_result_list = []
    machine_analysis_result_list = []
    machine_job_result_list = []
    machine_job_log_list = []
    
    main_box_machine_dict = {}
    machine_main_box_dict = {}
    #print(df.columns)
    for row in df.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        main_box = getattr(row, MAINBOX_COLUMN)
        machine = getattr(row, MACHINE_COLUMN)
        owner = getattr(row, OWNER_COLUMN)

        if job_type == 'BOX':
            continue
        
        # Handle Self Start mainbox
        if main_box == '*Self Start' or main_box == 'Self Start':
            main_box = '*' + job_name
        
        if machine is None or pd.isna(machine) or machine == '':
            machine = 'No Machine Assigned'
        main_box_machine_dict.setdefault(main_box, {})
        main_box_machine_dict[main_box].setdefault(machine, [])
        main_box_machine_dict[main_box][machine].append((job_name, box_name, job_type, owner))
        
        machine_main_box_dict.setdefault(machine, {})
        machine_main_box_dict[machine].setdefault(main_box, [])
        machine_main_box_dict[machine][main_box].append((job_name, box_name, job_type, owner))


    for key, value in main_box_machine_dict.items():
        main_box = key
        
        main_box_analysis_result_list.append({
            'Main Box': main_box,
            'Count of Machines': len(value),
            'Total Count of Jobs': sum(len(details) for details in value.values()),
            'Machines': ', '.join(value.keys()),
        })
        
        for machine, details in value.items():
            if machine is None or pd.isna(machine) or machine == '':
                machine = 'No Machine Assigned'
            
            machine_job_result_list.append({
                'Machine': machine,
                'Main Box': main_box,
                'Count of Jobs': len(details),
            })
            for detail in details:
                job_name, box_name, job_type, owner = detail
                machine_job_log_list.append({
                    'Machine': machine,
                    'Main Box': main_box,
                    'Box Name': box_name,
                    'Job Name': job_name,
                    'Job Type': job_type,
                    'Owner': owner,
                })
                
    for key, value in machine_main_box_dict.items():
        machine = key
        
        machine_analysis_result_list.append({
            'Machine': machine,
            'Count of Main Boxes': len(value),
            'Total Count of Jobs': sum(len(details) for details in value.values()),
            'Main Boxes': ', '.join(value.keys()),
        })
        
        
        
    df_machine_analysis_result = pd.DataFrame(machine_analysis_result_list)
    df_main_box_analysis_result = pd.DataFrame(main_box_analysis_result_list)
    df_machine_job_result = pd.DataFrame(machine_job_result_list)
    df_machine_job_log = pd.DataFrame(machine_job_log_list)

    return df_machine_analysis_result, df_main_box_analysis_result, df_machine_job_result, df_machine_job_log


def createDeploymentSets(df):
    """
    Create deployment sets ensuring all jobs in a mainbox have their machines deployed together
    or already deployed in previous sets.
    """
    deployment_sets = []
    deployed_jobs = set()
    deployed_machines = set()
    
    # Build dictionaries for analysis
    main_box_machine_dict = {}
    machine_main_box_dict = {}
    job_details_dict = {}
    main_box_jobs_dict = {}
    box_jobs_dict = {}  # เก็บ BOX jobs แยกต่างต่าง
    
    for row in df.itertuples(index=False):
        job_name = getattr(row, JOBNAME_COLUMN)
        job_type = getattr(row, JOBTYPE_COLUMN)
        box_name = getattr(row, BOXNAME_COLUMN)
        main_box = getattr(row, MAINBOX_COLUMN)
        machine = getattr(row, MACHINE_COLUMN)
        owner = getattr(row, OWNER_COLUMN)

        # Handle Self Start mainbox
        if main_box == '*Self Start' or main_box == 'Self Start':
            main_box = job_name
            
        # Store job details for all jobs (including BOX)
        job_details_dict[job_name] = {
            'job_name': job_name,
            'job_type': job_type,
            'box_name': box_name,
            'main_box': main_box,
            'machine': machine if pd.notna(machine) and machine != '' else 'No Machine Assigned',
            'owner': owner
        }
        
        # BOX jobs ไม่มี machine - เก็บแยกต่างหาก
        if job_type == 'BOX':
            box_jobs_dict.setdefault(main_box, []).append(job_name)
            continue
        
        # สำหรับ non-BOX jobs เท่านั้น
        if machine is None or pd.isna(machine) or machine == '':
            machine = 'No Machine Assigned'
        
        # Build mapping dictionaries (เฉพาะ non-BOX jobs)
        main_box_machine_dict.setdefault(main_box, set()).add(machine)
        machine_main_box_dict.setdefault(machine, set()).add(main_box)
        main_box_jobs_dict.setdefault(main_box, []).append(job_name)
    
    def canDeployMainBox(main_box, additional_machines=set()):
        """Check if all machines required by main_box are available"""
        if main_box not in main_box_machine_dict:
            return True  # BOX-only mainbox can always be deployed
        required_machines = main_box_machine_dict[main_box]
        all_available_machines = deployed_machines.union(additional_machines)
        return required_machines.issubset(all_available_machines)
    
    def getUndeployedMainBoxes():
        """Get main boxes that still have undeployed jobs"""
        undeployed = []
        # Check non-BOX jobs
        for main_box in main_box_machine_dict.keys():
            undeployed_jobs = [job_name for job_name in main_box_jobs_dict.get(main_box, []) 
                             if job_name not in deployed_jobs]
            if undeployed_jobs:
                undeployed.append(main_box)
        
        # Check BOX-only mainboxes
        for main_box in box_jobs_dict.keys():
            if main_box not in main_box_machine_dict:  # BOX-only mainbox
                undeployed_box_jobs = [job_name for job_name in box_jobs_dict[main_box] 
                                     if job_name not in deployed_jobs]
                if undeployed_box_jobs:
                    undeployed.append(main_box)
        
        return undeployed
    
    def getJobsInMainBox(main_box):
        """Get all jobs (including BOX) in a mainbox"""
        jobs = []
        # Add non-BOX jobs
        for job_name in main_box_jobs_dict.get(main_box, []):
            if job_name not in deployed_jobs:
                jobs.append(job_details_dict[job_name])
        
        # Add BOX jobs
        for job_name in box_jobs_dict.get(main_box, []):
            if job_name not in deployed_jobs:
                jobs.append(job_details_dict[job_name])
        
        return jobs
    
    set_number = 1
    
    # Phase 1: Deploy 1 machine with all related mainboxes that use only this machine
    single_machine_candidates = []
    
    for machine, related_mainboxes in machine_main_box_dict.items():
        all_mainboxes_use_only_this_machine = True
        for main_box in related_mainboxes:
            if len(main_box_machine_dict[main_box]) > 1:
                all_mainboxes_use_only_this_machine = False
                break
        
        if all_mainboxes_use_only_this_machine:
            single_machine_candidates.append((machine, related_mainboxes))
    
    # Deploy single machine candidates
    for machine, related_mainboxes in single_machine_candidates:
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box in related_mainboxes:
            jobs_in_mainbox = getJobsInMainBox(main_box)
            
            if jobs_in_mainbox:
                current_set_jobs.extend(jobs_in_mainbox)
                current_set_mainboxes.append(main_box)
        
        if current_set_jobs:
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': f'Single Machine ({len(current_set_mainboxes)} MainBoxes)',
                'main_boxes': current_set_mainboxes,
                'machines': [machine],
                'new_machines': [machine],
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            deployed_machines.add(machine)
            set_number += 1
    
    # Phase 2: Deploy mainboxes with zero new machines
    while True:
        undeployed_mainboxes = getUndeployedMainBoxes()
        if not undeployed_mainboxes:
            break
            
        zero_new_machine_candidates = []
        for main_box in undeployed_mainboxes:
            if canDeployMainBox(main_box):
                machine_count = len(main_box_machine_dict.get(main_box, set()))
                zero_new_machine_candidates.append((main_box, machine_count))
        
        if not zero_new_machine_candidates:
            break
        
        zero_new_machine_candidates.sort(key=lambda x: x[1])
        
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box, machine_count in zero_new_machine_candidates:
            jobs_in_mainbox = getJobsInMainBox(main_box)
            
            if jobs_in_mainbox:
                current_set_jobs.extend(jobs_in_mainbox)
                current_set_mainboxes.append(main_box)
        
        if current_set_jobs:
            all_machines_in_set = set()
            for main_box in current_set_mainboxes:
                if main_box in main_box_machine_dict:
                    all_machines_in_set.update(main_box_machine_dict[main_box])
            
            machine_counts = [len(main_box_machine_dict.get(mb, set())) for mb in current_set_mainboxes]
            min_machines = min(machine_counts) if machine_counts else 0
            max_machines = max(machine_counts) if machine_counts else 0
            
            if min_machines == max_machines:
                deploy_type = f'Zero New Machines - {min_machines} Machine MainBoxes ({len(current_set_mainboxes)} boxes)'
            else:
                deploy_type = f'Zero New Machines - {min_machines}-{max_machines} Machine MainBoxes ({len(current_set_mainboxes)} boxes)'
            
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': deploy_type,
                'main_boxes': current_set_mainboxes,
                'machines': list(all_machines_in_set),
                'new_machines': [],
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            set_number += 1
        else:
            break
    
    # Phase 3: Add one new machine at a time
    while True:
        undeployed_mainboxes = getUndeployedMainBoxes()
        if not undeployed_mainboxes:
            break
        
        # Filter out BOX-only mainboxes for machine-based deployment
        machine_based_mainboxes = [mb for mb in undeployed_mainboxes if mb in main_box_machine_dict]
        
        if not machine_based_mainboxes:
            # Handle remaining BOX-only mainboxes
            box_only_mainboxes = [mb for mb in undeployed_mainboxes if mb not in main_box_machine_dict]
            if box_only_mainboxes:
                current_set_jobs = []
                current_set_mainboxes = []
                
                for main_box in box_only_mainboxes:
                    jobs_in_mainbox = getJobsInMainBox(main_box)
                    if jobs_in_mainbox:
                        current_set_jobs.extend(jobs_in_mainbox)
                        current_set_mainboxes.append(main_box)
                
                if current_set_jobs:
                    deployment_sets.append({
                        'set_number': set_number,
                        'deployment_type': f'BOX Only ({len(current_set_mainboxes)} MainBoxes)',
                        'main_boxes': current_set_mainboxes,
                        'machines': [],
                        'new_machines': [],
                        'job_count': len(current_set_jobs),
                        'jobs': current_set_jobs
                    })
                    
                    for job in current_set_jobs:
                        deployed_jobs.add(job['job_name'])
                    set_number += 1
            break
        
        best_mainbox = min(machine_based_mainboxes, 
                          key=lambda mb: len(main_box_machine_dict[mb] - deployed_machines))
        
        required_machines = main_box_machine_dict[best_mainbox]
        new_machines_needed = required_machines - deployed_machines
        
        if len(new_machines_needed) == 0:
            continue
        
        selected_new_machine = list(new_machines_needed)[0]
        
        current_set_jobs = []
        current_set_mainboxes = []
        
        for main_box in undeployed_mainboxes:
            if canDeployMainBox(main_box, {selected_new_machine}):
                jobs_in_mainbox = getJobsInMainBox(main_box)
                
                if jobs_in_mainbox:
                    current_set_jobs.extend(jobs_in_mainbox)
                    current_set_mainboxes.append(main_box)
        
        if current_set_jobs:
            all_machines_in_set = set()
            for main_box in current_set_mainboxes:
                if main_box in main_box_machine_dict:
                    all_machines_in_set.update(main_box_machine_dict[main_box])
            
            deployment_sets.append({
                'set_number': set_number,
                'deployment_type': f'One New Machine ({len(current_set_mainboxes)} MainBoxes)',
                'main_boxes': current_set_mainboxes,
                'machines': list(all_machines_in_set),
                'new_machines': [selected_new_machine],
                'job_count': len(current_set_jobs),
                'jobs': current_set_jobs
            })
            
            for job in current_set_jobs:
                deployed_jobs.add(job['job_name'])
            deployed_machines.update(all_machines_in_set)
            set_number += 1
        else:
            break
    
    return deployment_sets


def analyzeDeploymentSets(deployment_sets):
    """Analyze and create summary of deployment sets"""
    summary_list = []
    detail_list = []
    
    for deploy_set in deployment_sets:
        new_machines = deploy_set.get('new_machines', [])
        
        # แยกประเภท jobs เป็น 3 กลุ่ม
        regular_jobs = []     # jobs ทั่วไป (อยู่ใน BOX)
        box_jobs = []         # BOX jobs
        standalone_jobs = []  # Standalone jobs (ไม่อยู่ใน BOX และไม่ใช่ BOX)
        
        # แยกประเภท MainBox
        real_mainboxes = []   # MainBoxes ที่เป็น box จริงๆ
        
        for job in deploy_set['jobs']:
            if job['job_type'] == 'BOX':
                box_jobs.append(job['job_name'])
            elif job['box_name'] is None or pd.isna(job['box_name']) or job['box_name'] == '':
                # Job ที่ไม่อยู่ใน BOX และไม่ใช่ BOX = Standalone Job
                standalone_jobs.append(job['job_name'])
            else:
                # Job ที่อยู่ใน BOX = Regular Job
                regular_jobs.append(job['job_name'])
        
        # แยกประเภท MainBox (เฉพาะ MainBox ที่เป็นจริง ไม่รวม Standalone)
        for main_box in deploy_set['main_boxes']:
            jobs_in_mainbox = [job for job in deploy_set['jobs'] if job['main_box'] == main_box]
            
            # ถ้าไม่ใช่ Standalone (job เดียวที่ main_box == job_name)
            if not (len(jobs_in_mainbox) == 1 and jobs_in_mainbox[0]['job_name'] == main_box):
                real_mainboxes.append(main_box)
        
        summary_list.append({
            'Set Number': deploy_set['set_number'],
            'Deployment Type': deploy_set['deployment_type'],
            'Real MainBoxes Count': len(real_mainboxes),
            'Standalone Jobs Count': len(standalone_jobs),
            'Regular Jobs Count': len(regular_jobs),
            'Box Jobs Count': len(box_jobs),
            'Total Machines Count': len(deploy_set['machines']),
            'New Machines Count': len(new_machines),
            'Total Jobs Count': deploy_set['job_count'],
            'Real MainBoxes': ', '.join(real_mainboxes) if real_mainboxes else 'None',
            'Standalone Jobs': ', '.join(standalone_jobs) if standalone_jobs else 'None',
            'Regular Jobs': ', '.join(regular_jobs) if regular_jobs else 'None',
            'Box Jobs': ', '.join(box_jobs) if box_jobs else 'None',
            'All Machines': ', '.join(deploy_set['machines']),
            'New Machines': ', '.join(new_machines) if new_machines else 'None'
        })
        
        for job in deploy_set['jobs']:
            # กำหนดประเภทของ Job
            if job['job_type'] == 'BOX':
                job_category = 'Box Job'
                main_box_type = 'Real MainBox'
            elif job['box_name'] is None or pd.isna(job['box_name']) or job['box_name'] == '':
                job_category = 'Standalone Job'
                main_box_type = 'Standalone'
            else:
                job_category = 'Regular Job'
                main_box_type = 'Real MainBox'
            
            detail_list.append({
                'Set Number': deploy_set['set_number'],
                'Deployment Type': deploy_set['deployment_type'],
                'Job Name': job['job_name'],
                'Job Type': job['job_type'],
                'Job Category': job_category,
                'Box Name': job['box_name'],
                'Main Box': job['main_box'],
                'Main Box Type': main_box_type,
                'Machine': job['machine'],
                'Owner': job['owner']
            })
    
    df_summary = pd.DataFrame(summary_list)
    df_detail = pd.DataFrame(detail_list)
    
    return df_summary, df_detail

def main():
    df_job = getDataExcel("input main ROOT job file")

    df_machine, df_main_box, df_result, df_log = findingmachineAndJob(df_job)
    
    # Create deployment sets
    deployment_sets = createDeploymentSets(df_job)
    df_deploy_summary, df_deploy_detail = analyzeDeploymentSets(deployment_sets)
    
    createExcel(OUTPUT_EXCEL_NAME, 
                (OUTPUT_MACHINE_SHEETNAME, df_machine), 
                (OUTPUT_MAIN_BOX_SHEETNAME, df_main_box), 
                (OUTPUT_RESULT_SHEETNAME, df_result), 
                (OUTPUT_SHEETNAME_LOG, df_log),
                ('Deployment Sets Summary', df_deploy_summary),
                ('Deployment Sets Detail', df_deploy_detail)
                )
    
    
if __name__ == '__main__':
    main()